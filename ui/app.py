"""
TXA WinSetup — Main Application Window
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading, sys, os, ctypes, getpass
from pathlib import Path

from .theme import COLORS, FONTS, TAB_ITEMS
from .widgets import (
    TXAButton, TXACard, TXALabel, TXAEntry,
    TXATabBar, TXAProgressBar, TXADiskCard, TXAScrollableFrame, TXAPartitionCard
)

class TXAWinSetup(tk.Tk):
    def __init__(self, state, is_phase3: bool = False, is_winpe: bool = False, initial_iso: str = ""):
        super().__init__()
        self.state = state
        self.is_phase3 = is_phase3
        self.initial_iso = initial_iso
        from core.disk import is_winpe as detect_pe
        self.is_winpe = is_winpe or detect_pe()

        # ── Window setup ──
        self.title("TXA WinSetup — Cài Windows Tự Động")
        self.configure(bg=COLORS["bg_dark"])
        self.geometry("980x700")
        self.minsize(880, 600)
        self.resizable(True, True)

        # Căn giữa màn hình
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - 980) // 2)
        y = max(0, (sh - 700) // 2)
        self.geometry(f"980x700+{x}+{y}")

        # Nạp nhận diện Icon và Logo
        self._load_app_branding()
        self.after(50, self._load_app_branding)

        # Đăng ký đóng cửa sổ an toàn (tự động unmount toàn bộ ổ ảo & xóa taskbar progress)
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Khởi tạo thanh tác vụ (Windows Taskbar Progress)
        try:
            from core.taskbar import taskbar_progress
            taskbar_progress.set_default_hwnd(self.winfo_id())
        except Exception:
            pass

        # Trạng thái cấu hình & wizard
        self._current_tab = 0
        self._selected_iso = initial_iso if initial_iso else ""
        self._wim_path = ""
        self._wim_drive = ""
        self._wim_images = []
        self._selected_image_idx = 1
        self._img_var = tk.IntVar(value=1)

        self._selected_disk = None
        self._selected_partition = None
        self._disks = []
        self._disk_cards = {}
        self._partition_cards = {}
        self._bios_key = ""
        self._bios_edition = ""
        self._driver_backup_path = ""
        self._driver_auto_restore = tk.BooleanVar(value=True)

        # Tự động nạp tài nguyên từ các folder unattend, drivers, tweaks
        from core.resource_loader import (
            ensure_resource_folders,
            get_unattend_files,
            get_driver_packages,
            get_available_tweaks,
        )
        ensure_resource_folders()
        self._unattend_files = get_unattend_files()
        self._driver_packages = get_driver_packages()
        self._available_tweaks = get_available_tweaks()
        self._selected_unattend_idx = 0
        self._selected_driver_idx = 0
        self._tweak_vars = {}
        for tw in self._available_tweaks:
            self._tweak_vars[tw["id"]] = tk.BooleanVar(value=tw["default"])

        try:
            curr_user = getpass.getuser() or "User"
        except Exception:
            curr_user = "User"

        self._config = {
            # Tùy chọn người dùng & bảo mật
            "username": curr_user,
            "password": "",
            "computer_name": "TXA-PC",
            "product_key": "",
            "bypass_tpm": True,
            "skip_ms_account": True,
            "auto_logon": True,
            "regional_same": True,
            "disable_telemetry": True,
            "disable_bitlocker": True,
            "timezone": "SE Asia Standard Time",
            # Tinh chỉnh hệ điều hành TXA
            "classic_context_menu": True,
            "disable_hibernation": True,
            "disable_search_indexing": False,
            "high_performance_power": True,
            "auto_activate": True,
            # Tùy chọn cài đặt
            "boot_mode": "GPT",
            "quick_format": True,
            "auto_reboot": True,
        }
        self._install_running = False

        self._build_ui()

        # Load BIOS key và danh sách ổ đĩa nền
        self._load_bios_key()
        self._load_disks_background()

        if self._selected_iso:
            try:
                self._hdr_iso_lbl.config(text=Path(self._selected_iso).name[:30] + "...", fg=COLORS["success"])
                self.after(300, self._load_iso_info)
            except Exception:
                pass

        if is_phase3:
            self._go_phase3()
        else:
            if self.state.load():
                self._ask_resume()
            # Tự động kiểm tra bản cập nhật khi khởi động (nếu được bật)
            self.after(2500, self._auto_check_update_on_startup)

    # ── Giao diện chính ──────────────────────────────────────────────

    def _build_ui(self):
        # 1. Header TXA
        hdr = tk.Frame(self, bg=COLORS["bg_panel"], height=58)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        logo_frame = tk.Frame(hdr, bg=COLORS["bg_panel"])
        logo_frame.pack(side="left", padx=16)

        if hasattr(self, '_logo_small_img') and self._logo_small_img:
            tk.Label(logo_frame, image=self._logo_small_img, bg=COLORS["bg_panel"]).pack(side="left", padx=(0, 8))

        tk.Label(logo_frame, text="TXA", bg=COLORS["bg_panel"],
                 fg=COLORS["accent"], font=FONTS["logo"]).pack(side="left")
        tk.Label(logo_frame, text=" WinSetup", bg=COLORS["bg_panel"],
                 fg=COLORS["text_primary"], font=FONTS["heading"]).pack(side="left", pady=4)

        ver_frame = tk.Frame(hdr, bg=COLORS["bg_panel"])
        ver_frame.pack(side="left", padx=16, pady=8)
        tk.Label(ver_frame, text="v1.3 Auto", bg=COLORS["bg_panel"],
                 fg=COLORS["text_muted"], font=FONTS["small"]).pack(anchor="w")
        tk.Label(ver_frame, text="Bộ cài Windows Tự Động", bg=COLORS["bg_panel"],
                 fg=COLORS["text_secondary"], font=FONTS["small"]).pack(anchor="w")

        tk.Frame(hdr, width=1, bg=COLORS["border"]).pack(
            side="left", fill="y", padx=12, pady=10
        )

        # Status indicator
        self._status_dot = tk.Label(hdr, text="●", bg=COLORS["bg_panel"],
                                    fg=COLORS["success"], font=FONTS["body"])
        self._status_dot.pack(side="left")
        
        status_txt = "Môi trường: Windows PE (RAMDisk X:\\) — Đã mở khóa toàn bộ ổ đĩa" if self.is_winpe else "Sẵn sàng — Tự động chuyển WinPE nếu cài đè C:"
        self._status_lbl = tk.Label(hdr, text=status_txt, bg=COLORS["bg_panel"],
                                    fg=COLORS["success"] if self.is_winpe else COLORS["text_secondary"],
                                    font=FONTS["small"])
        self._status_lbl.pack(side="left", padx=4)

        # Quick summary on header right
        self._hdr_iso_lbl = tk.Label(hdr, text="Chưa chọn ISO", bg=COLORS["bg_panel"],
                                     fg=COLORS["text_muted"], font=FONTS["small"])
        self._hdr_iso_lbl.pack(side="right", padx=16)

        # Nút kiểm tra cập nhật từ GitHub Release latest.yml
        self._btn_check_update = tk.Button(
            hdr, text="⟳ Cập nhật",
            bg=COLORS["bg_card"], fg=COLORS["accent"],
            activebackground=COLORS["accent"], activeforeground=COLORS["bg_dark"],
            font=FONTS["small"], relief="flat", padx=8, pady=2, cursor="hand2",
            command=self._on_check_update_click
        )
        self._btn_check_update.pack(side="right", padx=8)

        # Divider line
        tk.Frame(self, bg=COLORS["accent"], height=2).pack(fill="x")

        # 2. Thanh Tabs TXA
        self._tab_bar = TXATabBar(
            self, TAB_ITEMS,
            on_change=self._switch_tab,
            current=0
        )
        self._tab_bar.pack(fill="x")

        tk.Frame(self, bg=COLORS["border"], height=1).pack(fill="x")

        # 3. Main content area
        self._content = tk.Frame(self, bg=COLORS["bg_dark"])
        self._content.pack(fill="both", expand=True, padx=16, pady=10)

        # 4. Bottom nav bar
        self._nav = tk.Frame(self, bg=COLORS["bg_panel"], height=60)
        self._nav.pack(fill="x", side="bottom")
        self._nav.pack_propagate(False)

        self._btn_prev_tab = TXAButton(
            self._nav, "← Tab trước",
            command=lambda: self._step_tab(-1), style="ghost",
            width=130, height=38
        )
        self._btn_prev_tab.pack(side="left", padx=16, pady=11)

        self._btn_next_tab = TXAButton(
            self._nav, "Tab tiếp →",
            command=lambda: self._step_tab(1), style="ghost",
            width=130, height=38
        )
        self._btn_next_tab.pack(side="left", padx=4, pady=11)

        tk.Label(self._nav, text="© 2026 TXA  •  txasoftdev@gmail.com",
                 bg=COLORS["bg_panel"], fg=COLORS["text_muted"],
                 font=FONTS["small"]).pack(side="left", padx=16)

        # Nút cài đặt tự động luôn sẵn sàng ở góc phải
        self._btn_auto_install = TXAButton(
            self._nav, "🚀 BẮT ĐẦU CÀI ĐẶT TỰ ĐỘNG",
            command=self._confirm_and_start, style="primary",
            width=260, height=38
        )
        self._btn_auto_install.pack(side="right", padx=16, pady=11)

        # Hiển thị Tab 0
        self._render_current_tab()

    def _set_status(self, msg: str, color: str = None):
        if hasattr(self, '_status_lbl'):
            self._status_lbl.config(text=msg)
        if color and hasattr(self, '_status_dot'):
            self._status_dot.config(fg=color)

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()

    def _switch_tab(self, idx: int):
        try:
            self._save_tab_inputs()
        except Exception:
            pass
        self._current_tab = idx
        self._render_current_tab()

    def _step_tab(self, delta: int):
        new_idx = self._current_tab + delta
        if 0 <= new_idx < len(TAB_ITEMS):
            self._tab_bar.set_current(new_idx)

    def _render_current_tab(self):
        self._clear_content()

        # Cập nhật trạng thái nút nav
        self._btn_prev_tab.config_state(self._current_tab == 0 or self._install_running)
        self._btn_next_tab.config_state(self._current_tab == len(TAB_ITEMS) - 1)

        builders = {
            0: self._build_tab_main_setup,
            1: self._build_tab_automation,
            2: self._build_tab_driver,
            3: self._build_tab_install,
        }
        builders.get(self._current_tab, self._build_tab_main_setup)()

    # ── TAB 0: Cài đặt chính (ISO + Ổ đĩa) ──────────────────────────

    def _build_tab_main_setup(self):
        container = TXAScrollableFrame(self._content, bg=COLORS["bg_dark"])
        container.pack(fill="both", expand=True)
        c = container.scrollable

        # --- Card 1: Bộ cài đặt Windows (ISO & WIM) ---
        iso_card = TXACard(c)
        iso_card.pack(fill="x", pady=(0, 10))

        header_row = tk.Frame(iso_card, bg=COLORS["bg_card"])
        header_row.pack(fill="x", pady=(0, 6))
        TXALabel(header_row, "1. Chọn File ISO Windows", style="heading",
                 bg=COLORS["bg_card"]).pack(side="left")
        TXALabel(header_row, " (Windows 10/11 chính thức)", style="secondary",
                 bg=COLORS["bg_card"]).pack(side="left", padx=6)

        if not self._selected_iso:
            drop = tk.Frame(iso_card, bg=COLORS["bg_input"],
                            highlightthickness=1,
                            highlightbackground=COLORS["border"],
                            cursor="hand2")
            drop.pack(fill="x", ipady=12, pady=4)
            drop.bind("<Button-1>", lambda _: self._browse_iso())

            tk.Label(drop, text="📁", bg=COLORS["bg_input"],
                     font=("Segoe UI Emoji", 24)).pack(pady=(4, 2))
            tk.Label(drop, text="Click để chọn file ISO Windows",
                     bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                     font=FONTS["subhead"]).pack()
            tk.Label(drop, text="Hỗ trợ file ISO / WIM mọi phiên bản",
                     bg=COLORS["bg_input"], fg=COLORS["text_muted"],
                     font=FONTS["small"]).pack(pady=(2, 6))

            TXAButton(iso_card, "Chọn file ISO...", self._browse_iso,
                      style="ghost", width=160, height=34).pack(anchor="w", pady=(6, 2))
        else:
            row_file = tk.Frame(iso_card, bg=COLORS["bg_card"])
            row_file.pack(fill="x", pady=4)
            name = Path(self._selected_iso).name
            TXALabel(row_file, f"✓  {name}", style="subhead",
                     color=COLORS["success"], bg=COLORS["bg_card"]).pack(side="left")
            TXAButton(row_file, "⏏️ Eject ổ ảo", self._eject_current_iso,
                      style="ghost", width=110, height=28).pack(side="right", padx=(6, 0))
            TXAButton(row_file, "Thay đổi ISO", self._browse_iso,
                      style="ghost", width=110, height=28).pack(side="right")

            self._iso_info_frame = tk.Frame(iso_card, bg=COLORS["bg_card"])
            self._iso_info_frame.pack(fill="x", pady=(8, 2))
            self._render_wim_editions_ui(self._iso_info_frame)

        # --- Card 2: Phân vùng đích cài đặt Windows ---
        disk_card = TXACard(c)
        disk_card.pack(fill="x", pady=6)

        d_hdr = tk.Frame(disk_card, bg=COLORS["bg_card"])
        d_hdr.pack(fill="x", pady=(0, 6))
        TXALabel(d_hdr, "2. Chọn Phân Vùng Cài Đặt Windows", style="heading",
                 bg=COLORS["bg_card"]).pack(side="left")
        TXALabel(d_hdr, "🛡️ BẢO TOÀN toàn bộ dữ liệu trên các phân vùng khác",
                 style="small", color=COLORS["success"], bg=COLORS["bg_card"]).pack(side="left", padx=10)

        TXAButton(d_hdr, "⟳ Làm mới", self._refresh_disks,
                  style="ghost", width=100, height=28).pack(side="right")

        # Danh sách phân vùng trực quan
        self._disk_list_frame = tk.Frame(disk_card, bg=COLORS["bg_card"])
        self._disk_list_frame.pack(fill="x", pady=4)
        self._render_disks_ui(self._disk_list_frame)

        # Tùy chọn cài đặt & format
        self._size_frame = tk.Frame(disk_card, bg=COLORS["bg_card"])
        self._size_frame.pack(fill="x", pady=(8, 4))
        self._render_size_controls_ui(self._size_frame)

    def _browse_iso(self):
        path = filedialog.askopenfilename(
            title="Chọn file cài đặt Windows (ISO, WIM, ESD)",
            filetypes=[
                ("File cài đặt Windows", "*.iso *.wim *.esd *.swm"),
                ("ISO Image", "*.iso *.ISO"),
                ("WIM/ESD Image", "*.wim *.esd *.swm"),
                ("All files", "*.*")
            ]
        )
        if path:
            if self._selected_iso and self._selected_iso != path and self._selected_iso.lower().endswith(".iso"):
                try:
                    from core.wim import unmount_iso
                    unmount_iso(self._selected_iso)
                except Exception:
                    pass
            self._selected_iso = path
            if hasattr(self, '_hdr_iso_lbl'):
                self._hdr_iso_lbl.config(text=Path(path).name[:30] + "...", fg=COLORS["success"])
            self._render_current_tab()
            self._load_iso_info()

    def _eject_current_iso(self):
        """Eject và gỡ mount ổ đĩa ảo ISO hiện tại."""
        if self._selected_iso:
            try:
                from core.wim import unmount_iso
                unmount_iso(self._selected_iso)
            except Exception:
                pass
            self._selected_iso = ""
            self._wim_path = ""
            self._wim_drive = ""
            self._wim_images = []
            if hasattr(self, '_hdr_iso_lbl'):
                self._hdr_iso_lbl.config(text="Chưa chọn ISO", fg=COLORS["text_muted"])
            self._render_current_tab()
            self._set_status("Đã eject ổ đĩa ảo ISO an toàn.", COLORS["success"])

    def _load_iso_info(self):
        self._set_status("Đang đọc nguồn cài đặt...", COLORS["warning"])
        self.update()

        def _worker():
            try:
                from core.wim import mount_iso, get_wim_path_from_drive, read_wim_images, unmount_iso
                ext = Path(self._selected_iso).suffix.lower()

                # Nếu là file WIM/ESD/SWM trực tiếp -> Đọc luôn, không cần mount!
                if ext in (".wim", ".esd", ".swm"):
                    wim_path = self._selected_iso
                    letter = ""
                else:
                    letter = mount_iso(self._selected_iso)
                    if not letter:
                        # Fallback kiểm tra các ổ đĩa hiện tại xem đã có sẵn install.wim/esd chưa
                        wim_path = None
                        for d in "CDEFGHIJKLMNOPQRSTUVWXYZ":
                            p = f"{d}:\\sources\\install.wim"
                            if Path(p).exists():
                                wim_path = p
                                letter = d
                                break
                            p = f"{d}:\\sources\\install.esd"
                            if Path(p).exists():
                                wim_path = p
                                letter = d
                                break
                        if not wim_path:
                            self.after(0, lambda: self._set_status("Không mount được file ISO. Vui lòng chọn trực tiếp file install.wim / install.esd!", COLORS["error"]))
                            return
                    else:
                        wim_path = get_wim_path_from_drive(letter)
                        if not wim_path:
                            unmount_iso(self._selected_iso)
                            self.after(0, lambda: self._set_status("Không tìm thấy install.wim trong ISO", COLORS["error"]))
                            return

                images = read_wim_images(wim_path)
                if not images:
                    self.after(0, lambda: self._set_status("Không thể đọc metadata phiên bản trong file ảnh!", COLORS["error"]))
                    return

                self._wim_path = wim_path
                self._wim_images = images
                self._wim_drive = letter

                # Chọn phiên bản đầu tiên hoặc bản Pro nếu có
                self._selected_image_idx = images[0].index
                for img in images:
                    if "pro" in img.name.lower():
                        self._selected_image_idx = img.index
                        break

                self.after(0, lambda: self._set_status(f"Đã nạp {len(images)} phiên bản ({Path(wim_path).name})", COLORS["success"]))
                self.after(0, self._render_current_tab)
            except Exception as e:
                self.after(0, lambda: self._set_status(f"Lỗi nạp file: {e}", COLORS["error"]))

        threading.Thread(target=_worker, daemon=True).start()

    def _render_wim_editions_ui(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        if not self._wim_images:
            TXALabel(parent, "⏳ Đang đọc danh sách các phiên bản Windows trong file cài đặt...",
                     style="secondary", bg=COLORS["bg_card"]).pack(anchor="w", pady=4)
            return

        hdr_row = tk.Frame(parent, bg=COLORS["bg_card"])
        hdr_row.pack(fill="x", pady=(0, 4))
        TXALabel(hdr_row, "Chọn phiên bản Windows muốn cài đặt:",
                 style="subhead", bg=COLORS["bg_card"]).pack(side="left")
        TXALabel(hdr_row, f"({len(self._wim_images)} phiên bản có sẵn)",
                 style="secondary", bg=COLORS["bg_card"]).pack(side="left", padx=8)

        # Dropdown Combobox chọn phiên bản
        combo_frame = tk.Frame(parent, bg=COLORS["bg_card"])
        combo_frame.pack(fill="x", pady=2)

        edition_items = [
            f"Index {img.index}: {img.name} ({img.size_gb} GB - {img.architecture})"
            for img in self._wim_images
        ]

        curr_idx = 0
        for i, img in enumerate(self._wim_images):
            if img.index == self._selected_image_idx:
                curr_idx = i
                break

        edition_combo = ttk.Combobox(
            combo_frame,
            values=edition_items,
            state="readonly",
            font=FONTS["body"],
            width=54
        )
        edition_combo.current(curr_idx)
        edition_combo.pack(side="left", fill="x", expand=True)

        detail_lbl = tk.Label(
            parent,
            text="",
            bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
            font=FONTS["small"],
            anchor="w"
        )
        detail_lbl.pack(fill="x", pady=(4, 0))

        def _on_edition_change(event=None):
            idx = edition_combo.current()
            if 0 <= idx < len(self._wim_images):
                sel_img = self._wim_images[idx]
                self._selected_image_idx = sel_img.index
                self._img_var.set(sel_img.index)
                desc = f" — {sel_img.description}" if sel_img.description else ""
                detail_lbl.config(
                    text=f"✓ Đã chọn: {sel_img.name} (Index {sel_img.index}) | Dung lượng giải nén: {sel_img.size_gb} GB | Kiến trúc: {sel_img.architecture}{desc}",
                    fg=COLORS["accent"]
                )

        edition_combo.bind("<<ComboboxSelected>>", _on_edition_change)
        _on_edition_change()

    def _auto_select_default_partition(self):
        """Tự động tìm và chọn phân vùng cài đặt Windows phù hợp nhất (ưu tiên phân vùng C:)."""
        if not self._disks:
            return
        # Ưu tiên 1: Phân vùng C: (hệ điều hành hiện tại)
        for d in self._disks:
            for p in d.partitions:
                if p.letter == "C" or p.is_system:
                    self._selected_disk = d
                    self._selected_partition = p
                    self._config["install_mode"] = "existing_partition"
                    self._config["target_partition_letter"] = "C"
                    return
        # Ưu tiên 2: Phân vùng NTFS có dung lượng >= 30 GB
        for d in self._disks:
            for p in d.partitions:
                if p.size_gb >= 30.0 and (p.fs or "").upper() == "NTFS":
                    self._selected_disk = d
                    self._selected_partition = p
                    self._config["install_mode"] = "existing_partition"
                    self._config["target_partition_letter"] = p.letter or f"Part {p.index}"
                    return
        # Ưu tiên 3: Phân vùng đầu tiên
        for d in self._disks:
            if d.partitions:
                self._selected_disk = d
                self._selected_partition = d.partitions[0]
                self._config["install_mode"] = "existing_partition"
                self._config["target_partition_letter"] = d.partitions[0].letter or f"Part {d.partitions[0].index}"
                return

    def _load_disks_background(self):
        def _worker():
            try:
                from core.disk import get_all_disks
                self._disks = get_all_disks()
                self._auto_select_default_partition()
                self.after(0, self._render_current_tab)
                self.after(0, lambda: self._set_status(f"Đã phát hiện {len(self._disks)} ổ đĩa", COLORS["success"]))
            except Exception as e:
                print(f"Lỗi quét ổ đĩa: {e}")
        threading.Thread(target=_worker, daemon=True).start()

    def _refresh_disks(self):
        self._set_status("Đang quét phân vùng và ổ đĩa...", COLORS["warning"])
        def _worker():
            from core.disk import get_all_disks
            self._disks = get_all_disks(force_refresh=True)
            self._auto_select_default_partition()
            self.after(0, self._render_current_tab)
            self.after(0, lambda: self._set_status(f"Tìm thấy {len(self._disks)} ổ đĩa", COLORS["success"]))
        threading.Thread(target=_worker, daemon=True).start()

    def _render_disks_ui(self, parent):
        for w in parent.winfo_children():
            w.destroy()
        self._partition_cards = {}

        if not self._disks:
            TXALabel(parent, "Đang quét danh sách phân vùng ổ đĩa...",
                     style="secondary", bg=COLORS["bg_card"]).pack(pady=10)
            return

        all_parts = []
        for disk in self._disks:
            for p in disk.partitions:
                all_parts.append((disk, p))

        if not all_parts:
            TXALabel(parent, "Không tìm thấy phân vùng nào trên các ổ đĩa.",
                     style="warning", bg=COLORS["bg_card"]).pack(pady=10)
            return

        if not self._selected_partition:
            self._auto_select_default_partition()

        for disk, p in all_parts:
            is_sel = (
                self._selected_partition is not None
                and self._selected_disk is not None
                and self._selected_disk.index == disk.index
                and (
                    (self._selected_partition.letter and self._selected_partition.letter == p.letter)
                    or (self._selected_partition.index == p.index)
                )
            )
            card = TXAPartitionCard(
                parent, disk, p,
                on_select=self._select_partition,
                selected=is_sel
            )
            card.pack(fill="x", pady=3)
            key = f"{disk.index}_{p.index}_{p.letter}"
            self._partition_cards[key] = card

    def _select_partition(self, disk, partition):
        self._selected_disk = disk
        self._selected_partition = partition
        self._config["install_mode"] = "existing_partition"
        self._config["target_partition_letter"] = partition.letter or "C"

        for k, card in self._partition_cards.items():
            is_this = (
                card.disk.index == disk.index and 
                (card.partition.letter == partition.letter if partition.letter else card.partition.index == partition.index)
            )
            card.set_selected(is_this)

        if hasattr(self, '_size_frame'):
            self._render_size_controls_ui(self._size_frame)

        p_name = f"ổ {partition.letter}:\\" if partition.letter else f"phân vùng {partition.index}"
        if (partition.is_system or partition.letter == "C" or disk.is_system_disk) and not self.is_winpe:
            self._set_status(f"Đã chọn {p_name} (Windows hiện tại - Tool sẽ tự động reboot để cài sạch an toàn)", COLORS["warning"])
        else:
            self._set_status(f"Đã chọn {p_name} ({partition.size_gb} GB) trên Disk {disk.index}", COLORS["success"])

    def _render_size_controls_ui(self, parent):
        for w in parent.winfo_children():
            w.destroy()

        if not self._selected_disk:
            TXALabel(parent, "Vui lòng click chọn 1 phân vùng ở trên để cài đặt Windows.",
                     style="muted", bg=COLORS["bg_card"]).pack(anchor="w", pady=4)
            return

        from core.disk import suggest_partition_layout, find_target_partition
        layout = suggest_partition_layout(self._selected_disk)

        tk.Frame(parent, bg=COLORS["border"], height=1).pack(fill="x", pady=(6, 8))

        target_ltr = self._selected_partition.letter if self._selected_partition and self._selected_partition.letter else self._config.get("target_partition_letter", "C")

        if (self._selected_disk.is_system_disk or target_ltr == "C") and not self.is_winpe:
            warn_box = tk.Frame(parent, bg="#2A1E05", highlightthickness=1, highlightbackground=COLORS["warning"])
            warn_box.pack(fill="x", pady=(2, 8), padx=2)
            tk.Label(warn_box, text=" ⚠️ PHÂN VÙNG ĐANG CHẠY WINDOWS: ", bg="#2A1E05", fg=COLORS["warning"], font=FONTS["subhead"]).pack(side="left", padx=6, pady=4)
            tk.Label(warn_box, text=f"Phân vùng {target_ltr}: đang chạy Windows. Tool sẽ chuẩn bị môi trường và tự động khởi động lại máy để cài đặt sạch.",
                     bg="#2A1E05", fg=COLORS["text_primary"], font=FONTS["small"]).pack(side="left", pady=4)

        # ── Chọn chế độ cài đặt ──
        mode_box = tk.Frame(parent, bg=COLORS["bg_card"])
        mode_box.pack(fill="x", pady=(0, 8))
        TXALabel(mode_box, "Tùy chọn cài đặt & bảo vệ dữ liệu:", style="subhead", bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 4))

        if not hasattr(self, '_var_install_mode'):
            self._var_install_mode = tk.StringVar(value=self._config.get("install_mode", "existing_partition"))

        rb_m_style = {
            "bg": COLORS["bg_card"], "fg": COLORS["text_primary"],
            "selectcolor": COLORS["bg_input"], "activebackground": COLORS["bg_card"],
            "font": FONTS["body"]
        }

        row_modes = tk.Frame(mode_box, bg=COLORS["bg_card"])
        row_modes.pack(fill="x", pady=2)

        tk.Radiobutton(
            row_modes,
            text=f"🛡️ Cài vào phân vùng {target_ltr}: (Format phân vùng này, BẢO TOÀN các phân vùng khác)",
            variable=self._var_install_mode, value="existing_partition",
            command=lambda: self._render_size_controls_ui(parent),
            **rb_m_style
        ).pack(side="left", padx=(0, 16))

        tk.Radiobutton(
            row_modes,
            text=f"⚡ Xóa sạch toàn bộ Disk {self._selected_disk.index} ({self._selected_disk.model}) & chia lại từ đầu",
            variable=self._var_install_mode, value="clean_disk",
            command=lambda: self._render_size_controls_ui(parent),
            **rb_m_style
        ).pack(side="left")

        current_mode = self._var_install_mode.get()
        self._config["install_mode"] = current_mode

        if current_mode == "existing_partition":
            # --- CHẾ ĐỘ 1: Cài vào phân vùng đã chọn ---
            part_box = tk.Frame(parent, bg=COLORS["bg_input"], padx=12, pady=10,
                                highlightthickness=1, highlightbackground=COLORS["border"])
            part_box.pack(fill="x", pady=(4, 8))

            p_desc = f"Phân vùng đích: {target_ltr}:"
            if self._selected_partition:
                lbl = f" [{self._selected_partition.label}]" if self._selected_partition.label else ""
                p_desc += f" — Dung lượng: {self._selected_partition.size_gb} GB ({self._selected_partition.fs or 'NTFS'}){lbl}"

            TXALabel(part_box, f"✓ {p_desc}", style="subhead",
                     color=COLORS["accent"], bg=COLORS["bg_input"]).pack(anchor="w", pady=(0, 6))

            if not hasattr(self, '_var_quick_format'):
                self._var_quick_format = tk.BooleanVar(value=self._config.get("quick_format", True))

            chk_fmt = tk.Checkbutton(
                part_box,
                text=f"Format nhanh phân vùng {target_ltr}: sang NTFS (Khuyến nghị: Xóa sạch Windows cũ để máy chạy mượt như mới)",
                variable=self._var_quick_format,
                bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                selectcolor=COLORS["bg_panel"], activebackground=COLORS["bg_input"],
                font=FONTS["body"], cursor="hand2"
            )
            chk_fmt.pack(anchor="w", pady=2)
            self._config["quick_format"] = self._var_quick_format.get()
            self._config["target_partition_letter"] = target_ltr
        else:
            # --- CHẾ ĐỘ 2: Phân chia lại toàn bộ ổ đĩa ---
            TXALabel(parent, "Sơ đồ phân vùng ổ đĩa dự kiến sau khi format sạch:",
                     style="subhead", bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 4))

            part_bar = tk.Frame(parent, bg="#111827", height=32, highlightthickness=1, highlightbackground=COLORS["border"])
            part_bar.pack(fill="x", pady=(2, 8))
            part_bar.pack_propagate(False)

            esp_f = tk.Frame(part_bar, bg="#0284c7")
            esp_f.pack(side="left", fill="y", padx=1)
            tk.Label(esp_f, text=" ESP (300 MB) ", bg="#0284c7", fg="#ffffff", font=FONTS["small"]).pack(side="left")

            win_f = tk.Frame(part_bar, bg="#16a34a")
            win_f.pack(side="left", fill="both", expand=True, padx=1)
            self._visual_c_lbl = tk.Label(win_f, text=f" C: Windows ({self._config.get('c_gb', layout['c_gb'])} GB - NTFS) ",
                                          bg="#16a34a", fg="#ffffff", font=FONTS["subhead"])
            self._visual_c_lbl.pack(fill="both", expand=True)

            data_f = tk.Frame(part_bar, bg="#7c3aed")
            data_f.pack(side="left", fill="both", expand=True, padx=1)
            self._visual_data_lbl = tk.Label(data_f, text=f" DATA ({self._config.get('data_gb', layout['data_gb'])} GB - NTFS) ",
                                             bg="#7c3aed", fg="#ffffff", font=FONTS["subhead"])
            self._visual_data_lbl.pack(fill="both", expand=True)

            row = tk.Frame(parent, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=4)

            TXALabel(row, "Ổ C: (Windows)  ", style="body", bg=COLORS["bg_card"]).pack(side="left")
            c_val = str(self._config.get("c_gb", layout["c_gb"]))
            self._c_entry = TXAEntry(row, width=6)
            self._c_entry.insert(0, c_val)
            self._c_entry.pack(side="left")
            TXALabel(row, "  GB       ", style="secondary", bg=COLORS["bg_card"]).pack(side="left")

            TXALabel(row, "Ổ DATA (Dữ liệu):  ", style="body", bg=COLORS["bg_card"]).pack(side="left")
            data_val = str(self._config.get("data_gb", layout["data_gb"]))
            self._data_entry = TXAEntry(row, width=6)
            self._data_entry.insert(0, data_val)
            self._data_entry.pack(side="left")
            TXALabel(row, "  GB", style="secondary", bg=COLORS["bg_card"]).pack(side="left")

            def _update_visual(*args):
                try:
                    cg = int(self._c_entry.get().strip() or "60")
                    dg = int(self._data_entry.get().strip() or "0")
                    self._visual_c_lbl.config(text=f" C: Windows ({cg} GB - NTFS) ")
                    self._visual_data_lbl.config(text=f" DATA ({dg} GB - NTFS) ")
                    self._config["c_gb"] = cg
                    self._config["data_gb"] = dg
                except Exception:
                    pass
            self._c_entry.bind("<KeyRelease>", _update_visual)
            self._data_entry.bind("<KeyRelease>", _update_visual)

        # Tùy chọn format & reboot
        opt_row = tk.Frame(parent, bg=COLORS["bg_card"])
        opt_row.pack(fill="x", pady=(8, 2))

        cb_opt_style = {
            "bg": COLORS["bg_card"], "fg": COLORS["text_primary"],
            "selectcolor": COLORS["bg_input"], "activebackground": COLORS["bg_card"],
            "font": FONTS["small"]
        }

        self._var_quick_format = tk.BooleanVar(value=self._config.get("quick_format", True))
        self._var_auto_reboot = tk.BooleanVar(value=self._config.get("auto_reboot", True))

        tk.Checkbutton(opt_row, text="  Format nhanh phân vùng cài đặt (Quick Format NTFS)",
                       variable=self._var_quick_format, **cb_opt_style).pack(side="left", padx=(0, 16))
        tk.Checkbutton(opt_row, text="  Tự động khởi động lại sau khi cài đặt hoàn tất (Auto Reboot)",
                       variable=self._var_auto_reboot, **cb_opt_style).pack(side="left")

        boot_scheme_str = "GPT (Chuẩn UEFI)" if self._selected_disk.is_gpt else "MBR (Chuẩn BIOS Legacy)"
        TXALabel(parent,
                 f"Tổng dung lượng: {layout['total_gb']} GB  •  Chuẩn ổ đĩa: {boot_scheme_str}",
                 style="muted", bg=COLORS["bg_card"]).pack(anchor="w", pady=(4, 0))

    # ── TAB 1: Tự động hóa & Cấu hình Hệ thống ────────────

    def _build_tab_automation(self):
        container = TXAScrollableFrame(self._content, bg=COLORS["bg_dark"])
        container.pack(fill="both", expand=True)
        c = container.scrollable

        cb_style = {
            "bg": COLORS["bg_card"], "fg": COLORS["text_primary"],
            "selectcolor": COLORS["bg_input"], "activebackground": COLORS["bg_card"],
            "font": FONTS["body"]
        }

        # ── Card 1: Trải nghiệm Người dùng (User Experience) ──
        card_ux = TXACard(c)
        card_ux.pack(fill="x", pady=(0, 10))

        hdr_rf = tk.Frame(card_ux, bg=COLORS["bg_card"])
        hdr_rf.pack(fill="x", pady=(0, 6))
        TXALabel(hdr_rf, "1. Trải nghiệm Người dùng & Cài đặt Tự động (OOBE & Unattend)",
                 style="heading", bg=COLORS["bg_card"]).pack(side="left")
        tk.Label(hdr_rf, text=" TXA AUTO UNATTEND ", bg="#0284c7", fg="#ffffff",
                 font=("Segoe UI", 8, "bold"), padx=6, pady=1).pack(side="left", padx=8)

        # Dropdown nạp file Unattend XML tự động từ folder unattend/
        box_unattend = tk.Frame(card_ux, bg=COLORS["bg_input"], highlightthickness=1, highlightbackground=COLORS["border"])
        box_unattend.pack(fill="x", padx=4, pady=(2, 10))

        h_u = tk.Frame(box_unattend, bg=COLORS["bg_input"])
        h_u.pack(fill="x", padx=10, pady=(6, 2))
        TXALabel(h_u, "File Cấu hình Cài đặt Tự động (Unattend XML):", style="subhead", bg=COLORS["bg_input"]).pack(side="left")

        def _open_unattend_dir():
            from core.resource_loader import get_base_dir
            d = get_base_dir() / "unattend"
            d.mkdir(parents=True, exist_ok=True)
            os.startfile(str(d))

        def _reload_unattend():
            from core.resource_loader import get_unattend_files
            self._unattend_files = get_unattend_files()
            self._render_current_tab()

        TXAButton(h_u, "⟳ Quét lại", _reload_unattend, style="ghost", width=80, height=26).pack(side="right", padx=(4, 0))
        TXAButton(h_u, "📂 Mở folder unattend", _open_unattend_dir, style="ghost", width=155, height=26).pack(side="right")

        r_cb_u = tk.Frame(box_unattend, bg=COLORS["bg_input"])
        r_cb_u.pack(fill="x", padx=10, pady=(2, 6))

        unattend_labels = [u["name"] for u in self._unattend_files]
        self._cb_unattend = ttk.Combobox(
            r_cb_u, values=unattend_labels, state="readonly",
            font=FONTS["body"], width=58
        )
        if self._selected_unattend_idx < len(unattend_labels):
            self._cb_unattend.current(self._selected_unattend_idx)
        self._cb_unattend.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def _on_unattend_changed(evt=None):
            self._selected_unattend_idx = self._cb_unattend.current()
            if 0 <= self._selected_unattend_idx < len(self._unattend_files):
                sel_u = self._unattend_files[self._selected_unattend_idx]
                self._config["custom_unattend_path"] = sel_u["path"]

        self._cb_unattend.bind("<<ComboboxSelected>>", _on_unattend_changed)

        TXALabel(card_ux, "Tùy biến OOBE, vượt rào phần cứng và thiết lập tài khoản tự động:",
                 style="secondary", bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        # Checkbox 1: Bypass TPM & SecureBoot
        self._var_bypass_tpm = tk.BooleanVar(value=self._config.get("bypass_tpm", True))
        tk.Checkbutton(card_ux, text="  Bỏ qua yêu cầu TPM 2.0, Secure Boot, RAM 4GB và CPU (Cài mượt Windows 11 máy cũ)",
                       variable=self._var_bypass_tpm, **cb_style).pack(anchor="w", pady=3)

        # Checkbox 2: Bypass MSA
        self._var_skip_ms = tk.BooleanVar(value=self._config.get("skip_ms_account", True))
        tk.Checkbutton(card_ux, text="  Bỏ qua yêu cầu tài khoản Microsoft (OOBE BypassNRO — Dùng tài khoản cục bộ)",
                       variable=self._var_skip_ms, **cb_style).pack(anchor="w", pady=3)

        # Khung tài khoản cục bộ
        user_box = tk.Frame(card_ux, bg=COLORS["bg_input"], highlightthickness=1, highlightbackground=COLORS["border"])
        user_box.pack(fill="x", padx=24, pady=6)

        r_u1 = tk.Frame(user_box, bg=COLORS["bg_input"])
        r_u1.pack(fill="x", padx=10, pady=(6, 3))
        TXALabel(r_u1, "Tên tài khoản (Username): ", style="body", bg=COLORS["bg_input"]).pack(side="left")
        self._username_e = TXAEntry(r_u1, placeholder="User", width=18)
        self._username_e.insert(0, self._config.get("username", "User"))
        self._username_e.pack(side="left", padx=6)

        def _fill_curr_user():
            import getpass
            try:
                name = getpass.getuser() or "User"
            except Exception:
                name = "User"
            self._username_e.delete(0, "end")
            self._username_e.insert(0, name)

        TXAButton(r_u1, "📋 Lấy tên máy hiện tại", _fill_curr_user,
                  style="ghost", width=150, height=28).pack(side="left", padx=4)

        r_u2 = tk.Frame(user_box, bg=COLORS["bg_input"])
        r_u2.pack(fill="x", padx=10, pady=(3, 6))
        TXALabel(r_u2, "Mật khẩu (Password):       ", style="body", bg=COLORS["bg_input"]).pack(side="left")
        self._password_e = TXAEntry(r_u2, placeholder="Để trống = Không có mật khẩu", width=26)
        self._password_e.insert(0, self._config.get("password", ""))
        self._password_e.pack(side="left", padx=6)

        self._var_autologon = tk.BooleanVar(value=self._config.get("auto_logon", True))
        tk.Checkbutton(user_box, text="  Tự động đăng nhập vào Windows không cần nhập mật khẩu (Autologon)",
                       variable=self._var_autologon,
                       bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["bg_card"], activebackground=COLORS["bg_input"],
                       font=FONTS["small"]).pack(anchor="w", padx=10, pady=(0, 6))

        # Checkbox 3: Regional options
        self._var_regional = tk.BooleanVar(value=self._config.get("regional_same", True))
        tk.Checkbutton(card_ux, text="  Đồng bộ cài đặt múi giờ & vùng giống máy hiện tại (SE Asia UTC+7 Việt Nam)",
                       variable=self._var_regional, **cb_style).pack(anchor="w", pady=3)

        # Checkbox 4: Disable Telemetry
        self._var_telemetry = tk.BooleanVar(value=self._config.get("disable_telemetry", True))
        tk.Checkbutton(card_ux, text="  Tắt thu thập dữ liệu chẩn đoán & bỏ qua toàn bộ câu hỏi riêng tư (Disable Telemetry)",
                       variable=self._var_telemetry, **cb_style).pack(anchor="w", pady=3)

        # Checkbox 5: Disable BitLocker
        self._var_bitlocker = tk.BooleanVar(value=self._config.get("disable_bitlocker", True))
        tk.Checkbutton(card_ux, text="  Tắt tự động mã hóa ổ đĩa BitLocker (Tránh rủi ro bị khóa BitLocker ngoài ý muốn)",
                       variable=self._var_bitlocker, **cb_style).pack(anchor="w", pady=3)

        # ── Card 2: Tinh chỉnh Hệ thống (System Tweaks từ folder tweaks/) ──
        card_tweaks = TXACard(c)
        card_tweaks.pack(fill="x", pady=6)

        hdr_wn = tk.Frame(card_tweaks, bg=COLORS["bg_card"])
        hdr_wn.pack(fill="x", pady=(0, 6))
        TXALabel(hdr_wn, "2. Tinh chỉnh Hệ thống Tự động (System Registry Tweaks)",
                 style="heading", bg=COLORS["bg_card"]).pack(side="left")
        tk.Label(hdr_wn, text=" TỰ ĐỘNG NẠP TWEAKS ", bg="#16a34a", fg="#ffffff",
                 font=("Segoe UI", 8, "bold"), padx=6, pady=1).pack(side="left", padx=8)

        def _open_tweaks_dir():
            from core.resource_loader import get_base_dir
            d = get_base_dir() / "tweaks"
            d.mkdir(parents=True, exist_ok=True)
            os.startfile(str(d))

        def _reload_tweaks():
            from core.resource_loader import get_available_tweaks
            self._available_tweaks = get_available_tweaks()
            for tw in self._available_tweaks:
                if tw["id"] not in self._tweak_vars:
                    self._tweak_vars[tw["id"]] = tk.BooleanVar(value=tw["default"])
            self._render_current_tab()

        TXAButton(hdr_wn, "⟳ Tải lại", _reload_tweaks, style="ghost", width=80, height=26).pack(side="right", padx=(4, 0))
        TXAButton(hdr_wn, "📂 Mở folder tweaks", _open_tweaks_dir, style="ghost", width=140, height=26).pack(side="right")

        TXALabel(card_tweaks, f"Đã quét và tải {len(self._available_tweaks)} file tinh chỉnh .reg từ folder tweaks/ (Tích chọn để tự động áp dụng sau khi cài):",
                 style="secondary", bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        # Hiển thị danh sách Checkboxes được quét động từ folder tweaks/
        tweaks_box = tk.Frame(card_tweaks, bg=COLORS["bg_card"])
        tweaks_box.pack(fill="x", pady=2)

        for tw in self._available_tweaks:
            tid = tw["id"]
            if tid not in self._tweak_vars:
                self._tweak_vars[tid] = tk.BooleanVar(value=tw["default"])
            var = self._tweak_vars[tid]

            r_tw = tk.Frame(tweaks_box, bg=COLORS["bg_card"])
            r_tw.pack(fill="x", pady=2)
            tk.Checkbutton(
                r_tw, text=f"  {tw['title']}",
                variable=var, **cb_style
            ).pack(side="left")
            tk.Label(r_tw, text=f"({tw['desc']})", bg=COLORS["bg_card"],
                     fg=COLORS["text_muted"], font=FONTS["small"]).pack(side="left", padx=4)

        # Các tùy chọn bổ sung
        r_extra = tk.Frame(card_tweaks, bg=COLORS["bg_input"], highlightthickness=1, highlightbackground=COLORS["border"])
        r_extra.pack(fill="x", pady=(8, 2), padx=2)
        self._var_activate = tk.BooleanVar(value=self._config.get("auto_activate", True))
        tk.Checkbutton(r_extra, text="  Tự động kích hoạt bản quyền từ BIOS OEM hoặc Digital License nếu có",
                       variable=self._var_activate,
                       bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["bg_card"], activebackground=COLORS["bg_input"],
                       font=FONTS["body"]).pack(anchor="w", padx=6, pady=4)

        # ── Card 3: Thông tin Thiết bị & Bản quyền ──
        card_pc = TXACard(c)
        card_pc.pack(fill="x", pady=6)

        TXALabel(card_pc, "3. Tên Máy tính & Khóa Bản quyền (Device & License Key)",
                 style="heading", bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        r_pc = tk.Frame(card_pc, bg=COLORS["bg_card"])
        r_pc.pack(fill="x", pady=4)
        TXALabel(r_pc, "Tên máy tính (PC Name): ", style="body", bg=COLORS["bg_card"]).pack(side="left")
        self._pcname_e = TXAEntry(r_pc, placeholder="TXA-PC", width=22)
        self._pcname_e.insert(0, self._config.get("computer_name", "TXA-PC"))
        self._pcname_e.pack(side="left", padx=6)

        r_key = tk.Frame(card_pc, bg=COLORS["bg_card"])
        r_key.pack(fill="x", pady=4)
        TXALabel(r_key, "Product Key bản quyền:  ", style="body", bg=COLORS["bg_card"]).pack(side="left")
        self._key_e = TXAEntry(r_key, placeholder="Để trống hoặc trích tự động từ BIOS...", width=32)
        key_val = self._config.get("product_key", "") or self._bios_key
        if key_val:
            self._key_e.insert(0, key_val)
        self._key_e.pack(side="left", padx=6)

        if self._bios_key:
            tk.Label(r_key, text=f"✓ Đã phát hiện BIOS OEM ({self._bios_edition})",
                     bg="#064e3b", fg="#34d399", font=FONTS["small"], padx=6, pady=2).pack(side="left", padx=6)

    def _load_bios_key(self):
        def _worker():
            try:
                from core.bios import get_bios_key, get_key_edition
                key = get_bios_key()
                self._bios_key = key
                if key:
                    edition = get_key_edition(key)
                    self._bios_edition = edition
                    self._config["product_key"] = key
                    self.after(0, lambda: self._set_status(f"BIOS Key: ...{key[-8:]} ({edition})", COLORS["success"]))
            except Exception as e:
                print(f"Lỗi đọc BIOS key: {e}")
        threading.Thread(target=_worker, daemon=True).start()

    # ── TAB 2: Sao lưu & Khôi phục Driver ─────────────────────────

    def _build_tab_driver(self):
        container = TXAScrollableFrame(self._content, bg=COLORS["bg_dark"])
        container.pack(fill="both", expand=True)
        c = container.scrollable

        from core.driver_backup import get_backup_default_path
        if not self._driver_backup_path:
            self._driver_backup_path = get_backup_default_path()

        # ── Card 1: Sao lưu Driver từ máy hiện tại ──
        card_bk = TXACard(c)
        card_bk.pack(fill="x", pady=(0, 10))

        h1 = tk.Frame(card_bk, bg=COLORS["bg_card"])
        h1.pack(fill="x", pady=(0, 4))
        TXALabel(h1, "1. Sao lưu Driver từ Windows hiện tại (Export)", style="heading", bg=COLORS["bg_card"]).pack(side="left")
        tk.Label(h1, text=" TỰ ĐỘNG TRÍCH XUẤT ", bg="#0284c7", fg="#ffffff",
                 font=("Segoe UI", 8, "bold"), padx=6, pady=1).pack(side="left", padx=8)

        TXALabel(card_bk, "Trích xuất toàn bộ driver đang hoạt động (Wifi, LAN, Audio, GPU, Touchpad...) lưu vào ổ đĩa an toàn.",
                 style="secondary", bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        r1 = tk.Frame(card_bk, bg=COLORS["bg_card"])
        r1.pack(fill="x", pady=4)
        TXALabel(r1, "Thư mục lưu Driver: ", style="body", bg=COLORS["bg_card"]).pack(side="left")
        self._driver_path_e = TXAEntry(r1, width=38)
        self._driver_path_e.insert(0, self._driver_backup_path)
        self._driver_path_e.pack(side="left", padx=8)

        TXAButton(r1, "Browse...", self._browse_driver_path,
                  style="ghost", width=90, height=30).pack(side="left")

        self._driver_status_lbl = TXALabel(card_bk, "", style="secondary", bg=COLORS["bg_card"])
        self._driver_status_lbl.pack(anchor="w", pady=2)

        b_row = tk.Frame(card_bk, bg=COLORS["bg_card"])
        b_row.pack(anchor="w", pady=(6, 4))
        TXAButton(b_row, "▶ Bắt đầu sao lưu ngay", self._do_backup_driver,
                  style="primary", width=190, height=36).pack(side="left")

        # ── Card 2: Khôi phục Driver vào hệ điều hành ──
        card_rs = TXACard(c)
        card_rs.pack(fill="x", pady=(0, 10))

        h2 = tk.Frame(card_rs, bg=COLORS["bg_card"])
        h2.pack(fill="x", pady=(0, 4))
        TXALabel(h2, "2. Khôi phục Driver vào Windows (Restore & Inject)", style="heading", bg=COLORS["bg_card"]).pack(side="left")
        tk.Label(h2, text=" DISM OFFLINE + ONLINE ", bg="#16a34a", fg="#ffffff",
                 font=("Segoe UI", 8, "bold"), padx=6, pady=1).pack(side="left", padx=8)

        TXALabel(card_rs, "Hai phương thức khôi phục Driver linh hoạt:",
                 style="secondary", bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        # Tùy chọn A: Tự động khôi phục khi cài Windows mới
        box_auto = tk.Frame(card_rs, bg=COLORS["bg_input"], highlightthickness=1, highlightbackground=COLORS["border"])
        box_auto.pack(fill="x", pady=4, padx=4)

        # Dropdown nạp gói Driver từ folder drivers/
        h_d = tk.Frame(box_auto, bg=COLORS["bg_input"])
        h_d.pack(fill="x", padx=10, pady=(6, 2))
        TXALabel(h_d, "Gói Driver nguồn (Nạp từ folder drivers/ hoặc sao lưu từ máy này):", style="subhead", bg=COLORS["bg_input"]).pack(side="left")

        def _open_drivers_dir():
            from core.resource_loader import get_base_dir
            d = get_base_dir() / "drivers"
            d.mkdir(parents=True, exist_ok=True)
            os.startfile(str(d))

        def _reload_drivers():
            from core.resource_loader import get_driver_packages
            self._driver_packages = get_driver_packages()
            self._render_current_tab()

        TXAButton(h_d, "⟳ Quét lại", _reload_drivers, style="ghost", width=80, height=26).pack(side="right", padx=(4, 0))
        TXAButton(h_d, "📂 Mở folder drivers", _open_drivers_dir, style="ghost", width=150, height=26).pack(side="right")

        r_cb_d = tk.Frame(box_auto, bg=COLORS["bg_input"])
        r_cb_d.pack(fill="x", padx=10, pady=(2, 6))

        driver_labels = [d["name"] for d in self._driver_packages]
        self._cb_driver = ttk.Combobox(
            r_cb_d, values=driver_labels, state="readonly",
            font=FONTS["body"], width=58
        )
        if self._selected_driver_idx < len(driver_labels):
            self._cb_driver.current(self._selected_driver_idx)
        self._cb_driver.pack(side="left", fill="x", expand=True, padx=(0, 6))

        def _on_driver_changed(evt=None):
            self._selected_driver_idx = self._cb_driver.current()
            if 0 <= self._selected_driver_idx < len(self._driver_packages):
                sel_d = self._driver_packages[self._selected_driver_idx]
                if sel_d["path"]:
                    self._driver_backup_path = sel_d["path"]
                    self._driver_path_e.delete(0, "end")
                    self._driver_path_e.insert(0, sel_d["path"])

        self._cb_driver.bind("<<ComboboxSelected>>", _on_driver_changed)

        tk.Checkbutton(
            box_auto,
            text="  ⚡ Tự động nạp trực tiếp toàn bộ Driver này vào Windows mới khi bung cài đặt",
            variable=self._driver_auto_restore,
            bg=COLORS["bg_input"], fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_card"], activebackground=COLORS["bg_input"],
            font=FONTS["body"]
        ).pack(anchor="w", padx=8, pady=(6, 2))

        TXALabel(box_auto,
                 "   • Hệ thống sẽ dùng DISM nạp sẵn Driver vào Windows mới ngay trước khi khởi động lại.\n"
                 "   • Máy tính khởi động lên lần đầu là có sẵn Wifi, Touchpad, âm thanh không lo thiếu mạng.",
                 style="muted", bg=COLORS["bg_input"]).pack(anchor="w", padx=16, pady=(0, 6))

        # Tùy chọn B: Khôi phục ngay vào máy hiện tại
        box_manual = tk.Frame(card_rs, bg=COLORS["bg_card"])
        box_manual.pack(fill="x", pady=(10, 4))

        TXALabel(box_manual, "Hoặc khôi phục / cài đặt ngay lập tức vào máy tính hiện tại:",
                 style="body", bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 4))

        r2 = tk.Frame(box_manual, bg=COLORS["bg_card"])
        r2.pack(fill="x", pady=4)

        TXAButton(r2, "⚡ Khôi phục Driver ngay vào máy này", self._do_restore_driver_now,
                  style="ghost", width=270, height=36).pack(side="left")

        self._restore_status_lbl = TXALabel(card_rs, "", style="secondary", bg=COLORS["bg_card"])
        self._restore_status_lbl.pack(anchor="w", pady=(4, 0))

    def _browse_driver_path(self):
        path = filedialog.askdirectory(title="Chọn thư mục lưu Driver")
        if path:
            self._driver_backup_path = path
            self._driver_path_e.delete(0, "end")
            self._driver_path_e.insert(0, path)

    def _do_backup_driver(self):
        path = self._driver_path_e.get().strip()
        if not path:
            messagebox.showwarning("Cảnh báo", "Vui lòng chỉ định thư mục lưu driver!")
            return
        self._driver_backup_path = path
        self._driver_status_lbl.config(text="⏳ Đang quét và trích xuất driver từ hệ thống, vui lòng chờ...", fg=COLORS["warning"])
        self.update()

        def _worker():
            from core.driver_backup import backup_drivers
            ok, msg = backup_drivers(path)
            color = COLORS["success"] if ok else COLORS["error"]
            self.after(0, lambda: self._driver_status_lbl.config(text=f"{'✓' if ok else '❌'} {msg}", fg=color))
            self.after(0, lambda: self._set_status(msg, color))
        threading.Thread(target=_worker, daemon=True).start()

    def _do_restore_driver_now(self):
        path = self._driver_path_e.get().strip()
        if not path or not Path(path).exists():
            path = filedialog.askdirectory(title="Chọn thư mục driver cần khôi phục")
            if not path:
                return
            self._driver_backup_path = path
            self._driver_path_e.delete(0, "end")
            self._driver_path_e.insert(0, path)

        confirm = messagebox.askyesno(
            "Xác nhận cài Driver",
            f"Bạn có muốn quét và cài đặt toàn bộ driver từ thư mục sau vào máy tính này không?\n\n{path}"
        )
        if not confirm:
            return

        self._restore_status_lbl.config(text="⏳ Đang nạp và cài đặt driver vào Windows bằng DISM...", fg=COLORS["warning"])
        self.update()

        def _worker():
            from core.driver_backup import restore_drivers
            ok, msg = restore_drivers(path)
            color = COLORS["success"] if ok else COLORS["error"]
            self.after(0, lambda: self._restore_status_lbl.config(text=f"{'✓' if ok else '❌'} {msg}", fg=color))
            self.after(0, lambda: self._set_status(f"Khôi phục driver: {msg}", color))
        threading.Thread(target=_worker, daemon=True).start()

    # ── TAB 3: Tiến trình & Log ────────────────────────────────────

    def _build_tab_install(self):
        c = self._content

        # Summary box
        sum_card = TXACard(c)
        sum_card.pack(fill="x", pady=(0, 8))

        s_hdr = tk.Frame(sum_card, bg=COLORS["bg_card"])
        s_hdr.pack(fill="x")
        TXALabel(s_hdr, "Tóm tắt cấu hình cài đặt tự động", style="heading", bg=COLORS["bg_card"]).pack(side="left")

        # Details
        iso_name = Path(self._selected_iso).name if self._selected_iso else "Chưa chọn file ISO"
        disk_name = f"Disk {self._selected_disk.index} ({self._selected_disk.model})" if self._selected_disk else "Chưa chọn ổ đĩa"
        c_gb = self._config.get("c_gb", "Mặc định")

        info_txt = f"• Bộ cài: {iso_name}   •   Đích: {disk_name} (C: {c_gb} GB)   •   User: {self._config.get('username', 'User')}"
        TXALabel(sum_card, info_txt, style="small", color=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(4, 0))

        # Progress bar
        p_frame = tk.Frame(c, bg=COLORS["bg_dark"])
        p_frame.pack(fill="x", pady=6)

        self._prog_bar = TXAProgressBar(p_frame, height=8)
        self._prog_bar.pack(fill="x", pady=(2, 2))

        p_row = tk.Frame(p_frame, bg=COLORS["bg_dark"])
        p_row.pack(fill="x", pady=(2, 0))
        self._prog_msg = TXALabel(p_row, "Sẵn sàng cài đặt", style="secondary", bg=COLORS["bg_dark"])
        self._prog_msg.pack(side="left")

        p_right = tk.Frame(p_row, bg=COLORS["bg_dark"])
        p_right.pack(side="right")

        self._prog_eta_lbl = TXALabel(p_right, "⏱️ ETA: --:--", style="small", color=COLORS["text_secondary"], bg=COLORS["bg_dark"])
        self._prog_eta_lbl.pack(side="left", padx=(0, 12))

        self._prog_pct_lbl = TXALabel(p_right, "00.00%", style="accent", bg=COLORS["bg_dark"])
        self._prog_pct_lbl.pack(side="left")

        # Terminal Log Box
        log_frame = tk.Frame(c, bg=COLORS["bg_input"],
                             highlightthickness=1,
                             highlightbackground=COLORS["border"])
        log_frame.pack(fill="both", expand=True, pady=4)

        scroll = tk.Scrollbar(log_frame)
        self._log_text = tk.Text(
            log_frame, bg=COLORS["bg_input"], fg="#A0A0A0",
            font=FONTS["mono"], bd=0, state="disabled",
            wrap="word", relief="flat", yscrollcommand=scroll.set
        )
        scroll.config(command=self._log_text.yview)
        scroll.pack(side="right", fill="y")
        self._log_text.pack(fill="both", expand=True, padx=8, pady=8)

        # Nút cài đặt to ở Tab 3
        if not self._install_running:
            b_frame = tk.Frame(c, bg=COLORS["bg_dark"])
            b_frame.pack(fill="x", pady=(6, 0))
            TXAButton(b_frame, "🚀 BẮT ĐẦU CÀI ĐẶT TỰ ĐỘNG NGAY",
                      command=self._confirm_and_start, style="primary",
                      width=320, height=42).pack(anchor="center")

    def _update_progress(self, pct: float, msg: str, eta: str = ""):
        def _ui():
            if hasattr(self, '_prog_bar') and self._prog_bar.winfo_exists():
                if pct >= 0:
                    self._prog_bar.set(pct)
            if hasattr(self, '_prog_pct_lbl') and self._prog_pct_lbl.winfo_exists():
                if pct >= 0:
                    self._prog_pct_lbl.config(text=f"{float(pct):05.2f}%")
            if hasattr(self, '_prog_eta_lbl') and self._prog_eta_lbl.winfo_exists():
                if eta and eta != "--:--":
                    self._prog_eta_lbl.config(text=f"⏱️ ETA: {eta}", fg=COLORS["warning"])
                elif pct >= 100:
                    self._prog_eta_lbl.config(text="⏱️ Hoàn tất", fg=COLORS["success"])
                elif pct > 0:
                    self._prog_eta_lbl.config(text="⏱️ ETA: Đang tính...", fg=COLORS["text_secondary"])
            if hasattr(self, '_prog_msg') and self._prog_msg.winfo_exists():
                self._prog_msg.config(text=msg[:100])
            if hasattr(self, '_log_text') and self._log_text.winfo_exists():
                self._log_text.configure(state="normal")
                log_prefix = f"[{float(pct):05.2f}%]" if pct >= 0 else "[INFO]"
                eta_suffix = f" (ETA: {eta})" if eta and eta != "--:--" else ""
                self._log_text.insert("end", f"{log_prefix}{eta_suffix} {msg}\n")
                self._log_text.see("end")
                self._log_text.configure(state="disabled")
            self._set_status(msg[:50])

            # CẬP NHẬT TIẾN TRÌNH LÊN THANH TÁC VỤ (WINDOWS TASKBAR)
            try:
                from core.taskbar import taskbar_progress
                taskbar_progress.set_progress(pct, self.winfo_id())
            except Exception:
                pass
        self.after(0, _ui)

    # ── Lưu dữ liệu tạm khi chuyển tab ──────────────────────────────

    def _save_tab_inputs(self):
        try:
            if hasattr(self, '_c_entry'):
                try:
                    if self._c_entry.winfo_exists():
                        self._config["c_gb"] = int(self._c_entry.get().strip())
                except Exception:
                    pass
            if hasattr(self, '_data_entry'):
                try:
                    if self._data_entry.winfo_exists():
                        self._config["data_gb"] = int(self._data_entry.get().strip())
                except Exception:
                    pass
            if hasattr(self, '_username_e'):
                try:
                    if self._username_e.winfo_exists():
                        v = self._username_e.get().strip()
                        if v:
                            self._config["username"] = v
                except Exception:
                    pass
            if hasattr(self, '_password_e'):
                try:
                    if self._password_e.winfo_exists():
                        self._config["password"] = self._password_e.get()
                except Exception:
                    pass
            if hasattr(self, '_pcname_e'):
                try:
                    if self._pcname_e.winfo_exists():
                        self._config["computer_name"] = self._pcname_e.get().strip() or "TXA-PC"
                except Exception:
                    pass
            if hasattr(self, '_key_e'):
                try:
                    if self._key_e.winfo_exists():
                        self._config["product_key"] = self._key_e.get().strip()
                except Exception:
                    pass
            if hasattr(self, '_var_bypass_tpm'):
                self._config["bypass_tpm"] = self._var_bypass_tpm.get()
            if hasattr(self, '_var_skip_ms'):
                self._config["skip_ms_account"] = self._var_skip_ms.get()
            if hasattr(self, '_var_autologon'):
                self._config["auto_logon"] = self._var_autologon.get()
            if hasattr(self, '_var_regional'):
                self._config["regional_same"] = self._var_regional.get()
            if hasattr(self, '_var_telemetry'):
                self._config["disable_telemetry"] = self._var_telemetry.get()
            if hasattr(self, '_var_bitlocker'):
                self._config["disable_bitlocker"] = self._var_bitlocker.get()
            if hasattr(self, '_var_classic_menu'):
                self._config["classic_context_menu"] = self._var_classic_menu.get()
            if hasattr(self, '_var_hibernate'):
                self._config["disable_hibernation"] = self._var_hibernate.get()
            if hasattr(self, '_var_search_index'):
                self._config["disable_search_indexing"] = self._var_search_index.get()
            if hasattr(self, '_var_power_plan'):
                self._config["high_performance_power"] = self._var_power_plan.get()
            if hasattr(self, '_var_activate'):
                self._config["auto_activate"] = self._var_activate.get()
            if hasattr(self, '_var_quick_format'):
                self._config["quick_format"] = self._var_quick_format.get()
            if hasattr(self, '_var_auto_reboot'):
                self._config["auto_reboot"] = self._var_auto_reboot.get()

            # Lưu các file Registry Tweaks được người dùng tích chọn
            if hasattr(self, '_tweak_vars') and hasattr(self, '_available_tweaks'):
                sel_tweaks = []
                for tw in self._available_tweaks:
                    var = self._tweak_vars.get(tw["id"])
                    if var and var.get():
                        sel_tweaks.append(tw["path"])
                self._config["selected_tweak_paths"] = sel_tweaks

            # Lưu file unattend XML nếu người dùng chọn từ dropdown
            if hasattr(self, '_cb_unattend') and self._cb_unattend and hasattr(self, '_unattend_files'):
                try:
                    if self._cb_unattend.winfo_exists():
                        idx = self._cb_unattend.current()
                        if 0 <= idx < len(self._unattend_files):
                            self._config["custom_unattend_path"] = self._unattend_files[idx]["path"]
                except Exception:
                    pass

            # Lưu đường dẫn driver và tùy chọn tự động khôi phục
            if hasattr(self, '_driver_path_e') and self._driver_path_e:
                try:
                    if self._driver_path_e.winfo_exists():
                        dp = self._driver_path_e.get().strip()
                        if dp:
                            self._driver_backup_path = dp
                            self._config["driver_backup_path"] = dp
                except Exception:
                    pass
            if hasattr(self, '_driver_auto_restore'):
                self._config["driver_auto_restore"] = self._driver_auto_restore.get()
        except Exception:
            pass

    # ── Xác thực & Bắt đầu cài đặt ─────────────────────────────────

    def _validate_all(self) -> bool:
        self._save_tab_inputs()

        # 1. Kiểm tra ISO / WIM
        if not self._selected_iso:
            messagebox.showerror("Thiếu file cài đặt", "Vui lòng chọn file ISO hoặc WIM/ESD Windows ở Tab 'Cài đặt chính'!")
            self._tab_bar.set_current(0)
            return False

        if not self._wim_path:
            messagebox.showerror("Chưa sẵn sàng", "File cài đặt đang được nạp, vui lòng chờ trong giây lát!")
            return False

        # 2. Kiểm tra ổ đĩa
        if not self._selected_disk:
            messagebox.showerror("Chưa chọn ổ đĩa", "Vui lòng chọn ổ đĩa muốn cài đặt ở Tab 'Cài đặt chính'!")
            self._tab_bar.set_current(0)
            return False

        install_mode = self._config.get("install_mode", "existing_partition")
        if install_mode == "clean_disk":
            c_gb = self._config.get("c_gb", 60)
            if c_gb < 30:
                messagebox.showerror("Kích thước không hợp lệ", "Dung lượng phân vùng ổ C: tối thiểu phải từ 30 GB trở lên!")
                return False
        else:
            target_ltr = self._config.get("target_partition_letter", "")
            if not target_ltr:
                messagebox.showerror("Chưa chọn phân vùng", "Vui lòng chọn một phân vùng để cài đặt Windows!")
                return False

        # 3. Kiểm tra User
        u = self._config.get("username", "User")
        if not u or " " in u or len(u) > 20:
            messagebox.showerror("Tên người dùng không hợp lệ", "Tên người dùng không được chứa dấu cách và tối đa 20 ký tự!")
            self._tab_bar.set_current(1)
            return False

        return True

    def _confirm_and_start(self):
        if not self._validate_all():
            return

        disk = self._selected_disk
        iso_name = Path(self._selected_iso).name
        install_mode = self._config.get("install_mode", "existing_partition")
        target_ltr = self._config.get("target_partition_letter", "C")
        c_gb = self._config.get("c_gb", 60)
        data_gb = self._config.get("data_gb", 0)

        if install_mode == "existing_partition":
            msg = (
                f"BẠN CÓ CHẮC CHẮN MUỐN CÀI ĐẶT WINDOWS?\n\n"
                f"• Chế độ: Cài vào phân vùng có sẵn (BẢO TOÀN DỮ LIỆU KHÁC)\n"
                f"• File cài đặt: {iso_name}\n"
                f"• Ổ đĩa: Disk {disk.index} ({disk.model})\n"
                f"• Phân vùng đích: {target_ltr}: (Sẽ được format để cài Windows mới)\n\n"
                f"🛡️ AN TOÀN TUYỆT ĐỐI:\n"
                f"Các phân vùng khác trên ổ đĩa (D:, E:...) sẽ được BẢO TOÀN NGUYÊN VẸN, không bị xóa!\n\n"
                f"Bạn có muốn bắt đầu cài đặt ngay không?"
            )
        elif self.is_winpe:
            msg = (
                f"BẠN CÓ CHẮC CHẮN MUỐN FORMAT SẠCH TOÀN BỘ Ổ ĐĨA TRÊN WINPE?\n\n"
                f"• Môi trường: Windows PE (RAMDisk X:\\)\n"
                f"• File cài đặt: {iso_name}\n"
                f"• Ổ đĩa đích: Disk {disk.index} ({disk.model})\n"
                f"• Phân chia lại: C: {c_gb} GB | DATA: {data_gb} GB\n\n"
                f"⚡ CÀI ĐẶT TRỰC TIẾP:\n"
                f"Hệ thống sẽ thực hiện phân vùng, format và bung nạp Windows trực tiếp.\n\n"
                f"⚠️ CẢNH BÁO: Toàn bộ dữ liệu trên Disk {disk.index} sẽ bị XÓA HOÀN TOÀN!"
            )
        elif disk.is_system_disk:
            msg = (
                f"BẠN ĐANG CHỌN XÓA SẠCH Ổ HỆ THỐNG ĐANG CHẠY:\n\n"
                f"• Ổ đĩa: Disk {disk.index} ({disk.model}) — Đang chứa Windows hiện tại\n"
                f"• File cài đặt: {iso_name}\n"
                f"• Phân vùng dự kiến: C: {c_gb} GB | DATA: {data_gb} GB\n\n"
                f"⚠️ QUY TRÌNH TỰ ĐỘNG KHỞI ĐỘNG LẠI:\n"
                f"Vì đang dùng Windows, hệ thống không thể format ổ C: trực tiếp.\n"
                f"Tool sẽ lưu cấu hình và TỰ ĐỘNG REBOOT máy tính để tiếp tục phân vùng sạch sau khi khởi động lại.\n\n"
                f"Bạn có chắc chắn muốn tiếp tục và khởi động lại không?"
            )
        else:
            msg = (
                f"BẠN CÓ CHẮC CHẮN MUỐN XÓA SẠCH VÀ PHÂN VÙNG LẠI Ổ ĐĨA?\n\n"
                f"• File cài đặt: {iso_name}\n"
                f"• Ổ đĩa đích: Disk {disk.index} ({disk.model})\n"
                f"• Phân chia: C: {c_gb} GB | DATA: {data_gb} GB\n\n"
                f"⚠️ CẢNH BÁO: Toàn bộ dữ liệu trên Disk {disk.index} sẽ bị XÓA HOÀN TOÀN!"
            )

        confirm = messagebox.askyesno("Xác nhận cài đặt tự động", msg, icon="warning")
        if not confirm:
            return

        # Chuyển sang Tab 3 (Tiến trình & Log)
        self._tab_bar.set_current(3)
        self._start_install_process()

    def _start_install_process(self):
        self._install_running = True
        self._btn_auto_install.config_state(True)
        self._btn_auto_install.set_text("⏳ ĐANG CÀI ĐẶT...")

        def _worker():
            try:
                from core.installer import run_full_install
                ok, msg = run_full_install(
                    state=self.state,
                    disk=self._selected_disk,
                    wim_path=self._wim_path,
                    image_index=self._selected_image_idx,
                    config=self._config,
                    driver_backup_path=self._driver_backup_path if self._driver_auto_restore.get() else "",
                    tool_exe_path=sys.executable,
                    progress=self._update_progress,
                )
                self._install_running = False
                if ok:
                    if msg == "SYSTEM_DISK_REBOOT":
                        self.after(0, self._page_system_disk_reboot)
                    else:
                        self.after(0, self._page_done)
                else:
                    self.after(0, lambda: self._install_failed(msg))
            except Exception as e:
                self._install_running = False
                self.after(0, lambda: self._install_failed(str(e)))

        threading.Thread(target=_worker, daemon=True).start()

    def _install_failed(self, msg: str):
        messagebox.showerror("Cài đặt thất bại", f"Lỗi:\n{msg}")
        self._update_progress(-1, f"❌ LỖI: {msg}")
        try:
            from core.taskbar import taskbar_progress
            taskbar_progress.set_error(self.winfo_id())
        except Exception:
            pass
        self._btn_auto_install.config_state(False)
        self._btn_auto_install.set_text("🚀 BẮT ĐẦU CÀI ĐẶT TỰ ĐỘNG")

    def _page_system_disk_reboot(self):
        self._clear_content()
        c = self._content
        tk.Label(c, text="🔄", bg=COLORS["bg_dark"],
                 fg=COLORS["warning"], font=("Segoe UI Emoji", 48)).pack(pady=(20, 4))
        TXALabel(c, "Đã chuẩn bị môi trường cài đặt thành công!", style="title", bg=COLORS["bg_dark"]).pack()

        info = (
            "Do bạn chọn cài đặt lên ổ đĩa đang chạy Windows hiện tại,\n"
            "hệ thống đã lưu trạng thái cấu hình và thiết lập tự động cài đặt sau khi khởi động lại.\n\n"
            "Máy tính sẽ khởi động lại để format ổ và tiếp tục cài đặt tự động từ môi trường khởi động an toàn."
        )
        TXALabel(c, info, style="body", bg=COLORS["bg_dark"]).pack(pady=10)

        self._countdown = 15
        self._countdown_lbl = TXALabel(c, f"Tự động khởi động lại sau {self._countdown}s...",
                                        style="accent", bg=COLORS["bg_dark"])
        self._countdown_lbl.pack(pady=4)

        btn_row = tk.Frame(c, bg=COLORS["bg_dark"])
        btn_row.pack(pady=16)
        TXAButton(btn_row, "Khởi động lại ngay",
                  command=self._do_reboot,
                  style="primary", width=220, height=44).pack(side="left", padx=8)
        TXAButton(btn_row, "Hủy đếm ngược",
                  command=lambda: setattr(self, '_countdown', 999999),
                  style="ghost", width=160, height=44).pack(side="left", padx=8)

        self._tick_countdown()

    def _page_done(self):
        try:
            from core.taskbar import taskbar_progress
            taskbar_progress.set_progress(100.0, self.winfo_id())
        except Exception:
            pass
        self._clear_content()
        c = self._content
        tk.Label(c, text="✓", bg=COLORS["bg_dark"],
                 fg=COLORS["success"], font=("Segoe UI", 48)).pack(pady=(20, 4))
        TXALabel(c, "Cài đặt hoàn tất!", style="title", bg=COLORS["bg_dark"]).pack()
        TXALabel(c, "Windows đã được bung thành công vào ổ đĩa.\nMáy tính sẽ khởi động lại để hoàn tất cấu hình tự động.",
                 style="secondary", bg=COLORS["bg_dark"]).pack(pady=8)

        auto_reb = self._config.get("auto_reboot", True)
        if auto_reb:
            self._countdown = 15
            self._countdown_lbl = TXALabel(c, f"Tự động khởi động lại sau {self._countdown}s",
                                            style="muted", bg=COLORS["bg_dark"])
            self._countdown_lbl.pack(pady=4)
        else:
            TXALabel(c, "Đã hoàn tất bung nạp Windows. Bạn có thể tự khởi động lại máy khi sẵn sàng.",
                     style="muted", bg=COLORS["bg_dark"]).pack(pady=4)

        btn_row = tk.Frame(c, bg=COLORS["bg_dark"])
        btn_row.pack(pady=16)
        TXAButton(btn_row, "Khởi động lại ngay",
                  command=self._do_reboot,
                  style="primary", width=200, height=44).pack(side="left", padx=8)
        TXAButton(btn_row, "Đóng tool",
                  command=self.destroy,
                  style="ghost", width=160, height=44).pack(side="left", padx=8)

        if auto_reb:
            self._tick_countdown()

    def _tick_countdown(self):
        self._countdown -= 1
        if self._countdown <= 0:
            self._do_reboot()
            return
        if hasattr(self, '_countdown_lbl'):
            self._countdown_lbl.config(text=f"Tự động khởi động lại sau {self._countdown}s")
            self.after(1000, self._tick_countdown)

    def _do_reboot(self):
        os.system("shutdown /r /t 5 /c \"TXA WinSetup: Khởi động lại để hoàn tất cài đặt\"")
        self.destroy()

    def _go_phase3(self):
        self._tab_bar.set_current(3)
        self._update_progress(0, "Phase 3: Tự động cài đặt driver và tối ưu sau reboot...")

        def _worker():
            from core.installer import phase3_install_drivers, phase3_cleanup
            phase3_install_drivers(self.state, self._update_progress)
            phase3_cleanup(self.state, self._update_progress)
            self.after(0, self._page_done)

        threading.Thread(target=_worker, daemon=True).start()

    def _ask_resume(self):
        from core.state import STEP_LABELS
        step = self.state.step
        label = STEP_LABELS.get(step, str(step))
        resume = messagebox.askyesno(
            "Tiếp tục cài đặt?",
            f"Phát hiện tiến trình cài đặt trước đó đang dở:\n"
            f"Bước: {label}\n\n"
            "Bạn có muốn tiếp tục từ bước này không?"
        )
        if resume:
            self._tab_bar.set_current(3)
            self._start_install_process()
        else:
            self.state.clear()

    def _load_app_branding(self):
        """Nạp Logo và Icon ứng dụng thống nhất lên thanh tiêu đề và thanh tác vụ."""
        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base = Path(sys._MEIPASS) / "assets"
            else:
                base = Path(__file__).resolve().parent.parent / "assets"

            logo_small = base / "logo_small.png"
            if logo_small.exists():
                self._logo_small_img = tk.PhotoImage(file=str(logo_small))
                # iconphoto(True, ...) thay thế triệt để icon lông vũ mặc định của Tkinter trên tiêu đề cửa sổ
                try:
                    self.iconphoto(True, self._logo_small_img)
                except Exception:
                    pass
            else:
                self._logo_small_img = None

            ico_file = base / "icon.ico"
            if ico_file.exists():
                try:
                    self.iconbitmap(default=str(ico_file))
                    self.iconbitmap(str(ico_file))
                except Exception:
                    pass

                # Sử dụng trực tiếp Win32 API WM_SETICON để ép thanh tiêu đề Windows DWM hiển thị icon chính xác
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    IMAGE_ICON = 1
                    LR_LOADFROMFILE = 0x00000010
                    WM_SETICON = 0x0080
                    h_icon_big = user32.LoadImageW(None, str(ico_file), IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
                    h_icon_small = user32.LoadImageW(None, str(ico_file), IMAGE_ICON, 16, 16, LR_LOADFROMFILE)

                    wid = self.winfo_id()
                    root_hwnd = user32.GetAncestor(wid, 3) or wid
                    for h in (wid, root_hwnd):
                        if h:
                            if h_icon_small:
                                user32.SendMessageW(h, WM_SETICON, 0, h_icon_small)
                            if h_icon_big:
                                user32.SendMessageW(h, WM_SETICON, 1, h_icon_big)
                except Exception:
                    pass
        except Exception:
            self._logo_small_img = None

    def _on_window_close(self):
        """Xử lý đóng ứng dụng an toàn: dọn dẹp taskbar progress và unmount toàn bộ ISO."""
        try:
            from core.taskbar import taskbar_progress
            taskbar_progress.clear(self.winfo_id())
        except Exception:
            pass
        try:
            from core.wim import unmount_all_iso
            unmount_all_iso()
        except Exception:
            pass
        self.destroy()

    def _auto_check_update_on_startup(self):
        """Tự động kiểm tra bản cập nhật trên luồng ngầm khi khởi động ứng dụng."""
        try:
            from core.updater import is_auto_check_enabled, check_update_async
            if not is_auto_check_enabled():
                return
            def on_result(res):
                self.after(0, lambda: self._handle_startup_update_result(res))
            check_update_async(on_result)
        except Exception:
            pass

    def _handle_startup_update_result(self, res):
        """Xử lý kết quả kiểm tra cập nhật tự động khi khởi động."""
        if res.get("has_update"):
            ver = res.get("latest_version")
            self._btn_check_update.config(
                text=f"⚡ Có bản v{ver} mới!",
                bg=COLORS["success"],
                fg="#0D0D0D",
                font=FONTS["brand"]
            )

    def _on_check_update_click(self):
        """Mở cửa sổ chi tiết cập nhật ứng dụng và tùy chọn bật/tắt tự động cập nhật."""
        self._open_update_window()

    def _open_update_window(self, pre_result=None):
        """Mở giao diện tương tác kiểm tra cập nhật, xem changelog và bật/tắt tùy chọn."""
        from core.updater import is_auto_check_enabled, set_auto_check_enabled, check_update_async, APP_VERSION
        import webbrowser

        win = tk.Toplevel(self)
        win.title("Cập nhật phần mềm — TXA WinSetup")
        win.configure(bg=COLORS["bg_dark"])
        win.geometry("540x480")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        # Căn giữa so với cửa sổ cha
        try:
            win.update_idletasks()
            px, py = self.winfo_x(), self.winfo_y()
            pw, ph = self.winfo_width(), self.winfo_height()
            x = px + max(0, (pw - 540) // 2)
            y = py + max(0, (ph - 480) // 2)
            win.geometry(f"540x480+{x}+{y}")
        except Exception:
            pass

        # Header
        hdr = tk.Frame(win, bg=COLORS["bg_panel"], padx=18, pady=14)
        hdr.pack(fill="x")
        tk.Label(hdr, text="TXA WinSetup — Trình Cập Nhật", bg=COLORS["bg_panel"],
                 fg=COLORS["text_primary"], font=FONTS["heading"]).pack(anchor="w")
        tk.Label(hdr, text=f"Phiên bản hiện tại: v{APP_VERSION} (Stable)", bg=COLORS["bg_panel"],
                 fg=COLORS["text_secondary"], font=FONTS["small"]).pack(anchor="w", pady=(2, 0))

        content = tk.Frame(win, bg=COLORS["bg_dark"], padx=18, pady=14)
        content.pack(fill="both", expand=True)

        # Status row
        status_lbl = tk.Label(content, text="● Đang kiểm tra phiên bản mới từ GitHub...",
                              bg=COLORS["bg_dark"], fg=COLORS["info"], font=FONTS["body"])
        status_lbl.pack(anchor="w", pady=(0, 10))

        # Changelog / Info text box
        txt_box = tk.Text(content, bg=COLORS["bg_input"], fg=COLORS["text_primary"],
                          font=FONTS["small"], relief="flat", height=8, wrap="word",
                          highlightthickness=1, highlightbackground=COLORS["border"])
        txt_box.pack(fill="both", expand=True, pady=(0, 12))
        txt_box.insert("1.0", f"Phiên bản hiện tại: v{APP_VERSION} (Bản mới nhất)\n\nĐang kết nối kiểm tra dữ liệu từ máy chủ...")
        txt_box.config(state="disabled")

        # Action buttons frame (download setup / portable)
        btn_action_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        btn_action_frame.pack(fill="x", pady=(0, 12))

        # Checkbox Tự động kiểm tra bản cập nhật
        cfg_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        cfg_frame.pack(fill="x", pady=(0, 8))

        auto_var = tk.BooleanVar(value=is_auto_check_enabled())
        def on_toggle_auto():
            set_auto_check_enabled(auto_var.get())
            cfg_tip.config(text="✓ Đã bật tự động kiểm tra!" if auto_var.get() else "✓ Đã tắt tự động kiểm tra!")
            self.after(2500, lambda: cfg_tip.config(text=""))

        chk = tk.Checkbutton(
            cfg_frame,
            text="Tự động kiểm tra bản cập nhật mới khi mở ứng dụng",
            variable=auto_var,
            command=on_toggle_auto,
            bg=COLORS["bg_dark"],
            fg=COLORS["text_primary"],
            selectcolor=COLORS["bg_panel"],
            activebackground=COLORS["bg_dark"],
            activeforeground=COLORS["accent"],
            font=FONTS["small"],
            cursor="hand2"
        )
        chk.pack(side="left")

        cfg_tip = tk.Label(cfg_frame, text="", bg=COLORS["bg_dark"], fg=COLORS["success"], font=FONTS["small"])
        cfg_tip.pack(side="left", padx=8)

        # Bottom buttons
        bottom = tk.Frame(win, bg=COLORS["bg_panel"], padx=18, pady=10)
        bottom.pack(fill="x", side="bottom")

        close_btn = tk.Button(bottom, text="Đóng", bg=COLORS["bg_card"], fg=COLORS["text_secondary"],
                              relief="flat", padx=14, pady=4, cursor="hand2", command=win.destroy)
        close_btn.pack(side="right")

        recheck_btn = tk.Button(bottom, text="⟳ Kiểm tra lại", bg=COLORS["bg_card"], fg=COLORS["accent"],
                                relief="flat", padx=14, pady=4, cursor="hand2")
        recheck_btn.pack(side="right", padx=8)

        def apply_result(res):
            for w in btn_action_frame.winfo_children():
                w.destroy()
            txt_box.config(state="normal")
            txt_box.delete("1.0", "end")

            if not res.get("success"):
                status_lbl.config(text="❌ Không thể kết nối tới máy chủ cập nhật", fg=COLORS["error"])
                txt_box.insert("1.0", f"Lỗi: {res.get('error', 'Không có kết nối mạng hoặc GitHub không phản hồi.')}")
            elif res.get("has_update"):
                latest_v = res.get("latest_version")
                r_date = res.get("release_date", "")
                status_lbl.config(text=f"✨ Có phiên bản mới: v{latest_v} ({r_date})", fg=COLORS["success"])
                cl = res.get("changelog", "Không có thông tin chi tiết.")
                txt_box.insert("1.0", f"--- NỘI DUNG BẢN CẬP NHẬT v{latest_v} ---\n\n{cl}")

                s_url = res.get("setup_url")
                if s_url:
                    tk.Button(
                        btn_action_frame, text="📥 Tải bộ cài Setup (.exe)",
                        bg=COLORS["accent"], fg="#FFFFFF", font=FONTS["small"],
                        relief="flat", padx=10, pady=4, cursor="hand2",
                        command=lambda u=s_url: webbrowser.open(u)
                    ).pack(side="left", padx=(0, 8))

                p_url = res.get("portable_url")
                if p_url:
                    tk.Button(
                        btn_action_frame, text="📦 Tải Portable (.exe)",
                        bg=COLORS["bg_card"], fg=COLORS["text_primary"], font=FONTS["small"],
                        relief="flat", padx=10, pady=4, cursor="hand2",
                        command=lambda u=p_url: webbrowser.open(u)
                    ).pack(side="left", padx=(0, 8))

                gh_url = res.get("releases_page")
                if gh_url:
                    tk.Button(
                        btn_action_frame, text="🌐 GitHub Release",
                        bg=COLORS["bg_card"], fg=COLORS["text_secondary"], font=FONTS["small"],
                        relief="flat", padx=10, pady=4, cursor="hand2",
                        command=lambda u=gh_url: webbrowser.open(u)
                    ).pack(side="left")
            else:
                status_lbl.config(text=f"✅ Bạn đang sử dụng phiên bản mới nhất: v{APP_VERSION}", fg=COLORS["success"])
                txt_box.insert("1.0", f"Phiên bản hiện tại: v{APP_VERSION} (Bản mới nhất)\n\nKhông có bản cập nhật nào mới hơn trên GitHub.\n\nTXA WinSetup hiện tại là bản cập nhật chuẩn nhất và hoạt động hoàn toàn ổn định.")

            txt_box.config(state="disabled")
            recheck_btn.config(state="normal", text="⟳ Kiểm tra lại")

        def run_check():
            status_lbl.config(text="● Đang kiểm tra phiên bản mới từ GitHub...", fg=COLORS["info"])
            recheck_btn.config(state="disabled", text="Đang kiểm tra...")
            check_update_async(lambda res: win.after(0, lambda: apply_result(res)))

        recheck_btn.config(command=run_check)

        if pre_result:
            apply_result(pre_result)
        else:
            run_check()
