"""
Custom widgets dùng chung — TXA style
"""
import tkinter as tk
from tkinter import ttk
from .theme import COLORS, FONTS, RADIUS

class TXAButton(tk.Canvas):
    def __init__(self, parent, text="", command=None, style="primary",
                 width=160, height=40, **kw):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0,
                         bg=COLORS["bg_panel"], **kw)
        self.command = command
        self.style = style
        self.text = text
        self.w = width
        self.h = height
        self._hover = False
        self._disabled = False
        self._draw()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _bg(self):
        if self._disabled:
            return COLORS["text_muted"]
        if self.style == "primary":
            return COLORS["accent_hover"] if self._hover else COLORS["accent"]
        if self.style == "ghost":
            return COLORS["bg_hover"] if self._hover else COLORS["bg_card"]
        if self.style == "danger":
            return "#DC2626" if self._hover else "#B91C1C"
        return COLORS["bg_card"]

    def _draw(self):
        self.delete("all")
        r = RADIUS
        bg = self._bg()
        self._rounded_rect(2, 2, self.w-2, self.h-2, r, fill=bg, outline="")
        fg = COLORS["text_muted"] if self._disabled else COLORS["text_primary"]
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
        self._hover = True; self._draw()

    def _on_leave(self, _):
        self._hover = False; self._draw()

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
        # Vẽ border giả bằng frame ngoài
        self.configure(highlightbackground=COLORS["border"],
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
    """Thanh Tabs hiện đại phong cách TXA Studio"""
    def __init__(self, parent, tabs: list, on_change=None, current: int = 0, **kw):
        super().__init__(parent, bg=COLORS["bg_panel"], **kw)
        self.tabs = tabs  # list of (label, icon) or strings
        self.on_change = on_change
        self.current = current
        self._buttons = []
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        self._buttons = []

        bar_inner = tk.Frame(self, bg=COLORS["bg_panel"])
        bar_inner.pack(fill="x", padx=16)

        for i, item in enumerate(self.tabs):
            if isinstance(item, (list, tuple)):
                label, icon = item[0], item[1]
            else:
                label, icon = str(item), ""

            is_active = (i == self.current)
            canvas = tk.Canvas(bar_inner, height=44, bg=COLORS["bg_panel"],
                               highlightthickness=0, cursor="hand2")
            canvas.pack(side="left", padx=(0, 6), pady=(4, 0))

            self._render_tab(canvas, i, label, icon, is_active)
            canvas.bind("<Button-1>", lambda e, idx=i: self.set_current(idx))
            self._buttons.append((canvas, label, icon))

    def _render_tab(self, canvas, idx, label, icon, is_active):
        canvas.delete("all")
        text_str = f"{icon}  {label}".strip()
        font = FONTS["subhead"] if is_active else FONTS["body"]
        w = max(150, len(text_str) * 8 + 36)
        canvas.config(width=w)

        bg_col = COLORS["bg_card"] if is_active else COLORS["bg_panel"]
        fg_col = COLORS["accent"] if is_active else COLORS["text_secondary"]

        canvas.create_rectangle(0, 0, w, 44, fill=bg_col, outline="")
        if is_active:
            # Active bottom accent line
            canvas.create_rectangle(0, 40, w, 44, fill=COLORS["accent"], outline="")
        else:
            # Subtle border
            canvas.create_rectangle(0, 42, w, 44, fill=COLORS["border"], outline="")

        canvas.create_text(w // 2, 21, text=text_str, fill=fg_col, font=font)

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
    """Card hiển thị 1 phân vùng ổ đĩa để người dùng trực tiếp chọn phân vùng muốn cài Windows."""
    def __init__(self, parent, disk, partition, on_select=None, selected=False, **kw):
        super().__init__(parent, bg=COLORS["bg_card"], cursor="hand2", **kw)
        self.disk = disk
        self.partition = partition
        self.on_select = on_select
        self.selected = selected
        self._build()
        self._bind_click_recursive(self)

    def _bind_click_recursive(self, widget):
        widget.bind("<Button-1>", self._click)
        for child in widget.winfo_children():
            self._bind_click_recursive(child)

    def _build(self):
        border_col = COLORS["accent"] if self.selected else COLORS["border"]
        self.configure(
            highlightthickness=2,
            highlightbackground=border_col,
            padx=14, pady=10
        )
        from .theme import COLORS as C, FONTS as F
        p = self.partition
        d = self.disk

        # Row 1: Badges & status
        hdr = tk.Frame(self, bg=C["bg_card"])
        hdr.pack(fill="x")

        # Badge phân vùng
        p_badge = f"  Ổ {p.letter}:\\  " if p.letter else f"  Phân vùng {p.index}  "
        badge_bg = C["accent"] if self.selected else (C["warning"] if (p.is_system or p.letter == "C") else C["info"])
        tk.Label(hdr, text=p_badge, bg=badge_bg, fg=C["bg_dark"], font=F["subhead"], padx=6, pady=2).pack(side="left")

        # Label tên phân vùng & dung lượng
        label_text = f" [{p.label}]" if p.label else ""
        fs_text = f" ({p.fs})" if p.fs else ""
        tk.Label(hdr, text=f"  {p.size_gb} GB{fs_text}{label_text}", bg=C["bg_card"], fg=C["text_primary"], font=F["heading"]).pack(side="left")

        # Cảnh báo nếu là ổ đang chạy Windows
        if p.is_system or (p.letter == "C" and not d.is_system_disk):
            tk.Label(hdr, text=" ⚠️ PHÂN VÙNG WINDOWS HIỆN TẠI ", bg=C["warning"], fg=C["bg_dark"], font=F["small"], padx=4).pack(side="right")
        elif d.is_system_disk and p.letter == "C":
            tk.Label(hdr, text=" ⚠️ ĐANG CHẠY WINDOWS (TỰ REBOOT) ", bg=C["warning"], fg=C["bg_dark"], font=F["small"], padx=4).pack(side="right")
        elif p.bitlocker_status == "On":
            tk.Label(hdr, text=" 🔒 BITLOCKER ", bg=C["info"], fg="#FFFFFF", font=F["small"], padx=4).pack(side="right")

        # Row 2: Chi tiết ổ đĩa vật lý chứa phân vùng này
        sub_row = tk.Frame(self, bg=C["bg_card"])
        sub_row.pack(fill="x", pady=(6, 0))

        free_info = f"Còn trống: {p.free_gb} GB  •  " if p.free_gb > 0 else ""
        disk_desc = f"{free_info}Nằm trên Disk {d.index} ({d.model} — {d.interface} {d.size_gb} GB)"
        tk.Label(sub_row, text=disk_desc, bg=C["bg_card"], fg=C["text_secondary"], font=F["small"]).pack(side="left")

    def set_selected(self, val: bool):
        self.selected = val
        self.configure(
            highlightbackground=COLORS["accent"] if val else COLORS["border"]
        )

    def _click(self, _):
        if self.on_select:
            self.on_select(self.disk, self.partition)

