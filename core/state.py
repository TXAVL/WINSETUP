"""
State machine - lưu tiến trình cài đặt, phục hồi sau crash/reboot
"""
import json, os, sys, time
from pathlib import Path
from enum import IntEnum

# File state lưu ở %SystemDrive% để còn đọc được sau khi format C:
# Hoặc lưu trên ổ khác nếu đang format C:
STATE_FILENAME = "winsetup_state.json"

class Step(IntEnum):
    IDLE              = 0
    DISK_SELECTED     = 1
    CONFIG_DONE       = 2
    DRIVER_BACKUP     = 3
    DISK_PARTITIONED  = 4
    WIM_APPLIED       = 5
    BOOTLOADER_SET    = 6
    UNATTEND_WRITTEN  = 7
    SHELL_REPLACED    = 8   # Sau đây máy reboot vào Windows setup
    POST_REBOOT_1     = 9   # First boot: drivers + apps
    POST_REBOOT_2     = 10  # Second boot: cleanup, restore shell
    DONE              = 11

STEP_LABELS = {
    Step.IDLE:             "Chờ cấu hình",
    Step.DISK_SELECTED:    "Đã chọn ổ đĩa",
    Step.CONFIG_DONE:      "Đã cấu hình xong",
    Step.DRIVER_BACKUP:    "Đã sao lưu driver",
    Step.DISK_PARTITIONED: "Đã phân vùng ổ đĩa",
    Step.WIM_APPLIED:      "Đã áp dụng Windows image",
    Step.BOOTLOADER_SET:   "Đã cài bootloader",
    Step.UNATTEND_WRITTEN: "Đã tạo unattend.xml",
    Step.SHELL_REPLACED:   "Đang chờ reboot",
    Step.POST_REBOOT_1:    "Đang cài driver & ứng dụng",
    Step.POST_REBOOT_2:    "Đang dọn dẹp",
    Step.DONE:             "Hoàn tất",
}

class InstallState:
    def __init__(self):
        self.path = self._find_state_path()
        self.data: dict = {
            "version": 1,
            "step": Step.IDLE,
            "timestamp": 0,
            "config": {},
            "log": [],
        }

    def _find_state_path(self) -> Path:
        # Ưu tiên lưu trên ổ không phải C: (vì C: sẽ bị format)
        # Tìm ổ có đủ dung lượng
        for drive in "DEFGHIJKLMNOPQRSTUVWXYZ":
            p = Path(f"{drive}:\\{STATE_FILENAME}")
            try:
                p.parent.stat()
                return p
            except Exception:
                continue
        # Fallback về temp
        return Path(os.environ.get("TEMP", "C:\\Windows\\Temp")) / STATE_FILENAME

    def load(self) -> bool:
        """Đọc state từ file. Trả về True nếu có state đang dở."""
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            return self.data.get("step", Step.IDLE) not in (Step.IDLE, Step.DONE)
        except Exception:
            return False

    def save(self):
        try:
            self.data["timestamp"] = int(time.time())
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.log(f"[WARNING] Không lưu được state: {e}")

    def advance(self, step: Step, **kw):
        self.data["step"] = int(step)
        self.data.update(kw)
        self.log(f"→ {STEP_LABELS.get(step, step)}")
        self.save()

    def log(self, msg: str):
        entry = f"[{time.strftime('%H:%M:%S')}] {msg}"
        self.data.setdefault("log", []).append(entry)
        print(entry)

    def clear(self):
        self.data = {"version": 1, "step": Step.IDLE, "timestamp": 0, "config": {}, "log": []}
        try:
            self.path.unlink(missing_ok=True)
        except Exception:
            pass

    @property
    def step(self) -> Step:
        return Step(self.data.get("step", Step.IDLE))

    @property
    def config(self) -> dict:
        return self.data.setdefault("config", {})
