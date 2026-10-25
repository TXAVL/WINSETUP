"""
TXA WinSetup - Trình quản lý nạp tài nguyên tự động (Resource Loader)
Tự động phát hiện và đồng bộ các thư mục:
- unattend/ (File trả lời tự động .xml)
- drivers/  (Các gói driver offline)
- tweaks/   (Các file tinh chỉnh registry .reg)
"""
import sys, os
from pathlib import Path
from typing import List, Dict, Any

def get_base_dir() -> Path:
    """Trả về thư mục gốc ứng dụng bên ngoài (chứa file exe hoặc mã nguồn)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent

def get_bundled_dir() -> Path:
    """Trả về thư mục gói bên trong (sys._MEIPASS khi chạy onefile) hoặc thư mục gốc."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return get_base_dir()

def ensure_resource_folders() -> Dict[str, Path]:
    """Tự động kiểm tra và khởi tạo 3 thư mục unattend, drivers, tweaks nếu chưa có."""
    import shutil
    base = get_base_dir()
    bundled = get_bundled_dir()
    folders = {
        "unattend": base / "unattend",
        "drivers": base / "drivers",
        "tweaks": base / "tweaks",
    }
    for name, p in folders.items():
        p.mkdir(parents=True, exist_ok=True)
        # Nếu thư mục người dùng đang trống nhưng trong bundle có sẵn -> copy ra
        b_folder = bundled / name
        if b_folder.exists() and b_folder.is_dir() and not any(p.iterdir()):
            for item in b_folder.iterdir():
                try:
                    if item.is_file():
                        shutil.copy2(item, p / item.name)
                    elif item.is_dir():
                        shutil.copytree(item, p / item.name, dirs_exist_ok=True)
                except Exception:
                    pass
    return folders

def get_unattend_files() -> List[Dict[str, str]]:
    """Quét và trả về danh sách các file cấu hình unattend XML có sẵn."""
    base = get_base_dir()
    unattend_dir = base / "unattend"
    results = [
        {
            "id": "builtin",
            "name": "⚡ Tự động tạo XML theo thiết lập bên dưới (Khuyên dùng)",
            "path": "",
            "desc": "Tạo động dựa trên Username, Password, Bypass TPM & OOBE"
        }
    ]

    if unattend_dir.exists():
        for f in sorted(unattend_dir.glob("*.xml")):
            # Đọc dòng mô tả đầu tiên trong file xml nếu có
            title = f.stem.replace("_", " ").title()
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines()[:5]:
                    if "<!--" in line and "-->" in line:
                        comment = line.split("<!--")[1].split("-->")[0].strip()
                        if comment:
                            title = comment.replace("TXA WinSetup - ", "")
                            break
            except Exception:
                pass
            results.append({
                "id": f.name,
                "name": f"📄 {title} ({f.name})",
                "path": str(f.resolve()),
                "desc": f.name
            })
    return results

def get_driver_packages() -> List[Dict[str, str]]:
    """Quét và trả về danh sách các gói driver có sẵn trong thư mục drivers/."""
    base = get_base_dir()
    drv_dir = base / "drivers"
    results = [
        {
            "id": "current_machine",
            "name": "⚡ Tự động sao lưu & nạp Driver từ máy hiện tại (Khuyên dùng)",
            "path": "",
            "desc": "Trích xuất driver Wifi, LAN, Touchpad, Audio của máy này"
        }
    ]

    if drv_dir.exists():
        for item in sorted(drv_dir.iterdir()):
            if item.is_dir() and not item.name.startswith("."):
                name = item.name.replace("_", " ")
                results.append({
                    "id": item.name,
                    "name": f"📦 Gói Driver: {name} (drivers\\{item.name})",
                    "path": str(item.resolve()),
                    "desc": str(item)
                })
    return results

def get_available_tweaks() -> List[Dict[str, Any]]:
    """Quét toàn bộ các file .reg trong thư mục tweaks/ và lấy thông tin chi tiết."""
    base = get_base_dir()
    tweaks_dir = base / "tweaks"
    results = []

    if tweaks_dir.exists():
        for f in sorted(tweaks_dir.glob("*.reg")):
            title = f.stem.replace("_", " ").title()
            desc = "Áp dụng tinh chỉnh Windows qua Registry"
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                lines = [l.strip() for l in content.splitlines() if l.strip().startswith(";")]
                # Lấy dòng comment đầu tiên có ý nghĩa
                for l in lines:
                    c = l.lstrip("; -=").strip()
                    if c and "txa" not in c.lower() and len(c) > 5:
                        title = c
                        break
            except Exception:
                pass

            # Mặc định bật hầu hết các tweak tối ưu an toàn
            default_on = True
            if "search" in f.name.lower():
                default_on = False

            results.append({
                "id": f.name,
                "title": title,
                "desc": f.name,
                "path": str(f.resolve()),
                "default": default_on
            })
    return results
