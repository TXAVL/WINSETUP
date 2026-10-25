"""
TXA WinSetup - Production Builder Script
1. Đóng gói Portable EXE cho WinPE bằng PyInstaller
2. Biên dịch bộ cài đặt NSIS cho Windows
Xuất toàn bộ vào thư mục prod\
"""
import os, sys, shutil, subprocess
from pathlib import Path

# Ngăn hoàn toàn Python sinh file cache .pyc và thư mục __pycache__
sys.dont_write_bytecode = True

try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
PROD_DIR = BASE_DIR / "prod"
PROD_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("  TXA WinSetup - Production Builder")
print("  1. Portable EXE cho WinPE (X:\\ hoặc USB Cứu hộ)")
print("  2. Bộ cài đặt Windows Installer (NSIS Setup)")
print("=" * 70)

# 1. Chạy PyInstaller đóng gói Portable 1 file duy nhất cho WinPE và Bộ cài
portable_dest = PROD_DIR / "TXAWinSetup_Portable.exe"
print(f"\n[1/3] Đang đóng gói bản Portable EXE 1 file độc lập vào: {portable_dest.name}...")
portable_dist_dir = BASE_DIR / "dist"
pyinstaller_onefile_cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--distpath", str(portable_dist_dir),
    "--windowed",
    "--name", "TXAWinSetup",
    "--icon", str(BASE_DIR / "assets" / "icon.ico"),
    "--version-file", str(BASE_DIR / "assets" / "version.txt"),
    "--add-data", f"{BASE_DIR / 'assets'};assets",
    "--add-data", f"{BASE_DIR / 'unattend'};unattend",
    "--add-data", f"{BASE_DIR / 'drivers'};drivers",
    "--add-data", f"{BASE_DIR / 'tweaks'};tweaks",
    "--add-data", f"{BASE_DIR / 'tools'};tools",
    "--uac-admin",
    "--clean",
    str(BASE_DIR / "main.py")
]
ret_onefile = subprocess.run(pyinstaller_onefile_cmd, cwd=str(BASE_DIR))
dist_portable_exe = portable_dist_dir / "TXAWinSetup.exe"

if ret_onefile.returncode == 0 and dist_portable_exe.exists():
    shutil.copy2(dist_portable_exe, portable_dest)
    print(f"[✓] Đã tạo file Portable: {portable_dest}")
else:
    print("[LỖI] Không đóng gói được bản Portable!")
    sys.exit(1)

# 2. Biên dịch bộ cài NSIS
print("\n[2/3] Đang biên dịch bộ cài đặt NSIS...")
nsis_candidates = [
    r"C:\Program Files (x86)\NSIS\makensis.exe",
    r"C:\Program Files\NSIS\makensis.exe",
    "makensis.exe"
]
makensis = None
for c in nsis_candidates:
    if os.path.exists(c):
        makensis = c
        break
    if shutil.which(c):
        makensis = c
        break

if makensis:
    nsis_script = BASE_DIR / "installer.nsi"
    print(f"Sử dụng NSIS compiler: {makensis}")
    ret_nsis = subprocess.run([makensis, "/INPUTCHARSET", "UTF8", str(nsis_script)], cwd=str(BASE_DIR))
    setup_dest = PROD_DIR / "TXAWinSetup_Setup.exe"
    if ret_nsis.returncode == 0 and setup_dest.exists():
        print(f"[✓] Đã tạo bộ cài đặt NSIS: {setup_dest}")
    else:
        print("[CẢNH BÁO] Không biên dịch được bộ cài đặt NSIS!")
else:
    print("[CẢNH BÁO] Không tìm thấy makensis.exe trên máy!")

# Tự động tính hash SHA256 và sinh metadata cập nhật latest.yml
import hashlib
def calc_sha256(filepath):
    if not filepath.exists():
        return 0, ""
    h = hashlib.sha256()
    size = filepath.stat().st_size
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return size, h.hexdigest().upper()

setup_size, setup_hash = calc_sha256(PROD_DIR / "TXAWinSetup_Setup.exe")
port_size, port_hash = calc_sha256(PROD_DIR / "TXAWinSetup_Portable.exe")

latest_yml_content = f"""version: "1.3.0"
release_date: "2026-10-25"
repository: "TXAVL/WINSETUP"
channel: "stable"
setup_name: "TXAWinSetup_Setup.exe"
setup_size: {setup_size}
setup_sha256: "{setup_hash}"
setup_url: "https://github.com/TXAVL/WINSETUP/releases/latest/download/TXAWinSetup_Setup.exe"
portable_name: "TXAWinSetup_Portable.exe"
portable_size: {port_size}
portable_sha256: "{port_hash}"
portable_url: "https://github.com/TXAVL/WINSETUP/releases/latest/download/TXAWinSetup_Portable.exe"
changelog: |
  • Nâng cấp giao diện trực quan chọn Phân vùng (Partition-first): Người dùng trực tiếp chọn phân vùng muốn cài Windows (C:\, D:\...), bảo toàn 100% dữ liệu các phân vùng khác.
  • Hỗ trợ hộp chọn Combobox thả xuống hiển thị chi tiết mọi phiên bản Windows (Home, Pro, Enterprise, Education,...) trong file ISO/WIM/ESD.
  • Đảm bảo tương thích tuyệt đối với Windows 11 Canary / Insider Preview 29695.1001 (tự động tạo tài khoản Local Admin và bypass OOBE).
  • Khắc phục hoàn toàn lỗi kẹt/đơ chuyển tab khi vào tab Tiến trình & Logs rồi bấm quay lại các tab khác.
  • Nâng cấp cửa sổ cập nhật: Hiển thị đầy đủ changelog nội dung mới khi có bản update, giữ nguyên thông báo phiên bản ổn định khi đang ở bản mới nhất.
  • Tối ưu tốc độ tải và kiểm tra phân vùng ổ đĩa (Diskpart & WMI).
"""
for yml_path in [BASE_DIR / "latest.yml", PROD_DIR / "latest.yml"]:
    with open(yml_path, "w", encoding="utf-8") as f:
        f.write(latest_yml_content)
print(f"[✓] Đã tạo tệp metadata cập nhật: {PROD_DIR / 'latest.yml'}")

print("\n" + "=" * 70)
print(f"  HOÀN TẤT XUẤT BẢN PRODUCTION TRONG THƯ MỤC: {PROD_DIR}")
print("=" * 70)
for item in PROD_DIR.iterdir():
    size_mb = item.stat().st_size / (1024 * 1024)
    print(f"  • {item.name:<32} {size_mb:6.2f} MB")
print("=" * 70)

# 3. Tự động dọn dẹp thư mục rác sau build
print("\n[3/3] Đang dọn dẹp thư mục tạm thời (build, dist, spec)...")
for p in [BASE_DIR / "build", BASE_DIR / "dist"]:
    if p.exists():
        shutil.rmtree(p, ignore_errors=True)
spec_f = BASE_DIR / "TXAWinSetup.spec"
if spec_f.exists():
    spec_f.unlink(missing_ok=True)
for pyc in BASE_DIR.rglob("__pycache__"):
    if pyc.exists():
        shutil.rmtree(pyc, ignore_errors=True)
print("[✓] Đã dọn sạch toàn bộ file tạm thời và cache!")

