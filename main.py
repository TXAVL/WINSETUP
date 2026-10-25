"""
TXA WinSetup — Entry point
Chạy: python main.py
      python main.py --phase3     (sau reboot, cài driver)
"""
import sys, os, ctypes, atexit, shutil
from pathlib import Path

# Ngăn hoàn toàn Python sinh file cache .pyc và thư mục __pycache__
sys.dont_write_bytecode = True

def _clean_pycache():
    try:
        base = Path(__file__).resolve().parent
        for p in base.rglob("__pycache__"):
            if p.exists() and p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
    except Exception:
        pass

# Tự động dọn sạch lúc khởi chạy và khi thoát
_clean_pycache()
atexit.register(_clean_pycache)

# Fix Unicode output trên Windows console
try:
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    """Tự relaunch với quyền Admin nếu chưa có."""
    if "--elevated" in sys.argv or "--no-admin" in sys.argv:
        return
    script_path = os.path.abspath(sys.argv[0])
    script_dir = os.path.dirname(script_path)
    args = [f'"{script_path}"', "--elevated"] + [f'"{a}"' for a in sys.argv[1:] if a != "--elevated"]
    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            " ".join(args),
            script_dir, 1
        )
        if ret > 32:
            sys.exit(0)
    except Exception as e:
        print(f"Không thể nâng quyền Admin: {e}")

def main():
    try:
        # Tự động phát hiện môi trường WinPE / WinRE
        from core.disk import is_winpe
        in_pe = is_winpe()

        if in_pe:
            print("[INFO] Đang chạy trong môi trường Windows PE (RAMDisk X:\\).")
            admin = True
        else:
            admin = is_admin()
            if not admin:
                print("[INFO] Đang chạy với quyền User thường (chế độ xem trước).")
                print("[INFO] Để thực hiện phân vùng ổ đĩa và cài đặt, hãy chuột phải chọn 'Run as administrator'.")

        # Parse args
        phase3 = "--phase3" in sys.argv
        initial_iso = ""
        for arg in sys.argv[1:]:
            if arg.startswith("--"):
                continue
            clean_arg = arg.strip(' "\'')
            if clean_arg and Path(clean_arg).is_file():
                ext = Path(clean_arg).suffix.lower()
                if ext in [".iso", ".wim", ".esd", ".swm"]:
                    initial_iso = str(Path(clean_arg).resolve())
                    break

        # Fix DPI scaling trên Windows
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # Load state
        from core.state import InstallState
        state = InstallState()

        # Launch GUI
        from ui.app import TXAWinSetup
        app = TXAWinSetup(state, is_phase3=phase3, is_winpe=in_pe, initial_iso=initial_iso)

        # Đảm bảo cửa sổ nổi lên trên cùng màn hình khi mở
        app.deiconify()
        app.lift()
        app.attributes("-topmost", True)
        app.after(500, lambda: app.attributes("-topmost", False))
        app.focus_force()

        print("[INFO] Cửa sổ TXA WinSetup đã mở.")
        app.mainloop()
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(err_msg)
        with open("crash.log", "w", encoding="utf-8") as f:
            f.write(err_msg)

if __name__ == "__main__":
    main()
