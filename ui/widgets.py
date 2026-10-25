"""
Custom widgets dùng chung — TXA style
"""
import tkinter as tk
from tkinter import ttk
from .theme import COLORS, FONTS, RADIUS

class TXAButton(tk.Canvas):
    def __init__(self, parent, text="", command=None, style="primary",
                 width=160, height=40, **kw):
        parent_bg = kw.pop("bg", None)
        if not parent_bg:
            try:
                parent_bg = parent.cget("bg")
            except Exception:
                parent_bg = COLORS["bg_card"]
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0,
                         bg=parent_bg, **kw)
        self.command = command
        self.style = style
        self.text = text
        self.w = width
        self.h = height
        self._hover = False
        self._disabled = False
        self._parent_bg = parent_bg
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _colors(self):
        if self._disabled:
            return COLORS["bg_hover"], COLORS["border"], COLORS["text_muted"]
        if self.style == "primary":
            bg = COLORS["accent_hover"] if self._hover else COLORS["accent"]
            border = COLORS["accent_hover"] if self._hover else COLORS["accent"]
            fg = "#FFFFFF"
            return bg, border, fg
        if self.style == "ghost":
            bg = COLORS["bg_hover"] if self._hover else COLORS["bg_card"]
            border = COLORS["border_focus"] if self._hover else COLORS["border_card"]
            fg = COLORS["text_primary"]
            return bg, border, fg
        if self.style == "danger":
            bg = "#E11D48" if self._hover else "#BE123C"
            border = "#FB7185" if self._hover else "#BE123C"
            fg = "#FFFFFF"
            return bg, border, fg
        return COLORS["bg_card"], COLORS["border"], COLORS["text_primary"]

    def _draw(self):
        self.delete("all")
        r = RADIUS
        bg, border, fg = self._colors()
        self._rounded_rect(2, 2, self.w-2, self.h-2, r, fill=bg, outline=border, width=1)
        self.create_text(
            self.w//2, self.h//2,
            text=self.text, fill=fg,
            font=FONTS["subhead"]
        )

    def _rounded_rect(self, x1, y1, x2, y2, r, **kw):
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90,  extent=90,  **kw)
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0,   extent=90,  **kw)
        self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90,  **kw)
        self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90,  **kw)
        self.create_rectangle(x1+r, y1, x2-r, y2, **kw)
        self.create_rectangle(x1, y1+r, x2, y2-r, **kw)

    def _on_enter(self, _):
        if not self._disabled:
            self._hover = True
            self.config(cursor="hand2")
            self._draw()

    def _on_leave(self, _):
        if not self._disabled:
            self._hover = False
            self.config(cursor="")
            self._draw()

    def _on_click(self, _):
        if not self._disabled and self.command:
            self.command()

    def config_state(self, disabled: bool):
        self._disabled = disabled
        self._draw()

    def set_text(self, text: str):
        self.text = text
        self._draw()


class TXACard(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(
            parent,
            bg=COLORS["bg_card"],
            relief="flat",
            padx=16, pady=12,
            **kw
        )
        self.configure(highlightbackground=COLORS["border_card"],
                       highlightthickness=1)


class TXALabel(tk.Label):
    def __init__(self, parent, text="", style="body", color=None, **kw):
        fg = color or COLORS.get({
            "body": "text_primary",
            "secondary": "text_secondary",
            "muted": "text_muted",
            "accent": "text_accent",
            "success": "success",
            "warning": "warning",
            "error": "error",
            "heading": "text_primary",
            "subhead": "text_primary",
        }.get(style, "text_primary"), COLORS["text_primary"])
        super().__init__(
            parent, text=text,
            bg=kw.pop("bg", COLORS["bg_panel"]),
            fg=fg,
            font=FONTS.get(style, FONTS["body"]),
            **kw
        )


class TXAEntry(tk.Entry):
    def __init__(self, parent, placeholder="", **kw):
        self._ph = placeholder
        self._has_ph = False
        super().__init__(
            parent,
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat",
            font=FONTS["body"],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            **kw
        )
        if placeholder:
            self._show_placeholder()
            self.bind("<FocusIn>", self._clear_placeholder)
            self.bind("<FocusOut>", self._show_placeholder_if_empty)

    def _show_placeholder(self, *_):
        if not self.get():
            self.insert(0, self._ph)
            self.config(fg=COLORS["text_muted"])
            self._has_ph = True

    def _clear_placeholder(self, *_):
        if self._has_ph:
            self.delete(0, "end")
            self.config(fg=COLORS["text_primary"])
            self._has_ph = False

    def _show_placeholder_if_empty(self, *_):
        if not self.get():
            self._show_placeholder()

    def get_value(self) -> str:
        return "" if self._has_ph else self.get()


class TXAStepper(tk.Frame):
    """Progress stepper ngang — hiển thị các bước cài đặt."""
    def __init__(self, parent, steps: list, current: int = 0, **kw):
        super().__init__(parent, bg=COLORS["bg_dark"], **kw)
        self.steps = steps
        self.current = current
        self._draw()

    def _draw(self):
        for w in self.winfo_children():
            w.destroy()

        for i, name in enumerate(self.steps):
            is_done = i < self.current
            is_active = i == self.current

            col = COLORS["accent"] if is_active else (
                COLORS["success"] if is_done else COLORS["text_muted"]
            )

            f = tk.Frame(self, bg=COLORS["bg_dark"])
            f.pack(side="left", padx=4)

            # Circle
            circ = tk.Canvas(f, width=24, height=24,
                             bg=COLORS["bg_dark"], highlightthickness=0)
            circ.pack()
            fill = col if (is_active or is_done) else COLORS["bg_card"]
            circ.create_oval(2, 2, 22, 22, fill=fill,
                             outline=col, width=2)
            label_text = "✓" if is_done else str(i + 1)
            circ.create_text(12, 12, text=label_text,
                             fill=COLORS["text_primary"] if (is_active or is_done)
                             else COLORS["text_muted"],
                             font=FONTS["small"])

            # Label
            tk.Label(f, text=name, bg=COLORS["bg_dark"],
                     fg=col, font=FONTS["small"]).pack()

            # Connector line (trừ bước cuối)
            if i < len(self.steps) - 1:
                line_col = COLORS["success"] if is_done else COLORS["border"]
                tk.Frame(self, width=20, height=2,
                         bg=line_col).pack(side="left", pady=12)

    def set_step(self, step: int):
        self.current = step
        self._draw()


class TXATabBar(tk.Frame):
    """Thanh Tabs hiện đại phong cách Cyber Obsidian Segmented Pill"""
    def __init__(self, parent, tabs: list, on_change=None, current: int = 0, **kw):
        super().__init__(parent, bg=COLORS["bg_panel"], **kw)
        self.tabs = tabs
        self.on_change = on_change
        self.current = current
        self._buttons = []
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        self._buttons = []

        bar_inner = tk.Frame(self, bg=COLORS["bg_panel"])
        bar_inner.pack(fill="x", padx=16, pady=4)

        for i, item in enumerate(self.tabs):
            if isinstance(item, (list, tuple)):
                label, icon = item[0], item[1]
            else:
                label, icon = str(item), ""

            is_active = (i == self.current)
            canvas = tk.Canvas(bar_inner, height=38, bg=COLORS["bg_panel"],
                               highlightthickness=0, cursor="hand2")
            canvas.pack(side="left", padx=(0, 8), pady=2)

            self._render_tab(canvas, i, label, icon, is_active)
            canvas.bind("<Button-1>", lambda e, idx=i: self.set_current(idx))

            def _bind_hover(c=canvas, idx=i, lbl=label, ic=icon):
                def _enter(e):
                    if idx != self.current:
                        self._render_tab(c, idx, lbl, ic, False, is_hover=True)
                def _leave(e):
                    if idx != self.current:
                        self._render_tab(c, idx, lbl, ic, False, is_hover=False)
                c.bind("<Enter>", _enter)
                c.bind("<Leave>", _leave)
            _bind_hover()

            self._buttons.append((canvas, label, icon))

    def _render_tab(self, canvas, idx, label, icon, is_active, is_hover=False):
        canvas.delete("all")
        text_str = f"{icon}  {label}".strip()
        font = FONTS["subhead"] if is_active else FONTS["body"]
        w = max(148, len(text_str) * 8 + 32)
        h = 36
        canvas.config(width=w, height=h)

        r = 8
        if is_active:
            bg_col = COLORS["bg_card_selected"]
            outline_col = COLORS["accent"]
            fg_col = "#FFFFFF"
        elif is_hover:
            bg_col = COLORS["bg_hover"]
            outline_col = COLORS["border_card"]
            fg_col = COLORS["text_primary"]
        else:
            bg_col = COLORS["bg_panel"]
            outline_col = COLORS["border"]
            fg_col = COLORS["text_secondary"]

        self._draw_pill(canvas, 1, 1, w - 2, h - 2, r, fill=bg_col, outline=outline_col, width=1)

        if is_active:
            canvas.create_rectangle(w//4, h - 3, w - w//4, h - 1, fill=COLORS["accent"], outline="")

        canvas.create_text(w // 2, h // 2, text=text_str, fill=fg_col, font=font)

    def _draw_pill(self, canvas, x1, y1, x2, y2, r, **kw):
        canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90,  extent=90,  **kw)
        canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0,   extent=90,  **kw)
        canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90,  **kw)
        canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90,  **kw)
        canvas.create_rectangle(x1+r, y1, x2-r, y2, **kw)
        canvas.create_rectangle(x1, y1+r, x2, y2-r, **kw)

    def set_current(self, idx: int):
        if idx == self.current:
            return
        self.current = idx
        for i, (canvas, label, icon) in enumerate(self._buttons):
            self._render_tab(canvas, i, label, icon, i == self.current)
        if self.on_change:
            self.on_change(idx)


class TXAScrollableFrame(tk.Frame):
    """Container có thanh cuộn mượt mà"""
    def __init__(self, parent, bg=COLORS["bg_dark"], **kw):
        super().__init__(parent, bg=bg, **kw)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable = tk.Frame(self.canvas, bg=bg)

        self.scrollable.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self._canvas_win = self.canvas.create_window((0, 0), window=self.scrollable, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self._on_resize)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)

    def _on_resize(self, event):
        self.canvas.itemconfig(self._canvas_win, width=event.width)

    def _on_wheel(self, event):
        try:
            if self.winfo_exists() and self.canvas.winfo_exists():
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


class TXAProgressBar(tk.Canvas):
    def __init__(self, parent, height=6, **kw):
        super().__init__(parent, height=height,
                         bg=COLORS["bg_card"],
                         highlightthickness=0, **kw)
        self._pct = 0
        self.bind("<Configure>", self._redraw)

    def set(self, pct: float):
        self._pct = max(0.0, min(100.0, float(pct)))
        self._redraw()

    def _redraw(self, *_):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = h // 2
        # Track
        self._rr(0, 0, w, h, r, fill=COLORS["border"], outline="")
        # Fill
        fill_w = int(w * self._pct / 100)
        if fill_w > 0:
            self._rr(0, 0, fill_w, h, r, fill=COLORS["accent"], outline="")

    def _rr(self, x1, y1, x2, y2, r, **kw):
        self.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, **kw)
        self.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, **kw)
        self.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, **kw)
        self.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, **kw)
        self.create_rectangle(x1+r, y1, x2-r, y2, **kw)
        self.create_rectangle(x1, y1+r, x2, y2-r, **kw)


class TXADiskCard(tk.Frame):
    """Card hiển thị thông tin 1 ổ đĩa, click để chọn."""
    def __init__(self, parent, disk, on_select=None, selected=False, **kw):
        super().__init__(parent, bg=COLORS["bg_card"],
                         cursor="hand2", **kw)
        self.disk = disk
        self.on_select = on_select
        self.selected = selected
        self._build()
        self.bind("<Button-1>", self._click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._click)

    def _build(self):
        border_col = COLORS["accent"] if self.selected else COLORS["border"]
        self.configure(
            highlightthickness=2,
            highlightbackground=border_col,
            padx=14, pady=10
        )

        from .theme import COLORS as C, FONTS as F
        d = self.disk

        # Header row
        hdr = tk.Frame(self, bg=C["bg_card"])
        hdr.pack(fill="x")

        # Icon interface
        iface_colors = {
            "NVMe": C["accent"], "SSD": C["info"],
            "HDD": C["text_secondary"], "USB": C["warning"]
        }
        icon_col = iface_colors.get(d.interface, C["text_muted"])

        tk.Label(hdr, text=f"  {d.interface}  ",
                 bg=icon_col, fg=C["bg_dark"],
                 font=F["small"], padx=4).pack(side="left")
        tk.Label(hdr, text=f"  Disk {d.index}",
                 bg=C["bg_card"], fg=C["text_secondary"],
                 font=F["small"]).pack(side="left")
        if d.is_system_disk:
            tk.Label(hdr, text=" ⚠️ ĐANG CHẠY WINDOWS (CẦN REBOOT) ",
                     bg=C["warning"], fg=C["bg_dark"],
                     font=F["small"], padx=4).pack(side="right")

        # Model + size
        tk.Label(self, text=d.model,
                 bg=C["bg_card"], fg=C["text_primary"],
                 font=F["subhead"], anchor="w").pack(fill="x", pady=(4, 0))
        tk.Label(self, text=f"{d.size_gb} GB  •  {len(d.partitions)} phân vùng",
                 bg=C["bg_card"], fg=C["text_secondary"],
                 font=F["small"], anchor="w").pack(fill="x")

        # Partitions
        if d.partitions:
            pf = tk.Frame(self, bg=C["bg_card"])
            pf.pack(fill="x", pady=(6, 0))
            for p in d.partitions[:5]:
                bl = ""
                if p.bitlocker_status == "On":
                    bl = "  🔒"
                elif p.bitlocker_status == "Locked":
                    bl = "  🔴"
                letter_str = f"{p.letter}:\\" if p.letter else f"[{p.type}]"
                info = f"{letter_str}  {p.size_gb}GB  {p.fs}{bl}"
                tk.Label(pf, text=f"  • {info}",
                         bg=C["bg_card"], fg=C["text_muted"],
                         font=F["small"], anchor="w").pack(fill="x")

    def set_selected(self, val: bool):
        self.selected = val
        self.configure(
            highlightbackground=COLORS["accent"] if val else COLORS["border"]
        )

    def _click(self, _):
        if self.on_select:
            self.on_select(self.disk)


class TXAPartitionCard(tk.Frame):
    """Card hiển thị 1 phân vùng ổ đĩa đẹp mắt, có thanh dung lượng trực quan (Mini Capacity Bar)"""
    def __init__(self, parent, disk, partition, on_select=None, selected=False, **kw):
        super().__init__(parent, bg=COLORS["bg_card"], cursor="hand2", **kw)
        self.disk = disk
        self.partition = partition
        self.on_select = on_select
        self.selected = selected
        self._build()
        self._bind_events_recursive(self)

    def _bind_events_recursive(self, widget):
        widget.bind("<Button-1>", self._click)
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        for child in widget.winfo_children():
            self._bind_events_recursive(child)

    def _on_enter(self, _):
        if not self.selected:
            self.configure(bg=COLORS["bg_hover"], highlightbackground=COLORS["border_card"])

    def _on_leave(self, _):
        if not self.selected:
            self.configure(bg=COLORS["bg_card"], highlightbackground=COLORS["border"])

    def _build(self):
        bg = COLORS["bg_card_selected"] if self.selected else COLORS["bg_card"]
        border_col = COLORS["accent"] if self.selected else COLORS["border"]
        self.configure(
            bg=bg,
            highlightthickness=2 if self.selected else 1,
            highlightbackground=border_col,
            padx=14, pady=10
        )
        from .theme import COLORS as C, FONTS as F
        p = self.partition
        d = self.disk

        # Xác định vai trò phân vùng
        is_win_os = (p.is_system or p.letter == "C") and p.size_gb >= 15.0
        is_system_part = p.type in ("EFI", "System", "MSR", "Reserved", "Recovery") or p.size_gb < 15.0

        # Row 1: Badges & status
        hdr = tk.Frame(self, bg=bg)
        hdr.pack(fill="x")

        # Radio checkmark icon
        if is_system_part and not is_win_os:
            radio_icon = "⊘"
            radio_color = C["text_muted"]
        else:
            radio_icon = "●" if self.selected else "○"
            radio_color = C["accent"] if self.selected else C["text_muted"]
        tk.Label(hdr, text=radio_icon, bg=bg, fg=radio_color, font=("Segoe UI", 12, "bold")).pack(side="left", padx=(0, 8))

        # Badge phân vùng
        p_badge = f"  Ổ {p.letter}:\\  " if p.letter else f"  Phân vùng {p.index}  "
        if self.selected:
            badge_bg = C["accent"]
            badge_fg = "#FFFFFF"
        elif is_win_os:
            badge_bg = C["warning"]
            badge_fg = "#000000"
        elif is_system_part:
            badge_bg = "#1E293B"
            badge_fg = "#94A3B8"
        else:
            badge_bg = C["info"]
            badge_fg = C["bg_dark"]
        tk.Label(hdr, text=p_badge, bg=badge_bg, fg=badge_fg, font=F["subhead"], padx=6, pady=2).pack(side="left")

        # Label tên phân vùng & dung lượng
        label_text = f" [{p.label}]" if p.label else ""
        fs_text = f" • {p.fs}" if p.fs else ""
        tk.Label(hdr, text=f"  {p.size_gb} GB{fs_text}{label_text}", bg=bg, fg=C["text_primary"], font=F["heading"]).pack(side="left")

        # Badges trạng thái bên phải
        if is_win_os:
            tk.Label(hdr, text=" ⚠️ WINDOWS HIỆN TẠI (TỰ REBOOT) ", bg=C["warning"], fg="#000000", font=F["badge"], padx=5, pady=2).pack(side="right")
        elif p.type in ("EFI", "System") or (p.size_gb < 2.0 and p.fs == "FAT32"):
            tk.Label(hdr, text=" 🛡 EFI BOOT ", bg="#1E293B", fg="#94A3B8", font=F["badge"], padx=5, pady=2).pack(side="right")
        elif p.type in ("MSR", "Reserved"):
            tk.Label(hdr, text=" ⚙ MSR DỰ TRỮ ", bg="#1E293B", fg="#94A3B8", font=F["badge"], padx=5, pady=2).pack(side="right")
        elif p.type == "Recovery" or "Recovery" in (p.label or ""):
            tk.Label(hdr, text=" 🔄 RECOVERY ", bg="#1E293B", fg="#94A3B8", font=F["badge"], padx=5, pady=2).pack(side="right")
        elif p.bitlocker_status == "On":
            tk.Label(hdr, text=" 🔒 BITLOCKER ", bg=C["info"], fg="#FFFFFF", font=F["badge"], padx=5, pady=2).pack(side="right")

        # Row 2: Thanh hiển thị dung lượng (Capacity Bar)
        total = p.size_gb
        free = p.free_gb if p.free_gb > 0 else (total * 0.4 if total > 0 else 0)
        used = max(0.0, total - free)
        pct = int((used / total) * 100) if total > 0 else 50
        pct = min(100, max(0, pct))

        bar_frame = tk.Frame(self, bg=bg)
        bar_frame.pack(fill="x", pady=(8, 2))

        bar_canvas = tk.Canvas(bar_frame, height=5, bg=C["bg_input"], highlightthickness=0)
        bar_canvas.pack(fill="x")

        def _draw_bar(event=None):
            w = bar_canvas.winfo_width()
            if w <= 1:
                w = 400
            bar_canvas.delete("all")
            bar_canvas.create_rectangle(0, 0, w, 5, fill=C["bg_input"], outline="")
            fill_w = int(w * (pct / 100.0))
            fill_col = C["accent"] if self.selected else (C["success"] if pct < 85 else C["warning"])
            if fill_w > 0:
                bar_canvas.create_rectangle(0, 0, fill_w, 5, fill=fill_col, outline="")

        bar_canvas.bind("<Configure>", _draw_bar)
        bar_canvas.after(20, _draw_bar)

        # Row 3: Chi tiết ổ đĩa vật lý
        sub_row = tk.Frame(self, bg=bg)
        sub_row.pack(fill="x", pady=(4, 0))

        free_desc = f"Đã dùng: {used:.1f} GB ({pct}%)  •  Còn trống: {free:.1f} GB  •  " if p.free_gb > 0 else ""
        disk_desc = f"{free_desc}Nằm trên Disk {d.index} ({d.model} — {d.interface} {d.size_gb} GB)"
        tk.Label(sub_row, text=disk_desc, bg=bg, fg=C["text_secondary"], font=F["small"]).pack(side="left")

    def set_selected(self, val: bool):
        self.selected = val
        for w in self.winfo_children():
            w.destroy()
        self._build()
        self._bind_events_recursive(self)

    def _click(self, _):
        if self.on_select:
            self.on_select(self.disk, self.partition)

