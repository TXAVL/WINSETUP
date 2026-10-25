"""
Orchestrator cài đặt: diskpart, apply WIM, bootloader, unattend, recovery setup
"""
import subprocess, os, sys, tempfile, shutil, time
from pathlib import Path
from typing import Callable, Optional
from .state import InstallState, Step
from .disk import Disk, suggest_partition_layout
from .wim import apply_image, install_bootloader, install_bootloader_mbr
from .unattend import generate as gen_unattend

def _run(cmd: str, timeout: int = 60) -> tuple[int, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr).strip()

def _diskpart(lines: list, timeout: int = 120) -> str:
    script = "\n".join(lines)
    tf = tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt', delete=False, encoding='utf-8'
    )
    tf.write(script + "\n")
    tf.close()
    _, out = _run(f'diskpart /s "{tf.name}"', timeout=timeout)
    os.unlink(tf.name)
    return out

def log_cb(cb: Optional[Callable], msg: str, pct: float = -1.0, eta: str = ""):
    if pct >= 0:
        pct_fmt = f"{pct:05.2f}%"
        eta_part = f" (ETA: {eta})" if eta and eta != "--:--" else ""
        print(f"[{pct_fmt}]{eta_part} {msg}")
    else:
        print(msg)
    if cb:
        try:
            cb(pct, msg, eta)
        except TypeError:
            try:
                cb(pct, msg)
            except Exception:
                pass

# ── Bước 1: Phân vùng ổ đĩa ────────────────────────────────────────

def partition_disk(
    state: InstallState,
    disk: Disk,
    c_gb: int,
    data_gb: int,
    progress: Optional[Callable] = None,
) -> tuple[bool, str, dict]:
    """
    Xóa và tạo lại toàn bộ partition trên disk.
    Trả về (ok, msg, drive_map) trong đó drive_map = {efi, windows, data}
    """
    log_cb(progress, f"Đang phân vùng Disk {disk.index}...", 5)

    if disk.is_gpt:
        script = [
            f"select disk {disk.index}",
            "clean",
            "convert gpt",
            # EFI System Partition
            "create partition efi size=100",
            "format fs=fat32 quick label=EFI",
            "assign letter=S",
            # MSR
            "create partition msr size=16",
            # Windows C:
            f"create partition primary size={c_gb * 1024}",
            "format fs=ntfs quick label=Windows",
            "assign letter=W",
        ]
        if data_gb > 0:
            script += [
                "create partition primary",
                "format fs=ntfs quick label=Data",
                "assign letter=D",
            ]
    else:
        # MBR legacy
        script = [
            f"select disk {disk.index}",
            "clean",
            "convert mbr",
            "create partition primary size=500",
            "format fs=ntfs quick label=System",
            "active",
            "assign letter=S",
            f"create partition primary size={c_gb * 1024}",
            "format fs=ntfs quick label=Windows",
            "assign letter=W",
        ]
        if data_gb > 0:
            script += [
                "create partition primary",
                "format fs=ntfs quick label=Data",
                "assign letter=D",
            ]

    out = _diskpart(script, timeout=180)
    log_cb(progress, "Phân vùng hoàn tất", 20)

    drive_map = {
        "efi": "S",
        "windows": "W",
        "data": "D" if data_gb > 0 else "",
    }

    state.advance(Step.DISK_PARTITIONED, drive_map=drive_map)
    return True, "OK", drive_map

# ── Bước 2: Apply WIM ───────────────────────────────────────────────

def apply_windows(
    state: InstallState,
    wim_path: str,
    image_index: int,
    windows_drive: str,
    progress: Optional[Callable] = None,
) -> tuple[bool, str]:
    log_cb(progress, "Đang bung file ảnh Windows (DISM)...", 22.0)

    def _prog(pct, msg, eta=""):
        # Map 0%..100% của DISM sang dải 22.00%..85.00% của toàn bộ quy trình
        mapped = 22.0 + (float(pct) * 0.63)
        log_cb(progress, msg, mapped, eta)

    ok, msg = apply_image(wim_path, image_index, windows_drive, _prog)
    if not ok:
        return False, msg

    state.advance(Step.WIM_APPLIED)
    return True, "OK"

def format_and_prepare_existing_partition(
    state: InstallState,
    disk: Disk,
    target_letter: str,
    quick_format: bool = True,
    progress: Optional[Callable] = None,
) -> tuple[bool, str, dict]:
    """
    Chuẩn bị cài đặt vào phân vùng có sẵn (Không xóa các phân vùng khác trên ổ).
    Trả về (ok, msg, drive_map = {efi, windows, data})
    """
    log_cb(progress, f"Đang chuẩn bị phân vùng cài đặt ({target_letter}:)...", 5.0)

    # 1. Format phân vùng target nếu quick_format
    if quick_format and target_letter:
        log_cb(progress, f"Đang format nhanh phân vùng {target_letter}: sang NTFS...", 8.0)
        code, out = _run(f'format {target_letter}: /FS:NTFS /Q /Y /V:Windows', timeout=60)
        if code != 0:
            _diskpart([f"select volume {target_letter}", "format fs=ntfs quick label=Windows"])

    # 2. Tìm hoặc gán letter cho phân vùng EFI (nếu disk GPT)
    efi_letter = ""
    if disk.is_gpt:
        for p in disk.partitions:
            if p.type.upper() in ("EFI", "SYSTEM") or "EFI" in p.label.upper() or (p.fs.upper() == "FAT32" and p.size_gb < 1.0):
                if p.letter:
                    efi_letter = p.letter
                    break
        if not efi_letter:
            log_cb(progress, "Đang ánh xạ phân vùng EFI System Partition (ESP)...", 12.0)
            _diskpart([
                f"select disk {disk.index}",
                "select partition 1",
                "assign letter=S"
            ])
            efi_letter = "S"
    else:
        efi_letter = target_letter

    drive_map = {
        "efi": efi_letter or "S",
        "windows": target_letter,
        "data": "",
    }
    state.advance(Step.DISK_PARTITIONED, drive_map=drive_map)
    log_cb(progress, f"✓ Phân vùng Windows ({target_letter}:) & Boot ({efi_letter}:) đã sẵn sàng", 20.0)
    return True, "OK", drive_map

# ── Bước 3: Bootloader ──────────────────────────────────────────────

def setup_bootloader(
    state: InstallState,
    disk: Disk,
    windows_drive: str,
    efi_drive: str,
    progress: Optional[Callable] = None,
) -> tuple[bool, str]:
    log_cb(progress, "Đang cài bootloader...", 86)

    if disk.is_gpt:
        ok, msg = install_bootloader(windows_drive, efi_drive)
    else:
        ok, msg = install_bootloader_mbr(windows_drive)

    if not ok:
        return False, f"Bootloader lỗi: {msg}"

    state.advance(Step.BOOTLOADER_SET)
    log_cb(progress, "Bootloader OK", 88)
    return True, "OK"

# ── Bước 4: Unattend + RunOnce ─────────────────────────────────────

def write_unattend(
    state: InstallState,
    windows_drive: str,
    config: dict,
    tool_exe_path: str,
    progress: Optional[Callable] = None,
) -> tuple[bool, str]:
    log_cb(progress, "Đang tạo unattend.xml...", 89)

    panther = Path(f"{windows_drive}:\\Windows\\Panther")
    panther.mkdir(parents=True, exist_ok=True)

    sysprep = Path(f"{windows_drive}:\\Windows\\System32\\Sysprep")
    sysprep.mkdir(parents=True, exist_ok=True)

    # Copy tool exe vào Windows mới để Phase 3 chạy
    setup_scripts = Path(f"{windows_drive}:\\Windows\\Setup\\Scripts")
    setup_scripts.mkdir(parents=True, exist_ok=True)
    tool_dest = setup_scripts / "TXAWinSetup.exe"

    try:
        shutil.copy2(tool_exe_path, tool_dest)
    except Exception as e:
        log_cb(progress, f"[WARN] Không copy được tool: {e}", 89)
        tool_dest = Path(tool_exe_path)

    # Copy Avatar người dùng mặc định và OEM Logo của TXA Studio
    try:
        def get_asset_path(filename: str):
            if hasattr(sys, "_MEIPASS"):
                p = Path(sys._MEIPASS) / "assets" / filename
                if p.exists():
                    return p
            candidates = [
                Path(__file__).resolve().parent.parent / "assets" / filename,
                Path.cwd() / "assets" / filename,
            ]
            for c in candidates:
                if c.exists():
                    return c
            return None

        user_pics_dir = Path(f"{windows_drive}:\\ProgramData\\Microsoft\\User Account Pictures")
        user_pics_dir.mkdir(parents=True, exist_ok=True)
        for pic in ("user.png", "user.bmp", "user-192.png", "user-48.png", "user-40.png", "user-32.png", "guest.png", "guest.bmp"):
            src = get_asset_path(pic)
            if src and src.is_file():
                shutil.copy2(src, user_pics_dir / pic)

        oem_src = get_asset_path("oemlogo.bmp")
        if oem_src and oem_src.is_file():
            sys32 = Path(f"{windows_drive}:\\Windows\\System32")
            sys32.mkdir(parents=True, exist_ok=True)
            shutil.copy2(oem_src, sys32 / "oemlogo.bmp")
    except Exception as e:
        log_cb(progress, f"[WARN] Thiết lập avatar mặc định: {e}", 89)

    runonce_cmd = f'"{tool_dest}" --phase3'

    custom_unattend = config.get("custom_unattend_path", "")
    if custom_unattend and Path(custom_unattend).is_file():
        log_cb(progress, f"Đang nạp file cấu hình unattend tùy chọn: {Path(custom_unattend).name}", 89)
        try:
            shutil.copy2(custom_unattend, panther / "unattend.xml")
            shutil.copy2(custom_unattend, sysprep / "unattend.xml")
            shutil.copy2(custom_unattend, Path(f"{windows_drive}:\\autounattend.xml"))
        except Exception as e:
            log_cb(progress, f"[WARN] Không copy được file unattend tùy chọn: {e}", 89)
    else:
        xml = gen_unattend(
            username=config.get("username", "User"),
            password=config.get("password", ""),
            computer_name=config.get("computer_name", "TXA-WIN"),
            timezone=config.get("timezone", "SE Asia Standard Time"),
            product_key=config.get("product_key", ""),
            bypass_tpm=config.get("bypass_tpm", True),
            auto_logon=config.get("auto_logon", True),
            runonce_cmd=runonce_cmd,
            output_path=str(panther / "unattend.xml"),
        )
        try:
            (sysprep / "unattend.xml").write_text(xml, encoding="utf-8")
            (Path(f"{windows_drive}:\\autounattend.xml")).write_text(xml, encoding="utf-8")
        except Exception:
            pass

    # Copy các file Registry Tweaks được người dùng tích chọn
    selected_tweaks = config.get("selected_tweak_paths", [])
    if selected_tweaks:
        tweaks_dest = setup_scripts / "Tweaks"
        tweaks_dest.mkdir(parents=True, exist_ok=True)
        for tp in selected_tweaks:
            p_obj = Path(tp)
            if p_obj.is_file():
                try:
                    shutil.copy2(tp, tweaks_dest / p_obj.name)
                except Exception:
                    pass

    # Ghi SetupComplete.cmd chứa các tweak tinh chỉnh hệ thống TXA
    from .unattend import generate_setup_complete
    setup_cmd_content = generate_setup_complete(
        username=config.get("username", "User"),
        password=config.get("password", ""),
        computer_name=config.get("computer_name", "TXA-WIN"),
        classic_context_menu=config.get("classic_context_menu", True),
        disable_bitlocker=config.get("disable_bitlocker", True),
        disable_telemetry=config.get("disable_telemetry", True),
        disable_hibernation=config.get("disable_hibernation", True),
        disable_search_indexing=config.get("disable_search_indexing", False),
        high_performance_power=config.get("high_performance_power", True),
        auto_activate=config.get("auto_activate", True),
        product_key=config.get("product_key", ""),
    )
    (setup_scripts / "SetupComplete.cmd").write_text(setup_cmd_content, encoding="utf-8")

    state.advance(Step.UNATTEND_WRITTEN, tool_dest=str(tool_dest))
    log_cb(progress, "Unattend.xml & SetupComplete.cmd OK", 91)
    return True, "OK"

# ── Bước 5: Driver backup copy ─────────────────────────────────────

def copy_drivers(
    state: InstallState,
    driver_backup_path: str,
    windows_drive: str,
    progress: Optional[Callable] = None,
) -> tuple[bool, str]:
    if not driver_backup_path or not Path(driver_backup_path).exists():
        return True, "Không có driver backup"

    dest = Path(f"{windows_drive}:\\Drivers")
    dest.mkdir(exist_ok=True)

    log_cb(progress, "Đang copy driver vào phân vùng cài đặt...", 91)
    try:
        shutil.copytree(driver_backup_path, str(dest), dirs_exist_ok=True)
    except Exception as e:
        return False, str(e)

    # Nạp (Inject) Driver trực tiếp vào hệ điều hành mới qua DISM Offline
    log_cb(progress, "Đang nạp (inject) driver trực tiếp vào Windows mới...", 93)
    try:
        _run(f'dism /Image:"{windows_drive}:\\" /Add-Driver /Driver:"{dest}" /Recurse /ForceUnsigned', timeout=600)
    except Exception:
        pass

    log_cb(progress, "Đã bảo lưu và khôi phục Driver thành công!", 94)
    return True, "OK"

# ── Shell replacement (kiosk mode) ──────────────────────────────────

def set_shell_replacement(exe_path: str):
    """Set tool exe làm shell thay thế explorer — nếu boot vào Windows sẽ thấy tool."""
    _run(
        f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" '
        f'/v Shell /t REG_SZ /d "{exe_path}" /f'
    )

def restore_shell():
    """Khôi phục explorer.exe làm shell sau khi cài xong."""
    _run(
        'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" '
        '/v Shell /t REG_SZ /d "explorer.exe" /f'
    )

# ── Phase 3: Cài driver sau reboot ──────────────────────────────────

def phase3_install_drivers(
    state: InstallState,
    progress: Optional[Callable] = None,
) -> tuple[bool, str]:
    driver_dir = Path("C:\\Drivers")
    if driver_dir.exists():
        log_cb(progress, "Đang cài driver...", 20)
        _, out = _run(
            f'dism /Online /Add-Driver /Driver:"{driver_dir}" /Recurse /ForceUnsigned',
            timeout=300
        )
        log_cb(progress, "Driver cài xong", 80)

    state.advance(Step.POST_REBOOT_1)
    return True, "OK"

def phase3_cleanup(state: InstallState, progress: Optional[Callable] = None):
    """Dọn dẹp: xóa file temp, restore shell, xóa state."""
    log_cb(progress, "Đang dọn dẹp...", 85)
    restore_shell()

    # Xóa RunOnce key
    _run(
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" '
        '/v TXAWinSetup /f'
    )

    # Xóa driver folder
    try:
        shutil.rmtree("C:\\Drivers", ignore_errors=True)
    except Exception:
        pass

    state.advance(Step.POST_REBOOT_2)
    state.clear()
    log_cb(progress, "Hoàn tất!", 100)

# ── Full run orchestration ───────────────────────────────────────────

def run_full_install(
    state: InstallState,
    disk: Disk,
    wim_path: str,
    image_index: int,
    config: dict,
    driver_backup_path: str,
    tool_exe_path: str,
    progress: Optional[Callable] = None,
) -> tuple[bool, str]:
    """Chạy toàn bộ Phase 2 từ đầu."""

    layout = suggest_partition_layout(
        disk,
        c_size_gb=config.get("c_gb")
    )
    c_gb = layout["c_gb"]
    data_gb = layout["data_gb"]

    # Ghi state trước khi làm gì destructive
    state.config.update(config)
    state.config["wim_path"] = wim_path
    state.config["image_index"] = image_index
    state.config["disk_index"] = disk.index
    state.config["is_system_disk"] = disk.is_system_disk

    if disk.is_system_disk:
        log_cb(progress, "⚠️ Phát hiện cài đặt lên ổ đĩa hệ thống đang chạy (chứa Windows hiện tại)...", 10.00)
        log_cb(progress, "Do Windows đang chạy trực tiếp trên ổ này, không thể format C: ngay trong phiên hiện tại.", 20.00)
        log_cb(progress, "Đang thiết lập môi trường riêng cho tool (TXA Boot Environment / RAMDisk)...", 35.00)

        from .boot_env import setup_txa_boot_environment
        iso_drive = state.config.get("wim_drive", "")
        setup_txa_boot_environment(iso_drive=iso_drive, progress_cb=lambda p, m: log_cb(progress, m, p * 0.4 + 35.0))

        set_shell_replacement(tool_exe_path)
        state.advance(Step.SHELL_REPLACED)

        if driver_backup_path:
            log_cb(progress, f"Đang bảo lưu cấu hình driver: {driver_backup_path}", 85.00)

        log_cb(progress, "✓ Đã thiết lập môi trường riêng cho tool và lưu trạng thái thành công!", 100.00)
        log_cb(progress, "Máy tính sẽ khởi động lại và tự động nạp môi trường riêng để cài đặt...", 100.00)
        return True, "SYSTEM_DISK_REBOOT"

    set_shell_replacement(tool_exe_path)
    state.advance(Step.SHELL_REPLACED)

    # 1. Phân vùng / Chuẩn bị ổ đĩa theo chế độ đã chọn
    install_mode = config.get("install_mode", "existing_partition")
    if install_mode == "clean_disk":
        log_cb(progress, f"⚡ Chế độ: Xóa sạch toàn bộ Disk {disk.index} và phân chia lại...", 5.0)
        ok, msg, drive_map = partition_disk(state, disk, c_gb, data_gb, progress)
    else:
        target_letter = config.get("target_partition_letter", "C")
        quick_fmt = config.get("quick_format", True)
        log_cb(progress, f"🛡️ Chế độ an toàn: Cài đặt vào phân vùng {target_letter}: (Bảo toàn dữ liệu các phân vùng khác)", 5.0)
        ok, msg, drive_map = format_and_prepare_existing_partition(
            state=state,
            disk=disk,
            target_letter=target_letter,
            quick_format=quick_fmt,
            progress=progress
        )

    if not ok:
        return False, f"Chuẩn bị phân vùng lỗi: {msg}"

    win_drive = drive_map["windows"]
    efi_drive = drive_map.get("efi", "S")
    state.config["drive_map"] = drive_map
    state.save()

    # 2. Apply WIM
    ok, msg = apply_windows(state, wim_path, image_index, win_drive, progress)
    if not ok:
        return False, f"Apply WIM lỗi: {msg}"

    # 3. Bootloader
    ok, msg = setup_bootloader(state, disk, win_drive, efi_drive, progress)
    if not ok:
        return False, msg

    # 4. Unattend
    ok, msg = write_unattend(state, win_drive, config, tool_exe_path, progress)
    if not ok:
        return False, msg

    # 5. Driver copy
    copy_drivers(state, driver_backup_path, win_drive, progress)

    log_cb(progress, "Sẵn sàng khởi động lại!", 98)
    return True, "OK"
