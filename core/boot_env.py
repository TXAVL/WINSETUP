"""
TXA Dedicated Boot Environment — Môi trường khởi động riêng cho Tool (WinPE / RAMDisk)
Cho phép boot độc lập vào RAMDisk để format sạch ổ C: và cài đặt Windows tự động.
"""
import subprocess, os, shutil, re
from pathlib import Path
from typing import Optional, Callable

def _run_cmd(cmd: str, timeout: int = 60) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr).strip()
    except Exception as e:
        return -1, str(e)

def find_system_boot_sdi(iso_drive: str = "") -> Optional[str]:
    """Tìm file boot.sdi có sẵn trên hệ thống Windows hoặc trong ISO đã mount."""
    candidates = []
    # Ưu tiên tìm trong ISO đã mount (luôn có boot\boot.sdi trong Windows ISO)
    if iso_drive:
        candidates += [
            f"{iso_drive}:\\boot\\boot.sdi",
            f"{iso_drive}:\\Boot\\boot.sdi",
        ]
    candidates += [
        r"C:\Windows\Boot\DVD\EFI\boot.sdi",
        r"C:\Windows\Boot\DVD\PCAT\boot.sdi",
        r"C:\Windows\System32\Recovery\boot.sdi",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None

def find_boot_wim(iso_drive: str) -> Optional[str]:
    """Tìm boot.wim từ ISO đã mount hoặc từ Windows Recovery."""
    if iso_drive:
        p = f"{iso_drive}:\\sources\\boot.wim"
        if Path(p).exists():
            return p

    # Fallback kiểm tra WinRE
    re_candidates = [
        r"C:\Recovery\WindowsRE\Winre.wim",
        r"C:\Windows\System32\Recovery\Winre.wim",
    ]
    for r in re_candidates:
        if Path(r).exists():
            return r
    return None

def is_uefi() -> bool:
    """Kiểm tra hệ thống đang chạy UEFI hay Legacy BIOS."""
    try:
        import ctypes
        firmware_type = ctypes.c_uint()
        if ctypes.windll.kernel32.GetFirmwareType(ctypes.byref(firmware_type)):
            return firmware_type.value == 2
    except Exception:
        pass
    _, out = _run_cmd('bcdedit /enum {current}')
    return "winload.efi" in out.lower()

def _inject_app_into_wim(wim_path: Path, app_exe_path: str, log: Callable) -> bool:
    """Mount boot.wim (index 1), inject TXA exe + custom startnet.cmd, unmount+commit."""
    import tempfile as _tmpmod
    mount_dir = Path(_tmpmod.mkdtemp(prefix="txa_wim_mount_"))
    log("Đang mount WIM để tích hợp TXA vào môi trường WinPE...", 55.0)
    rc, out = _run_cmd(
        f'dism /Mount-Wim /WimFile:"{wim_path}" /index:1 /MountDir:"{mount_dir}"',
        timeout=300
    )
    if rc != 0:
        log(f"[WARN] Không mount được WIM: {out}")
        shutil.rmtree(str(mount_dir), ignore_errors=True)
        return False
    try:
        sys32 = mount_dir / "Windows" / "System32"
        txa_dest = sys32 / "TXAWinSetup.exe"
        shutil.copy2(app_exe_path, txa_dest)
        log("Đã nhúng TXAWinSetup.exe vào WinPE", 68.0)

        # Override startnet.cmd: chạy TXA thay vì Windows Setup
        startnet = sys32 / "startnet.cmd"
        startnet.write_text(
            "@echo off\r\n"
            "wpeinit\r\n"
            "X:\\Windows\\System32\\TXAWinSetup.exe\r\n",
            encoding="utf-8"
        )
        log("Đã cấu hình WinPE tự khởi chạy TXA thay vì Windows Setup", 72.0)

        rc2, out2 = _run_cmd(
            f'dism /Unmount-Wim /MountDir:"{mount_dir}" /Commit',
            timeout=300
        )
        if rc2 != 0:
            log(f"[WARN] Lỗi commit WIM: {out2}")
            return False
        log("✓ WIM đã được tùy chỉnh thành công", 75.0)
        return True
    except Exception as e:
        log(f"[WARN] Lỗi inject app vào WIM: {e}")
        _run_cmd(f'dism /Unmount-Wim /MountDir:"{mount_dir}" /Discard')
        return False
    finally:
        shutil.rmtree(str(mount_dir), ignore_errors=True)


def setup_txa_boot_environment(
    iso_drive: str,
    target_dir: str = r"C:\TXA_Boot",
    app_exe_path: str = "",
    progress_cb: Optional[Callable] = None,
) -> tuple[bool, str]:
    """
    Thiết lập môi trường khởi động riêng cho tool (RAMDisk WinPE).
    Khi khởi động lại, máy sẽ tự động boot vào môi trường này để cài đặt sạch.
    """
    def _log(msg: str, pct: float = -1.0):
        if progress_cb:
            progress_cb(pct, msg)
        print(f"[TXA BootEnv] {msg}")

    _log("Đang khởi tạo thư mục môi trường riêng cho tool...", 10.0)
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)

    # 1. Tìm và sao chép boot.wim
    _log("Đang tìm nạp file ảnh WinPE (boot.wim)...", 25.0)
    boot_wim_src = find_boot_wim(iso_drive)
    if not boot_wim_src:
        return False, "Không tìm thấy file boot.wim từ ISO hoặc WinRE của hệ thống!"

    dest_wim = target_path / "boot.wim"
    _log(f"Đang sao chép boot.wim vào môi trường riêng: {dest_wim}...", 40.0)
    try:
        if not dest_wim.exists() or dest_wim.stat().st_size != Path(boot_wim_src).stat().st_size:
            shutil.copy2(boot_wim_src, dest_wim)
    except Exception as e:
        return False, f"Không thể sao chép boot.wim: {e}"

    # 2. Inject TXA app + custom startnet.cmd vào boot.wim (DISM)
    # Nếu thất bại chỉ cảnh báo, không dừng — WinPE vẫn boot được (dù chạy setup.exe thay vì TXA)
    if app_exe_path and Path(app_exe_path).exists():
        _inject_app_into_wim(dest_wim, app_exe_path, _log)
    else:
        _log("[WARN] Không có đường dẫn TXA exe — bỏ qua bước inject app vào WinPE", 55.0)

    # 3. Tìm và sao chép boot.sdi (bắt buộc — nếu không có, ramdisk không mount được WIM)
    _log("Đang nạp file nạp khởi động RAMDisk (boot.sdi)...", 77.0)
    sdi_src = find_system_boot_sdi(iso_drive)
    dest_sdi = target_path / "boot.sdi"
    if not sdi_src:
        return False, (
            "Không tìm thấy file boot.sdi từ ISO hoặc hệ thống!\n"
            "Hãy đảm bảo file ISO Windows vẫn đang được mount trước khi cài đặt."
        )
    if not dest_sdi.exists() or dest_sdi.stat().st_size != Path(sdi_src).stat().st_size:
        try:
            shutil.copy2(sdi_src, dest_sdi)
        except Exception as e:
            return False, f"Không thể sao chép boot.sdi: {e}"

    # 3. Cấu hình BCD Entry để máy tự khởi động vào TXA Boot Environment
    _log("Đang cấu hình menu khởi động BCD cho môi trường TXA...", 75.0)

    # Tạo ramdiskoptions nếu chưa có
    _run_cmd('bcdedit /create {ramdiskoptions} /d "TXA WinSetup RAMDisk"')
    drive_letter = target_path.drive or "C:"
    rel_sdi = str(target_path).replace(drive_letter, "") + r"\boot.sdi"
    rel_wim = str(target_path).replace(drive_letter, "") + r"\boot.wim"

    _run_cmd(f'bcdedit /set {{ramdiskoptions}} ramdisksdidevice partition={drive_letter}')
    _run_cmd(f'bcdedit /set {{ramdiskoptions}} ramdisksdipath {rel_sdi}')

    # Tạo entry OSLoader mới
    code, out = _run_cmd('bcdedit /create /d "TXA WinSetup Environment (RAMDisk)" /application osloader')
    guid_match = re.search(r'\{[a-fA-F0-9\-]{36}\}', out)

    if guid_match:
        guid = guid_match.group(0)
        _log(f"Tạo entry BCD thành công: {guid}", 85.0)

        loader_file = "\\Windows\\system32\\winload.efi" if is_uefi() else "\\Windows\\system32\\winload.exe"
        _run_cmd(f'bcdedit /set {guid} device ramdisk=[{drive_letter}]{rel_wim},{{ramdiskoptions}}')
        _run_cmd(f'bcdedit /set {guid} osdevice ramdisk=[{drive_letter}]{rel_wim},{{ramdiskoptions}}')
        _run_cmd(f'bcdedit /set {guid} path {loader_file}')
        _run_cmd(f'bcdedit /set {guid} systemroot \\Windows')
        _run_cmd(f'bcdedit /set {guid} winpe yes')
        _run_cmd(f'bcdedit /set {guid} detecthal yes')

        # Thiết lập tự boot vào entry này trong lần khởi động lại tiếp theo
        _run_cmd(f'bcdedit /bootsequence {guid}')
        _log("✓ Đã thiết lập tự động boot vào môi trường TXA WinSetup khi khởi động lại!", 100.0)
        return True, guid
    else:
        # Nếu đã có sẵn hoặc WinRE được kích hoạt
        _log("Sử dụng cơ chế WinRE / Recovery Sequence...", 95.0)
        _run_cmd("reagentc /boottore")
        _log("✓ Đã thiết lập môi trường khởi động tự động!", 100.0)
        return True, "WINRE"
