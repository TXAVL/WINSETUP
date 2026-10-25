"""
Disk & partition detection — tự load toàn bộ thông tin ổ đĩa
"""
import subprocess, re, json
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Partition:
    index: int
    letter: str          # "C", "D", ... hoặc "" nếu chưa gán
    label: str
    size_gb: float
    free_gb: float
    fs: str              # NTFS, FAT32, ...
    type: str            # Primary, EFI, MSR, Recovery
    is_system: bool      # Partition đang chứa Windows boot
    is_active: bool
    bitlocker_status: str  # "Off" | "On" | "Locked" | "Unknown"
    raw_size_mb: int

@dataclass
class Disk:
    index: int
    model: str
    size_gb: float
    size_mb: int
    interface: str       # SSD / HDD / NVMe / USB
    partitions: List[Partition] = field(default_factory=list)
    is_gpt: bool = True
    is_system_disk: bool = False  # Đang chứa Windows đang chạy

def is_winpe() -> bool:
    """Tự động nhận diện môi trường Windows PE / WinRE."""
    import os
    # 1. Ổ hệ thống là X: (đặc trưng tuyệt đối của RAMDisk WinPE)
    if os.environ.get("SystemDrive", "").upper() == "X:":
        return True
    # 2. Key MiniNT trong registry (chỉ tồn tại trên WinPE)
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\MiniNT"):
            return True
    except Exception:
        pass
    # 3. File wpeutil.exe hoặc thư mục System32 của WinPE
    if os.path.exists(r"X:\Windows\System32\wpeutil.exe"):
        return True
    return False

def _run(cmd: str) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=30)
        return r.stdout
    except Exception:
        return ""

def _diskpart_script(lines: list) -> str:
    script = "\n".join(lines)
    import tempfile, os
    tf = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    tf.write(script + "\n")
    tf.close()
    out = _run(f'diskpart /s "{tf.name}"')
    os.unlink(tf.name)
    return out

def _get_bitlocker_status(letter: str) -> str:
    if not letter:
        return "Unknown"
    out = _run(f'manage-bde -status {letter}: 2>nul')
    if not out:
        return "Unknown"
    if "Fully Decrypted" in out or "Percentage Encrypted: 0" in out:
        return "Off"
    if "Locked" in out:
        return "Locked"
    if "Fully Encrypted" in out or "Percentage Encrypted: 100" in out:
        return "On"
    return "Unknown"

def _detect_interface(model: str, bus_type: str = "") -> str:
    m_lower = (model or "").lower()
    b_lower = str(bus_type or "").lower()
    if any(x in m_lower for x in ["nvme", "nvm"]) or "nvme" in b_lower:
        return "NVMe"
    if "usb" in m_lower or "usb" in b_lower:
        return "USB"
    if "ssd" in m_lower or "flash" in m_lower:
        return "SSD"
    if "hdd" in m_lower:
        return "HDD"
    return "SSD/HDD"

def _get_disks_via_powershell() -> List[Disk]:
    """Cách 1: Lấy thông tin ổ đĩa qua PowerShell Storage Module trong 1 lệnh duy nhất siêu tốc."""
    try:
        combined_ps = (
            "$ErrorActionPreference = 'SilentlyContinue'; "
            "$d = @(Get-Disk | Select-Object Number,FriendlyName,Size,PartitionStyle,BusType); "
            "$v = @(Get-Volume | Where-Object DriveLetter | Select-Object DriveLetter,FileSystemLabel,FileSystem,Size,SizeRemaining); "
            "$p = @(Get-Partition | Select-Object DiskNumber,PartitionNumber,DriveLetter,Size,IsActive,Type,IsBoot,IsSystem); "
            "@{Disks=$d; Volumes=$v; Partitions=$p} | ConvertTo-Json -Depth 3 -Compress"
        )
        raw = _run(f'powershell -NoProfile -NonInteractive -Command "{combined_ps}"')
        if not raw.strip():
            return []
        data = json.loads(raw)
        disk_list = data.get("Disks") or []
        if isinstance(disk_list, dict):
            disk_list = [disk_list]
        vol_list = data.get("Volumes") or []
        if isinstance(vol_list, dict):
            vol_list = [vol_list]
        vol_map = {v["DriveLetter"]: v for v in vol_list if v.get("DriveLetter")}

        part_list = data.get("Partitions") or []
        if isinstance(part_list, dict):
            part_list = [part_list]

        system_disk_num = None
        if not is_winpe():
            for p in part_list:
                if (p.get("IsBoot") or p.get("IsSystem")) and p.get("DriveLetter") == "C":
                    system_disk_num = p.get("DiskNumber")

        disks = []
        for d in disk_list:
            idx = d.get("Number", 0)
            size_bytes = d.get("Size", 0) or 0
            size_gb = round(size_bytes / (1024**3), 1)
            size_mb = size_bytes // (1024**2)
            model = d.get("FriendlyName", f"Disk {idx}") or f"Disk {idx}"
            is_gpt = (d.get("PartitionStyle", "GPT") == "GPT")
            bus_type = d.get("BusType", "")

            disk = Disk(
                index=idx,
                model=model,
                size_gb=size_gb,
                size_mb=size_mb,
                interface=_detect_interface(model, bus_type),
                is_gpt=is_gpt,
                is_system_disk=(idx == system_disk_num),
            )

            for p in part_list:
                if p.get("DiskNumber") != idx:
                    continue
                letter = p.get("DriveLetter") or ""
                if isinstance(letter, int):
                    letter = ""
                p_size_bytes = p.get("Size", 0) or 0
                p_size_mb = p_size_bytes // (1024**2)
                p_size_gb = round(p_size_bytes / (1024**3), 2)
                p_type = p.get("Type", "Primary") or "Primary"

                vol = vol_map.get(letter, {})
                label = vol.get("FileSystemLabel", "") or ""
                fs = vol.get("FileSystem", "") or ""
                free_bytes = vol.get("SizeRemaining", 0) or 0
                free_gb = round(free_bytes / (1024**3), 2)

                part = Partition(
                    index=p.get("PartitionNumber", 0),
                    letter=letter,
                    label=label,
                    size_gb=p_size_gb,
                    free_gb=free_gb,
                    fs=fs,
                    type=p_type,
                    is_system=bool(p.get("IsSystem")),
                    is_active=bool(p.get("IsActive")),
                    bitlocker_status="Unknown",
                    raw_size_mb=p_size_mb,
                )
                disk.partitions.append(part)

            disk.partitions.sort(key=lambda x: x.index)
            disks.append(disk)
        return disks
    except Exception:
        return []

def _get_disks_via_cim() -> List[Disk]:
    """Cách 2: Fallback CIM / WMI tiêu chuẩn (hoạt động kể cả không có Admin & không có Storage module)."""
    try:
        ps_disks = (
            "Get-CimInstance Win32_DiskDrive | "
            "Select-Object Index, Model, Size, MediaType, InterfaceType | "
            "ConvertTo-Json -Compress"
        )
        raw_disks = _run(f'powershell -NoProfile -Command "{ps_disks}"')
        if not raw_disks.strip():
            return []
        d_items = json.loads(raw_disks)
        if isinstance(d_items, dict):
            d_items = [d_items]

        ps_vols = (
            "Get-CimInstance Win32_LogicalDisk | "
            "Select-Object DeviceID, VolumeName, FileSystem, Size, FreeSpace | "
            "ConvertTo-Json -Compress"
        )
        raw_vols = _run(f'powershell -NoProfile -Command "{ps_vols}"')
        v_items = json.loads(raw_vols) if raw_vols.strip() else []
        if isinstance(v_items, dict):
            v_items = [v_items]
        v_map = {item.get("DeviceID", "").replace(":", "").upper(): item for item in v_items if item.get("DeviceID")}

        disks = []
        for d in d_items:
            idx = int(d.get("Index", 0))
            model = d.get("Model", f"Disk {idx}") or f"Disk {idx}"
            size_bytes = int(d.get("Size") or 0)
            size_gb = round(size_bytes / (1024**3), 1)
            size_mb = size_bytes // (1024**2)

            interface = "SSD"
            m_lower = model.lower()
            if any(x in m_lower for x in ["nvme", "nvm"]):
                interface = "NVMe"
            elif "usb" in m_lower:
                interface = "USB"

            disk = Disk(
                index=idx,
                model=model,
                size_gb=size_gb,
                size_mb=size_mb,
                interface=interface,
                is_gpt=True,
                is_system_disk=(not is_winpe() and idx == 0),
            )

            # Ghép volume nếu có letter
            for ltr, v in v_map.items():
                if not ltr or ltr in ("A", "B"):
                    continue
                v_size = int(v.get("Size") or 0)
                v_free = int(v.get("FreeSpace") or 0)
                part = Partition(
                    index=len(disk.partitions) + 1,
                    letter=ltr,
                    label=v.get("VolumeName") or "",
                    size_gb=round(v_size / (1024**3), 2),
                    free_gb=round(v_free / (1024**3), 2),
                    fs=v.get("FileSystem") or "NTFS",
                    type="Primary",
                    is_system=(ltr == "C"),
                    is_active=False,
                    bitlocker_status="Unknown",
                    raw_size_mb=v_size // (1024**2),
                )
                disk.partitions.append(part)

            disks.append(disk)
        return disks
    except Exception:
        return []

def _get_disks_via_diskpart() -> List[Disk]:
    """Cách 3: Fallback qua Diskpart (Dành riêng cho WinPE rút gọn không có PowerShell)."""
    try:
        out = _diskpart_script(["list disk", "list volume"])
        if not out.strip():
            return []

        disks: List[Disk] = []
        # Parse list disk
        for line in out.splitlines():
            line_s = line.strip()
            # Mẫu: Disk 0    Online          476 GB      0 B        *
            m = re.match(r'Disk\s+(\d+)\s+(\w+)\s+(\d+(?:\.\d+)?)\s+([KMGTP]?B)(?:\s+\d+(?:\.\d+)?\s+[KMGTP]?B)?(?:\s+Dyn)?(?:\s+(\*))?', line_s, re.I)
            if m:
                idx = int(m.group(1))
                val = float(m.group(3))
                unit = m.group(4).upper()
                if unit == "TB":
                    size_gb = val * 1024
                elif unit == "MB":
                    size_gb = val / 1024
                else:
                    size_gb = val
                size_mb = int(size_gb * 1024)
                is_gpt = (m.group(5) == "*")

                # Lấy detail disk để tìm model
                detail_out = _diskpart_script([f"select disk {idx}", "detail disk"])
                model = f"Disk {idx}"
                if detail_out.strip():
                    first_line = detail_out.strip().splitlines()[0]
                    if "diskpart" not in first_line.lower():
                        model = first_line[:40]

                interface = "NVMe" if "nvme" in model.lower() else ("USB" if "usb" in model.lower() else "SSD/HDD")

                disk = Disk(
                    index=idx,
                    model=model,
                    size_gb=round(size_gb, 1),
                    size_mb=size_mb,
                    interface=interface,
                    is_gpt=is_gpt,
                    is_system_disk=False,
                )
                disks.append(disk)

        # Parse list volume
        vol_pattern = re.compile(
            r'Volume\s+(\d+)\s+([A-Z])?\s+(.*?)\s+(NTFS|FAT32|exFAT|ReFS|RAW)\s+(Partition|Simple)\s+(\d+(?:\.\d+)?\s+[KMGTP]?B)\s+(\w+)\s*(.*)',
            re.I
        )
        for line in out.splitlines():
            vm = vol_pattern.search(line)
            if vm and disks:
                ltr = vm.group(2) or ""
                label = (vm.group(3) or "").strip()
                fs = vm.group(4) or ""
                size_str = vm.group(6) or ""
                info = (vm.group(8) or "").strip().lower()

                parts = size_str.split()
                val = float(parts[0]) if parts else 0.0
                unit = parts[1].upper() if len(parts) > 1 else "GB"
                if unit == "MB":
                    v_gb = val / 1024
                elif unit == "TB":
                    v_gb = val * 1024
                else:
                    v_gb = val

                part = Partition(
                    index=int(vm.group(1)),
                    letter=ltr,
                    label=label,
                    size_gb=round(v_gb, 2),
                    free_gb=0.0,
                    fs=fs,
                    type="EFI" if "system" in info else "Primary",
                    is_system=("system" in info or "boot" in info),
                    is_active=False,
                    bitlocker_status="Unknown",
                    raw_size_mb=int(v_gb * 1024),
                )
                disks[0].partitions.append(part)

        return disks
    except Exception:
        return []

_disk_cache: List[Disk] = []
_disk_cache_time: float = 0.0

def get_all_disks(force_refresh: bool = False) -> List[Disk]:
    """
    Load toàn bộ disk + partition info với 3 lớp bảo vệ tự động:
    1. PowerShell Storage Module (tối ưu 1 lệnh siêu tốc)
    2. WMI CIM Instance (nhanh, nhẹ, không cần Storage module)
    3. Diskpart parser (chạy trực tiếp trên WinPE không có PowerShell)
    """
    global _disk_cache, _disk_cache_time
    import time
    now = time.time()
    if not force_refresh and _disk_cache and (now - _disk_cache_time < 5.0):
        return _disk_cache

    # Lớp 1: PowerShell chuẩn
    disks = _get_disks_via_powershell()
    if not disks:
        # Lớp 2: WMI / CIM
        disks = _get_disks_via_cim()
    if not disks:
        # Lớp 3: Diskpart (cứu cánh cho WinPE)
        disks = _get_disks_via_diskpart()

    if disks:
        disks.sort(key=lambda x: x.index)
        _disk_cache = disks
        _disk_cache_time = now
        return disks
    return []

def suggest_partition_layout(disk: Disk, c_size_gb: Optional[int] = None) -> dict:
    """
    Tự đề xuất layout phân vùng dựa trên kích thước ổ.
    Trả về dict: efi_mb, msr_mb, c_gb, data_gb
    """
    total_mb = disk.size_mb
    efi_mb = 100
    msr_mb = 16
    overhead_mb = efi_mb + msr_mb + 512  # 512MB recovery partition

    usable_mb = total_mb - overhead_mb
    usable_gb = usable_mb / 1024

    if c_size_gb is None:
        # Tự đề xuất C: dựa trên tổng dung lượng
        if usable_gb <= 120:
            c_gb = int(usable_gb * 0.6)
        elif usable_gb <= 256:
            c_gb = 80
        elif usable_gb <= 512:
            c_gb = 120
        else:
            c_gb = 150
        c_gb = max(c_gb, 50)  # Tối thiểu 50GB cho C:
    else:
        c_gb = c_size_gb

    data_gb = int(usable_gb - c_gb)
    if data_gb < 0:
        data_gb = 0

    return {
        "efi_mb": efi_mb,
        "msr_mb": msr_mb,
        "c_gb": c_gb,
        "data_gb": data_gb,
        "total_gb": round(usable_gb, 1),
    }

def unlock_bitlocker(letter: str, recovery_key: str) -> tuple[bool, str]:
    """Mở khóa BitLocker bằng recovery key."""
    out = _run(f'manage-bde -unlock {letter}: -RecoveryKey "{recovery_key}" 2>&1')
    if "successfully" in out.lower():
        return True, "Mở khóa thành công"
    return False, out.strip()

def format_disk_info(disk: Disk) -> str:
    """Tóm tắt thông tin disk để hiển thị UI."""
    tag = " [HỆ THỐNG]" if disk.is_system_disk else ""
    return f"Disk {disk.index}: {disk.model} — {disk.size_gb} GB ({disk.interface}){tag}"

def get_recommended_disk(disks: List[Disk]) -> Optional[Disk]:
    """Tự chọn ổ đĩa phù hợp nhất để cài (ổ lớn nhất không phải system)."""
    candidates = [d for d in disks if not d.is_system_disk and d.size_gb >= 50]
    if not candidates:
        # Nếu chỉ có 1 ổ thì dùng ổ đó (sẽ cài đè)
        candidates = [d for d in disks if d.size_gb >= 50]
    if not candidates:
        return None
    return max(candidates, key=lambda d: d.size_gb)

def find_efi_partition(disk: Disk) -> Optional[Partition]:
    """Tìm phân vùng EFI System Partition (ESP) trên ổ đĩa."""
    for p in disk.partitions:
        if p.type.upper() in ("EFI", "SYSTEM") or "EFI" in p.label.upper() or (p.fs.upper() == "FAT32" and p.size_gb < 1.0):
            return p
    return None

def find_target_partition(disk: Disk) -> Optional[Partition]:
    """Tìm phân vùng phù hợp nhất để cài đặt Windows (thường là C: hoặc phân vùng NTFS lớn nhất)."""
    for p in disk.partitions:
        if p.letter.upper() == "C":
            return p
    ntfs_parts = [p for p in disk.partitions if p.fs.upper() == "NTFS" and p.size_gb >= 25]
    if ntfs_parts:
        return max(ntfs_parts, key=lambda p: p.size_gb)
    return None

