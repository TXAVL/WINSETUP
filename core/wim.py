"""
WIM / ISO operations: mount ISO, đọc edition list, apply image, track progress
"""
import subprocess, os, re, struct, json, atexit
from pathlib import Path
from typing import List, Optional, Callable
from dataclasses import dataclass

@dataclass
class WimImage:
    index: int
    name: str
    description: str
    size_gb: float
    architecture: str = "x64"

def _run(cmd: str, timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=timeout)
        return r.stdout + r.stderr
    except Exception as e:
        return str(e)

# ── ISO mount/unmount ───────────────────────────────────────────────

_MOUNTED_ISOS = set()

def mount_iso(iso_path: str) -> Optional[str]:
    """Mount ISO, trả về drive letter (vd: 'F') hoặc None."""
    already = get_mounted_drive(iso_path)
    if already:
        _MOUNTED_ISOS.add(str(Path(iso_path).resolve()))
        return already

    out = _run(
        f'powershell -NoProfile -Command "'
        f'try {{ $m = Get-DiskImage -ImagePath \'{iso_path}\'; if (-not $m.Attached) {{ $m = Mount-DiskImage -ImagePath \'{iso_path}\' -PassThru }}; ($m | Get-Volume).DriveLetter }} catch {{ }}"'
    )
    letter = out.strip().split()[-1] if out.strip() else ""
    if len(letter) == 1:
        _MOUNTED_ISOS.add(str(Path(iso_path).resolve()))
        return letter
    return None

def unmount_iso(iso_path: str):
    """Eject / Dismount ổ ảo ISO."""
    clean_path = str(Path(iso_path).resolve())
    _MOUNTED_ISOS.discard(clean_path)
    _run(f'powershell -NoProfile -Command "Dismount-DiskImage -ImagePath \'{iso_path}\' -ErrorAction SilentlyContinue"')

def unmount_all_iso():
    """Tự động unmount toàn bộ các ổ đĩa ảo ISO đã mount trước khi thoát ứng dụng."""
    for iso in list(_MOUNTED_ISOS):
        try:
            _run(f'powershell -NoProfile -Command "Dismount-DiskImage -ImagePath \'{iso}\' -ErrorAction SilentlyContinue"')
        except Exception:
            pass
    _MOUNTED_ISOS.clear()

atexit.register(unmount_all_iso)

def get_mounted_drive(iso_path: str) -> Optional[str]:
    """Kiểm tra ISO đã được mount chưa, trả về drive letter."""
    out = _run(
        f'powershell -NoProfile -Command "'
        f'$m = Get-DiskImage -ImagePath \'{iso_path}\'; '
        f'if ($m.Attached) {{ ($m | Get-Volume).DriveLetter }} else {{ \'\' }}"'
    )
    letter = out.strip().split()[-1] if out.strip() else ""
    return letter if len(letter) == 1 else None

# ── WIM metadata: Binary Parser kết hợp DISM Fallback ──────────────

def _read_images_via_dism(wim_path: str) -> List[WimImage]:
    """Sử dụng DISM của Windows để đọc danh sách phiên bản (hỗ trợ 100% WIM, ESD, SWM, Insider Preview)."""
    images = []
    try:
        out = _run(f'dism.exe /English /Get-WimInfo /WimFile:"{wim_path}"', timeout=30)
        if not out or "Index :" not in out:
            out = _run(f'dism.exe /English /Get-ImageInfo /ImageFile:"{wim_path}"', timeout=30)

        blocks = re.split(r"(?:^|\r?\n)(?=Index\s*:)", out)
        for b in blocks:
            m_idx = re.search(r"Index\s*:\s*(\d+)", b)
            if not m_idx:
                continue
            idx = int(m_idx.group(1))

            m_name = re.search(r"Name\s*:\s*(.+)", b)
            name = m_name.group(1).strip() if m_name else f"Windows Image {idx}"

            m_desc = re.search(r"Description\s*:\s*(.+)", b)
            desc = m_desc.group(1).strip() if m_desc else ""

            m_size = re.search(r"Size\s*:\s*([\d,\.]+)\s*bytes", b)
            size_gb = 0.0
            if m_size:
                raw_bytes = int(m_size.group(1).replace(",", "").replace(".", ""))
                size_gb = round(raw_bytes / (1024**3), 1)

            images.append(WimImage(
                index=idx,
                name=name,
                description=desc,
                size_gb=size_gb,
                architecture="x64"
            ))
    except Exception as e:
        print(f"[dism] read error: {e}")
    return images

def read_wim_images(wim_path: str) -> List[WimImage]:
    """
    Đọc danh sách toàn bộ các phiên bản Windows (Editions) trong file WIM / ESD / SWM.
    Kết hợp parser nhị phân siêu tốc và DISM fallback đảm bảo đọc được mọi bản Windows kể cả Insider Preview.
    """
    images = []
    # 1. Thử đọc nhanh trực tiếp qua header nhị phân nếu là file WIM uncompressed
    try:
        with open(wim_path, "rb") as f:
            header = f.read(208)
            if header[:8] == b"MSWIM\x00\x00\x00":
                xml_size_raw = struct.unpack_from("<Q", header, 72)[0]
                xml_size = xml_size_raw & 0x00FFFFFFFFFFFFFF
                xml_offset = struct.unpack_from("<Q", header, 80)[0]

                f.seek(xml_offset)
                xml_bytes = f.read(int(xml_size))
                xml_str = xml_bytes.decode("utf-16-le", errors="replace").lstrip("\ufeff")
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_str)

                for img in root.findall("IMAGE"):
                    idx = int(img.get("INDEX", 0))
                    name = (img.findtext("NAME") or f"Image {idx}").strip()
                    desc = (img.findtext("DESCRIPTION") or "").strip()
                    total_bytes = int(img.findtext("TOTALBYTES") or 0)
                    size_gb = round(total_bytes / (1024**3), 1)

                    arch_node = img.find(".//ARCH")
                    arch = "x64" if arch_node is None else (
                        "x64" if arch_node.text in ("9", "x64") else "x86"
                    )

                    images.append(WimImage(
                        index=idx, name=name, description=desc,
                        size_gb=size_gb, architecture=arch
                    ))
    except Exception:
        pass

    # 2. Nếu đọc binary không có kết quả (đặc trưng của file install.esd nén LZMS hoặc WIM đặc biệt)
    # Tự động chuyển sang gọi DISM của Windows
    if not images:
        images = _read_images_via_dism(wim_path)

    return images

def get_wim_path_from_drive(drive_letter: str) -> Optional[str]:
    """Tìm install.wim, install.esd hoặc install.swm trong sources folder của ổ đĩa."""
    sources = Path(f"{drive_letter}:\\sources")
    if sources.exists() and sources.is_dir():
        for name in ("install.wim", "install.esd", "install.swm"):
            p = sources / name
            if p.exists():
                return str(p)
        for f in sources.iterdir():
            if f.is_file() and f.suffix.lower() in (".wim", ".esd", ".swm") and "boot" not in f.name.lower():
                return str(f)
    return None

# ── Apply image ─────────────────────────────────────────────────────

def apply_image(
    wim_path: str,
    image_index: int,
    target_drive: str,
    progress_cb: Optional[Callable[[int, str], None]] = None,
) -> tuple[bool, str]:
    """
    Apply WIM vào target_drive (vd: "C").
    progress_cb(percent, message) được gọi liên tục.
    Trả về (success, message).
    """
    target = f"{target_drive}:\\"
    cmd = (
        f'dism /Apply-Image /ImageFile:"{wim_path}" '
        f'/Index:{image_index} /ApplyDir:{target} /Verify'
    )

    process = subprocess.Popen(
        cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace"
    )

    import time
    start_time = time.time()
    percent = 0.0
    eta_str = "--:--"

    def _notify(pct: float, msg: str, eta: str = ""):
        if progress_cb:
            try:
                progress_cb(pct, msg, eta)
            except TypeError:
                progress_cb(pct, msg)

    for line in process.stdout:
        line = line.strip()
        # DISM output: [==========  30.0%  ] hoặc [===== 12.35% =====]
        m = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
        if m:
            try:
                percent = float(m.group(1))
            except ValueError:
                pass

            now = time.time()
            elapsed = now - start_time
            if elapsed > 1.5 and percent > 0.5:
                speed = percent / elapsed  # % hoàn thành mỗi giây
                if speed > 0:
                    remaining_pct = max(0.0, 100.0 - percent)
                    eta_seconds = int(remaining_pct / speed)
                    mins, secs = divmod(eta_seconds, 60)
                    if mins >= 60:
                        hrs, mins = divmod(mins, 60)
                        eta_str = f"{hrs:02d}h {mins:02d}m"
                    else:
                        eta_str = f"{mins:02d}m {secs:02d}s"

            msg = f"Đang bung file ảnh Windows... {percent:05.2f}%"
            _notify(percent, msg, eta_str)
        elif line:
            _notify(percent, line[:80], eta_str)

    process.wait()
    if process.returncode == 0:
        _notify(100.0, "Bung file ảnh Windows hoàn tất!", "00m 00s")
        return True, "OK"
    return False, f"DISM exit code: {process.returncode}"

# ── Bootloader ──────────────────────────────────────────────────────

def install_bootloader(windows_drive: str, efi_drive: str) -> tuple[bool, str]:
    """
    Cài EFI bootloader.
    windows_drive: ổ chứa Windows (vd: "C")
    efi_drive: ổ EFI (vd: "S")
    """
    out = _run(
        f'bcdboot {windows_drive}:\\Windows /s {efi_drive}: /f UEFI',
        timeout=30
    )
    if "successfully" in out.lower() or out.strip() == "":
        return True, "OK"
    # Thử thêm /l en-us
    out2 = _run(
        f'bcdboot {windows_drive}:\\Windows /s {efi_drive}: /f ALL /l en-us',
        timeout=30
    )
    return ("successfully" in out2.lower() or not out2.strip()), out2

def install_bootloader_mbr(windows_drive: str) -> tuple[bool, str]:
    """Cài MBR bootloader cho máy Legacy BIOS."""
    out = _run(
        f'bcdboot {windows_drive}:\\Windows /f BIOS',
        timeout=30
    )
    return True, out
