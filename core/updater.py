"""
TXA WinSetup - Trình kiểm tra & Tự động Cập nhật (Auto Updater)
Lấy thông tin phiên bản mới nhất từ file latest.yml trên GitHub Release của repository TXAVL/WINSETUP
"""
import urllib.request
import re
import threading
from typing import Dict, Any, Optional, Tuple

APP_VERSION = "1.3.0"
REPO_OWNER = "TXAVL"
REPO_NAME = "WINSETUP"

# Endpoint lấy latest.yml trực tiếp từ GitHub Releases hoặc raw
RELEASE_YML_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/latest.yml"
RAW_YML_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/main/latest.yml"
RELEASES_PAGE_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases"

def parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Phân tích cú pháp cơ bản của file latest.yml mà không cần cài thêm thư viện pyyaml."""
    data: Dict[str, Any] = {}
    lines = text.replace("\r\n", "\n").split("\n")
    
    current_key = None
    multiline_buf = []
    in_multiline = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
            
        if in_multiline:
            if line.startswith("    ") or line.startswith("\t\t") or (line.startswith("  ") and not ":" in line):
                multiline_buf.append(stripped)
                continue
            else:
                data[current_key] = "\n".join(multiline_buf)
                in_multiline = False
                multiline_buf = []
                current_key = None
                
        match = re.match(r"^([a-zA-Z0-9_\-\.]+)\s*:\s*(.*)$", line)
        if match:
            k, v = match.group(1), match.group(2).strip()
            if v == "|" or v == ">":
                in_multiline = True
                current_key = k
                multiline_buf = []
            else:
                # Bỏ dấu nháy nếu có
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                data[k] = v
                
    if in_multiline and current_key:
        data[current_key] = "\n".join(multiline_buf)
        
    return data

def compare_versions(v1: str, v2: str) -> int:
    """
    So sánh hai chuỗi phiên bản dạng semver (ví dụ '1.3.0' và '1.2.0').
    Trả về:
      1 nếu v1 > v2
     -1 nếu v1 < v2
      0 nếu v1 == v2
    """
    def to_tuple(v: str) -> Tuple[int, ...]:
        clean = re.sub(r"[^\d\.]", "", v)
        parts = [int(p) for p in clean.split(".") if p.isdigit()]
        while len(parts) < 3:
            parts.append(0)
        return tuple(parts)

    t1, t2 = to_tuple(v1), to_tuple(v2)
    if t1 > t2:
        return 1
    elif t1 < t2:
        return -1
    return 0

def check_for_updates(timeout_sec: int = 6) -> Dict[str, Any]:
    """
    Kiểm tra phiên bản mới nhất từ GitHub Release.
    Trả về dict chứa thông tin phiên bản, trạng thái và đường dẫn tải về.
    """
    headers = {
        "User-Agent": f"TXAWinSetup/{APP_VERSION} (Windows; x64) GitHubReleaseClient",
        "Accept": "text/plain, text/yaml, application/x-yaml, */*"
    }
    
    content = ""
    last_err = ""
    
    for url in [RELEASE_YML_URL, RAW_YML_URL]:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout_sec) as response:
                if response.status == 200:
                    content = response.read().decode("utf-8", errors="replace")
                    break
        except Exception as e:
            last_err = str(e)
            continue
            
    if not content:
        return {
            "success": False,
            "has_update": False,
            "current_version": APP_VERSION,
            "error": last_err or "Không thể kết nối đến máy chủ cập nhật GitHub."
        }
        
    try:
        data = parse_simple_yaml(content)
        latest_ver = data.get("version", "").strip()
        if not latest_ver:
            # Tìm kiếm regex trực tiếp nếu format yml lồng nhau
            m = re.search(r'version\s*:\s*["\']?([^"\'\s]+)', content)
            if m:
                latest_ver = m.group(1)
                
        if not latest_ver:
            return {
                "success": False,
                "has_update": False,
                "current_version": APP_VERSION,
                "error": "Tệp cấu hình cập nhật latest.yml không hợp lệ."
            }
            
        has_update = compare_versions(latest_ver, APP_VERSION) > 0
        
        setup_url = data.get("setup_url", "")
        if not setup_url:
            setup_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/TXAWinSetup_Setup.exe"
            
        portable_url = data.get("portable_url", "")
        if not portable_url:
            portable_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/latest/download/TXAWinSetup_Portable.exe"

        changelog = data.get("changelog", "")
        if not changelog:
            # Tìm phần changelog trong text nếu có
            m_cl = re.search(r'changelog\s*:\s*\|\s*\n([\s\S]+?)(?=\n[a-zA-Z0-9_\-]+:|$)', content)
            if m_cl:
                changelog = m_cl.group(1).strip()
            else:
                changelog = f"Đã có phiên bản TXA WinSetup v{latest_ver} với các tính năng mới và cải tiến hiệu năng."

        return {
            "success": True,
            "has_update": has_update,
            "current_version": APP_VERSION,
            "latest_version": latest_ver,
            "release_date": data.get("release_date", "2026-10-25"),
            "setup_url": setup_url,
            "portable_url": portable_url,
            "releases_page": RELEASES_PAGE_URL,
            "changelog": changelog
        }
    except Exception as e:
        return {
            "success": False,
            "has_update": False,
            "current_version": APP_VERSION,
            "error": f"Lỗi đọc thông tin phiên bản: {e}"
        }

def check_update_async(callback):
    """Kiểm tra bản cập nhật trên luồng ngầm để không làm đơ giao diện UI."""
    def worker():
        result = check_for_updates()
        try:
            callback(result)
        except Exception:
            pass
    t = threading.Thread(target=worker, daemon=True)
    t.start()
