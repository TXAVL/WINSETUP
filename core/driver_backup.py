"""
Backup / restore driver Windows
"""
import subprocess, os
from pathlib import Path
from typing import Optional, Callable

def _run(cmd: str, timeout: int = 300) -> tuple[int, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()

def backup_drivers(
    output_dir: str,
    progress: Optional[Callable] = None,
) -> tuple[bool, str]:
    """
    Export tất cả driver đang cài trên Windows hiện tại.
    output_dir: thư mục lưu (nên ở ổ DATA hoặc USB, không phải C:)
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if progress:
        progress(-1, f"Đang backup driver vào {output_dir}...")

    code, out = _run(
        f'dism /Online /Export-Driver /Destination:"{output_dir}"',
        timeout=300
    )

    if code == 0:
        # Đếm số driver đã backup
        count = sum(1 for f in Path(output_dir).rglob("*.inf"))
        msg = f"Đã backup {count} driver"
        if progress:
            progress(100, msg)
        return True, msg

    return False, f"Lỗi backup driver: {out}"

def restore_drivers(
    driver_dir: str,
    progress: Optional[Callable] = None,
) -> tuple[bool, str]:
    """Cài lại driver từ backup vào Windows hiện tại (Phase 3)."""
    if not Path(driver_dir).exists():
        return False, "Không tìm thấy thư mục driver"

    if progress:
        progress(-1, f"Đang cài driver từ {driver_dir}...")

    code, out = _run(
        f'dism /Online /Add-Driver /Driver:"{driver_dir}" /Recurse /ForceUnsigned',
        timeout=600
    )

    if code == 0:
        if progress:
            progress(100, "Cài driver hoàn tất")
        return True, "OK"

    # Partial success vẫn chấp nhận
    if "successfully" in out.lower():
        return True, "OK (một số driver lỗi nhưng bỏ qua)"

    return False, out[:200]

def get_backup_default_path() -> str:
    """Tự tìm ổ phù hợp để lưu driver backup (không phải C:)."""
    for drive in "DEFGHIJKLMNOPQRSTUVWXYZ":
        p = Path(f"{drive}:\\")
        try:
            usage = os.statvfs(str(p)) if hasattr(os, 'statvfs') else None
            # Windows: dùng ctypes
            import ctypes
            free = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                str(p), None, None, ctypes.byref(free)
            )
            if free.value > 500 * 1024 * 1024:  # >500MB trống
                return str(p / "TXA_DriverBackup")
        except Exception:
            continue
    return "C:\\TXA_DriverBackup"
