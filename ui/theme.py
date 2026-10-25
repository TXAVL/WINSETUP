"""
TXA WinSetup — Design tokens & theme
"""

# ── Màu sắc TXA ─────────────────────────────────────────────────────
COLORS = {
    # Nền
    "bg_dark":       "#0D0D0D",
    "bg_panel":      "#141414",
    "bg_card":       "#1A1A1A",
    "bg_input":      "#111111",
    "bg_hover":      "#222222",

    # TXA accent — đỏ cam
    "accent":        "#E8431A",
    "accent_hover":  "#FF5530",
    "accent_dim":    "#7A2310",
    "accent_glow":   "#E8431A33",

    # Text
    "text_primary":  "#F0F0F0",
    "text_secondary":"#888888",
    "text_muted":    "#444444",
    "text_accent":   "#E8431A",

    # Status
    "success":       "#22C55E",
    "warning":       "#F59E0B",
    "error":         "#EF4444",
    "info":          "#3B82F6",

    # Border
    "border":        "#2A2A2A",
    "border_focus":  "#E8431A",
}

FONTS = {
    "title":    ("Segoe UI", 22, "bold"),
    "heading":  ("Segoe UI", 14, "bold"),
    "subhead":  ("Segoe UI", 12, "bold"),
    "body":     ("Segoe UI", 11),
    "small":    ("Segoe UI", 10),
    "mono":     ("Consolas", 10),
    "logo":     ("Segoe UI Black", 26, "bold"),
    "brand":    ("Segoe UI", 11, "bold"),
}

RADIUS = 8   # Corner radius px

STEP_NAMES = [
    "Chọn ISO",
    "Chọn ổ đĩa",
    "Cấu hình",
    "Backup driver",
    "Xác nhận",
    "Đang cài",
    "Hoàn tất",
]

TAB_ITEMS = [
    ("Cài đặt chính", "💽"),
    ("Tự động hóa", "⚙️"),
    ("Sao lưu Driver", "📦"),
    ("Tiến trình & Log", "🚀"),
]

