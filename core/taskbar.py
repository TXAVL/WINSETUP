"""
TXA WinSetup - Windows Taskbar Progress Controller (ITaskbarList3)
Hiển thị tiến trình cài đặt trực tiếp trên thanh tác vụ (Taskbar) của Windows.
Hỗ trợ các trạng thái:
- Normal (Xanh lá): Tiến trình đang chạy từ 0% đến 100%
- Error (Đỏ): Thất bại / Báo lỗi
- Paused (Vàng): Tạm dừng hoặc chờ xác nhận
- Indeterminate: Đang xử lý không xác định phần trăm
- NoProgress: Trở về trạng thái bình thường khi hoàn tất
"""
import sys
import ctypes
from ctypes import wintypes, POINTER, c_void_p, c_ulonglong, c_int, WINFUNCTYPE, c_long
from typing import Optional

# Ngăn hoàn toàn Python sinh file cache .pyc và thư mục __pycache__
sys.dont_write_bytecode = True

class GUID(ctypes.Structure):
    _fields_ = [
        ('Data1', wintypes.DWORD),
        ('Data2', wintypes.WORD),
        ('Data3', wintypes.WORD),
        ('Data4', wintypes.BYTE * 8)
    ]

CLSID_TaskbarList = GUID(
    0x56FDF344, 0xFD6D, 0x11d0,
    (wintypes.BYTE * 8)(0x95, 0x8A, 0x00, 0x60, 0x97, 0xC9, 0xA0, 0x90)
)
IID_ITaskbarList3 = GUID(
    0xEA1AFB91, 0x9E28, 0x4b86,
    (wintypes.BYTE * 8)(0x90, 0xE9, 0x9E, 0x9F, 0x8A, 0x5E, 0xEF, 0xAF)
)

class TaskbarProgress:
    TBPF_NOPROGRESS    = 0x00000000
    TBPF_INDETERMINATE = 0x00000001
    TBPF_NORMAL        = 0x00000002
    TBPF_ERROR         = 0x00000004
    TBPF_PAUSED        = 0x00000008

    def __init__(self):
        self._taskbar = None
        self._set_value_fn = None
        self._set_state_fn = None
        self._default_hwnd = None
        self._initialized = False
        self._init_com()

    def _init_com(self):
        if sys.platform != "win32":
            return
        try:
            ole32 = ctypes.windll.ole32
            ole32.CoInitialize(None)

            tb = c_void_p()
            hr = ole32.CoCreateInstance(
                ctypes.byref(CLSID_TaskbarList),
                None,
                1,  # CLSCTX_INPROC_SERVER
                ctypes.byref(IID_ITaskbarList3),
                ctypes.byref(tb)
            )
            if hr == 0 and tb:
                vtable = ctypes.cast(tb, POINTER(POINTER(c_void_p))).contents
                self._taskbar = tb
                # Vtable index 9: SetProgressValue(HWND, ULONGLONG, ULONGLONG)
                self._set_value_fn = WINFUNCTYPE(
                    c_long, c_void_p, wintypes.HWND, c_ulonglong, c_ulonglong
                )(vtable[9])
                # Vtable index 10: SetProgressState(HWND, int)
                self._set_state_fn = WINFUNCTYPE(
                    c_long, c_void_p, wintypes.HWND, c_int
                )(vtable[10])
                self._initialized = True
        except Exception:
            self._taskbar = None
            self._initialized = False

    def set_default_hwnd(self, hwnd):
        """Đặt HWND mặc định (tự động tìm top-level window)."""
        self._default_hwnd = self._resolve_hwnd(hwnd)

    def _resolve_hwnd(self, hwnd) -> Optional[int]:
        target = hwnd or self._default_hwnd
        if not target:
            return None
        try:
            user32 = ctypes.windll.user32
            # GA_ROOTOWNER = 3, lấy cửa sổ cấp cao nhất trên Taskbar
            root = user32.GetAncestor(wintypes.HWND(int(target)), 3)
            return root if root else int(target)
        except Exception:
            return int(target) if target else None

    def set_progress(self, pct: float, hwnd=None):
        """
        Cập nhật tiến trình phần trăm lên Taskbar:
        - pct < 0: Chuyển sang trạng thái Lỗi (Đỏ)
        - 0 <= pct <= 100: Màu xanh (Normal) với tỷ lệ tương ứng
        - pct >= 100: Màu xanh hoàn tất 100%
        """
        if not self._initialized or not self._taskbar:
            return
        target = self._resolve_hwnd(hwnd)
        if not target:
            return

        try:
            if pct < 0:
                self._set_state_fn(self._taskbar, target, self.TBPF_ERROR)
                self._set_value_fn(self._taskbar, target, 100, 100)
            elif pct >= 100:
                self._set_state_fn(self._taskbar, target, self.TBPF_NORMAL)
                self._set_value_fn(self._taskbar, target, 10000, 10000)
            else:
                self._set_state_fn(self._taskbar, target, self.TBPF_NORMAL)
                val = max(0, min(10000, int(float(pct) * 100)))
                self._set_value_fn(self._taskbar, target, val, 10000)
        except Exception:
            pass

    def set_indeterminate(self, hwnd=None):
        """Hiển thị hiệu ứng sóng lượn không xác định thời gian trên Taskbar."""
        if not self._initialized or not self._taskbar:
            return
        target = self._resolve_hwnd(hwnd)
        if not target:
            return
        try:
            self._set_state_fn(self._taskbar, target, self.TBPF_INDETERMINATE)
        except Exception:
            pass

    def set_error(self, hwnd=None):
        """Đổi thanh tác vụ sang màu Đỏ báo lỗi."""
        if not self._initialized or not self._taskbar:
            return
        target = self._resolve_hwnd(hwnd)
        if not target:
            return
        try:
            self._set_state_fn(self._taskbar, target, self.TBPF_ERROR)
            self._set_value_fn(self._taskbar, target, 100, 100)
        except Exception:
            pass

    def set_paused(self, hwnd=None):
        """Đổi thanh tác vụ sang màu Vàng tạm dừng."""
        if not self._initialized or not self._taskbar:
            return
        target = self._resolve_hwnd(hwnd)
        if not target:
            return
        try:
            self._set_state_fn(self._taskbar, target, self.TBPF_PAUSED)
        except Exception:
            pass

    def clear(self, hwnd=None):
        """Xóa thanh tiến trình trên Taskbar."""
        if not self._initialized or not self._taskbar:
            return
        target = self._resolve_hwnd(hwnd)
        if not target:
            return
        try:
            self._set_state_fn(self._taskbar, target, self.TBPF_NOPROGRESS)
        except Exception:
            pass

# Instance dùng chung cho toàn bộ app
taskbar_progress = TaskbarProgress()
