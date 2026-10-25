"""
Đọc OEM product key từ BIOS/ACPI (OA3 — OEM Activation 3.0)
"""
import subprocess, re, ctypes, ctypes.wintypes

def _run(cmd: str) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, shell=True, timeout=15)
        return r.stdout.strip()
    except Exception:
        return ""

def get_bios_key() -> str:
    """
    Đọc OEM key nhúng trong BIOS (ACPI MSDM table).
    Trả về product key dạng XXXXX-XXXXX-XXXXX-XXXXX-XXXXX hoặc "" nếu không có.
    """
    # Cách 1: WMI SoftwareLicensingService (cách chính thức)
    out = _run(
        'powershell -NoProfile -Command "'
        '(Get-WmiObject -query \'select * from SoftwareLicensingService\').OA3xOriginalProductKey"'
    )
    key = out.strip()
    if _is_valid_key(key):
        return key

    # Cách 2: PowerShell trực tiếp
    out = _run(
        'powershell -NoProfile -Command "'
        '$sls = Get-CimInstance SoftwareLicensingService; $sls.OA3xOriginalProductKey"'
    )
    key = out.strip()
    if _is_valid_key(key):
        return key

    # Cách 3: Đọc ACPI MSDM table qua kernel (cần admin)
    key = _read_acpi_msdm()
    if _is_valid_key(key):
        return key

    return ""

def _is_valid_key(key: str) -> bool:
    if not key:
        return False
    pattern = r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$'
    return bool(re.match(pattern, key.upper().strip()))

def _read_acpi_msdm() -> str:
    """Đọc thẳng MSDM ACPI table để lấy key."""
    try:
        # EnumSystemFirmwareTables + GetSystemFirmwareTable
        kernel32 = ctypes.windll.kernel32

        provider = ctypes.c_uint32(0x41435049)  # 'ACPI'
        table_id = ctypes.c_uint32(0x4D44534D)  # 'MSDM'

        # Lấy size trước
        size = kernel32.GetSystemFirmwareTable(provider, table_id, None, 0)
        if size == 0:
            return ""

        buf = (ctypes.c_char * size)()
        result = kernel32.GetSystemFirmwareTable(provider, table_id, buf, size)
        if result == 0:
            return ""

        data = bytes(buf)
        # MSDM structure: header (36 bytes) + data (rồi key ở cuối)
        # Key là ASCII string ở cuối table, thường offset 56 hoặc 68
        for offset in range(36, len(data) - 29):
            try:
                candidate = data[offset:offset+29].decode('ascii', errors='replace')
                if _is_valid_key(candidate):
                    return candidate
            except Exception:
                continue
        return ""
    except Exception:
        return ""

def get_key_edition(key: str) -> str:
    """
    Xác định edition từ product key (dựa vào channel prefix).
    Trả về "Pro", "Home", "Enterprise", ... hoặc "" nếu không xác định được.
    """
    if not key or not _is_valid_key(key):
        return ""

    # Microsoft public generic/channel keys để nhận dạng edition
    EDITION_MAP = {
        # Windows 11
        "W269N": "Home",
        "NF6HC": "Home N",
        "VK7JG": "Pro",
        "NW6C2": "Pro N",
        "W11NK": "Pro for Workstations",
        "PW8NR": "Pro for Workstations N",
        "2B87N": "Pro Education",
        "GJTYN": "Enterprise",
        "NPPR9": "Enterprise",
        "DPH2V": "Enterprise N",
        "YYVX9": "Enterprise S",
        "WNMTR": "Enterprise 2015 LTSB",
        "2F77B": "Enterprise 2015 LTSB N",
        # Windows 10 (vẫn hay gặp)
        "TX9XD": "Home",
        "3KHY7": "Home N",
        "7HNRX": "Home Country Specific",
        "PVMJN": "Home Single Language",
        "W269N-WFGWX": "Pro",
        "MH37W": "Pro",
    }

    prefix = key.split("-")[0].upper()
    return EDITION_MAP.get(prefix, "Unknown")

def get_installed_key() -> str:
    """Đọc key Windows đang cài (từ registry — thường bị ẩn)."""
    out = _run(
        'powershell -NoProfile -Command "'
        '(Get-ItemProperty "HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion").DigitalProductId"'
    )
    # DigitalProductId là binary, cần decode riêng
    # Dùng cách dễ hơn:
    out2 = _run(
        'powershell -NoProfile -Command "'
        '$key = (Get-WmiObject -Class SoftwareLicensingProduct | '
        'Where-Object { $_.Name -like \'Windows*\' -and $_.LicenseStatus -eq 1 } | '
        'Select-Object -First 1).ProductKeyPartial; $key"'
    )
    return out2.strip()
