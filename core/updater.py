"""
TXA WinSetup - Trình kiểm tra & Tự động Cập nhật (Auto Updater)
Lấy thông tin phiên bản mới nhất từ file latest.yml trên GitHub Release của repository TXAVL/WINSETUP
"""
import urllib.request
import re
import threading
from typing import Dict, Any, Optional, Tuple

APP_VERSION = "1.4.0"
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
            if line.startswith("  ") or line.startswith("\t"):
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

        setup_name = data.get("setup_name", "TXAWinSetup_Setup.exe")
        try:
            setup_size = int(data.get("setup_size", 0))
        except Exception:
            setup_size = 0
        setup_sha256 = data.get("setup_sha256", "").strip()

        portable_name = data.get("portable_name", "TXAWinSetup_Portable.exe")
        try:
            portable_size = int(data.get("portable_size", 0))
        except Exception:
            portable_size = 0
        portable_sha256 = data.get("portable_sha256", "").strip()

        return {
            "success": True,
            "has_update": has_update,
            "current_version": APP_VERSION,
            "latest_version": latest_ver,
            "release_date": data.get("release_date", "2026-10-25"),
            "setup_name": setup_name,
            "setup_size": setup_size,
            "setup_sha256": setup_sha256,
            "setup_url": setup_url,
            "portable_name": portable_name,
            "portable_size": portable_size,
            "portable_sha256": portable_sha256,
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

def download_file_resumable(
    url: str,
    dest_path: str,
    expected_sha256: str = "",
    expected_size: int = 0,
    progress_callback = None,
    cancel_event: Optional[threading.Event] = None,
) -> Tuple[bool, str]:
    """
    Tải file từ URL có hỗ trợ tiếp tục (resume) nếu bị ngắt quãng.
    progress_callback: fn(downloaded_bytes, total_bytes, speed_bps, status_text)
    cancel_event: Event để dừng/hủy tiến trình
    Trả về: (thành_công: bool, thông_điệp_hoặc_đường_dẫn_lỗi: str)
    """
    import os, time, hashlib, urllib.request, urllib.error
    from pathlib import Path

    dest_p = Path(dest_path)
    dest_p.parent.mkdir(parents=True, exist_ok=True)
    part_path = str(dest_p) + ".part"

    def check_sha256(fpath: str, exp_hash: str) -> bool:
        if not exp_hash or not os.path.exists(fpath):
            return False
        h = hashlib.sha256()
        with open(fpath, "rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest().upper() == exp_hash.upper().strip()

    # 1. Kiểm tra xem file hoàn chỉnh đã tồn tại và toàn vẹn chưa
    if os.path.exists(dest_path):
        if expected_sha256 and check_sha256(dest_path, expected_sha256):
            size = os.path.getsize(dest_path)
            if progress_callback:
                progress_callback(size, size, 0.0, "Đã có sẵn file tải về hợp lệ!")
            return True, dest_path
        elif not expected_sha256 and expected_size > 0 and os.path.getsize(dest_path) == expected_size:
            if progress_callback:
                progress_callback(expected_size, expected_size, 0.0, "Đã có sẵn file tải về hợp lệ!")
            return True, dest_path
        else:
            try:
                os.remove(dest_path)
            except Exception:
                pass

    # 2. Kiểm tra file tạm (.part) đang tải dở để tiếp tục
    downloaded = 0
    if os.path.exists(part_path):
        downloaded = os.path.getsize(part_path)
        if expected_size > 0 and downloaded > expected_size:
            try:
                os.remove(part_path)
            except Exception:
                pass
            downloaded = 0

    headers = {
        "User-Agent": f"TXAWinSetup/{APP_VERSION} (Windows; x64) GitHubReleaseClient",
        "Accept": "*/*"
    }
    if downloaded > 0:
        headers["Range"] = f"bytes={downloaded}-"

    total_bytes = expected_size

    try:
        if progress_callback:
            mode_desc = f" (tiếp tục từ {(downloaded / (1024*1024)):.1f} MB)" if downloaded > 0 else ""
            progress_callback(downloaded, total_bytes, 0.0, f"Đang kết nối tới máy chủ GitHub{mode_desc}...")

        req = urllib.request.Request(url, headers=headers)
        resp = None
        try:
            resp = urllib.request.urlopen(req, timeout=15)
        except urllib.error.HTTPError as he:
            if he.code == 416: # Range Not Satisfiable (đã tải xong toàn bộ trong file .part)
                if expected_sha256 and check_sha256(part_path, expected_sha256):
                    try:
                        if os.path.exists(dest_path):
                            os.remove(dest_path)
                        os.rename(part_path, dest_path)
                    except Exception as e:
                        return False, f"Không thể lưu file tải về: {e}"
                    return True, dest_path
                # Nếu không khớp thì xóa file part và tải lại từ đầu
                try:
                    os.remove(part_path)
                except Exception:
                    pass
                downloaded = 0
                req = urllib.request.Request(url, headers={"User-Agent": headers["User-Agent"]})
                resp = urllib.request.urlopen(req, timeout=15)
            else:
                return False, f"Máy chủ phản hồi lỗi HTTP {he.code}: {he.reason}"

        status_code = getattr(resp, "status", getattr(resp, "code", 200))
        content_range = resp.headers.get("Content-Range")
        content_length = resp.headers.get("Content-Length")

        if status_code == 206:
            file_mode = "ab"
            if content_range and "/" in content_range:
                try:
                    total_bytes = int(content_range.split("/")[-1].strip())
                except Exception:
                    pass
            elif content_length:
                try:
                    total_bytes = downloaded + int(content_length.strip())
                except Exception:
                    pass
        else:
            file_mode = "wb"
            downloaded = 0
            if content_length:
                try:
                    total_bytes = int(content_length.strip())
                except Exception:
                    pass

        chunk_size = 64 * 1024
        last_time = time.time()
        last_bytes = downloaded
        speed = 0.0

        with open(part_path, file_mode) as f:
            while True:
                if cancel_event and cancel_event.is_set():
                    return False, "Đã tạm dừng tiến trình tải xuống."
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                now = time.time()
                dt = now - last_time
                if dt >= 0.15:
                    speed = (downloaded - last_bytes) / dt if dt > 0 else 0.0
                    last_time = now
                    last_bytes = downloaded
                    if progress_callback:
                        progress_callback(downloaded, total_bytes, speed, "Đang tải xuống dữ liệu...")

        if total_bytes > 0 and downloaded < total_bytes:
            return False, f"Tải xuống bị gián đoạn ({downloaded}/{total_bytes} bytes). Bấm 'Tiếp tục tải' để tải tiếp."

        try:
            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(part_path, dest_path)
        except Exception as e:
            return False, f"Lỗi hoàn tất tệp tải về: {e}"

        if expected_sha256:
            if progress_callback:
                progress_callback(downloaded, total_bytes, 0.0, "Đang xác thực mã toàn vẹn SHA256...")
            if not check_sha256(dest_path, expected_sha256):
                try:
                    os.remove(dest_path)
                except Exception:
                    pass
                return False, "Mã băm SHA256 của file tải về không khớp! File có thể bị lỗi mạng hoặc bị can thiệp."

        if progress_callback:
            progress_callback(downloaded, total_bytes, 0.0, "Tải thành công và đã xác thực!")
        return True, dest_path

    except urllib.error.URLError as ue:
        return False, f"Mất kết nối mạng: {ue.reason}. Bấm 'Tiếp tục tải' để tải tiếp."
    except Exception as e:
        return False, f"Lỗi trong quá trình tải: {e}. Bấm 'Tiếp tục tải' để thử lại."

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


REG_SUBKEY = r"Software\TXA Studio\TXA WinSetup"
REG_VAL_AUTOCHECK = "AutoCheckUpdate"

def _get_settings_file():
    import os
    from pathlib import Path
    appdata = os.environ.get("LOCALAPPDATA")
    if appdata:
        p = Path(appdata) / "TXAWinSetup" / "settings.json"
    else:
        p = Path(__file__).resolve().parent.parent / "settings.json"
    return p

def is_auto_check_enabled() -> bool:
    """Kiểm tra xem chế độ tự động kiểm tra cập nhật có bật không (mặc định bật)."""
    # 1. Thử đọc từ Registry Windows
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, REG_VAL_AUTOCHECK)
            return bool(val)
    except Exception:
        pass

    # 2. Thử đọc từ settings.json cục bộ
    try:
        import json
        sf = _get_settings_file()
        if sf.exists():
            with open(sf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "auto_check_update" in data:
                    return bool(data["auto_check_update"])
    except Exception:
        pass

    # Mặc định là True (Bật)
    return True

def set_auto_check_enabled(enabled: bool) -> bool:
    """Lưu cài đặt tự động kiểm tra cập nhật vào Registry và settings.json."""
    saved = False
    # 1. Ghi vào Registry Windows
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY) as key:
            winreg.SetValueEx(key, REG_VAL_AUTOCHECK, 0, winreg.REG_DWORD, 1 if enabled else 0)
        saved = True
    except Exception:
        pass

    # 2. Ghi vào settings.json cục bộ
    try:
        import json
        sf = _get_settings_file()
        sf.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if sf.exists():
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
        data["auto_check_update"] = bool(enabled)
        with open(sf, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        saved = True
    except Exception:
        pass

    return saved

