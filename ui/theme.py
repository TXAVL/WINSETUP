"""
TXA WinSetup — Design tokens & theme
"""

# ── Hệ thống màu sắc Cyber Obsidian UI 2.0 ───────────────────────────
COLORS = {
    # Nền đa tầng Obsidian & Slate
    "bg_dark":          "#0B0E14",   # Nền chính không gian sâu, chống mỏi mắt
    "bg_panel":         "#111622",   # Nền thanh Header & Footer
    "bg_card":          "#161D2B",   # Nền Card nội dung nổi bật
    "bg_card_selected": "#1E283C",   # Nền Card khi được người dùng click chọn
    "bg_input":         "#0D111A",   # Nền ô nhập liệu & Combobox
    "bg_hover":         "#202A3D",   # Hiệu ứng rê chuột

    # Điểm nhấn Electric Sunset Amber-Orange
    "accent":           "#FF5500",   # Cam điện tử rực rỡ, hiện đại
    "accent_hover":     "#FF6E26",   # Hover sáng rực
    "accent_dim":       "#7A2800",   # Nền tối điểm nhấn
    "accent_glow":      "#FF55002E", # Hào quang mờ xung quanh viền
    "accent_blue":      "#38BDF8",   # Xanh Cyber Neon
    "accent_purple":    "#A855F7",   # Tím Gradient

    # Kiểu chữ tương phản cao
    "text_primary":     "#F8FAFC",   # Trắng tinh khiết chuẩn Slate-50
    "text_secondary":   "#94A3B8",   # Xám nhạt thanh lịch Slate-400
    "text_muted":       "#64748B",   # Xám đậm ghi chú Slate-500
    "text_accent":      "#FF6E26",   # Màu chữ cam nổi bật

    # Trạng thái hệ thống rực rỡ
    "success":          "#10B981",   # Xanh ngọc lục bảo Emerald
    "warning":          "#F59E0B",   # Vàng hổ phách Amber
    "error":            "#F43F5E",   # Đỏ san hô rực rỡ Rose
    "info":             "#0EA5E9",   # Xanh biển Sky Blue

    # Viền sắc nét tinh tế
    "border":           "#222B3D",   # Đường viền 1px định hình khối
    "border_card":      "#273347",   # Viền card nổi
    "border_focus":     "#FF5500",   # Viền khi focus vào ô nhập
}

FONTS = {
    "title":    ("Segoe UI", 20, "bold"),
    "heading":  ("Segoe UI", 13, "bold"),
    "subhead":  ("Segoe UI", 11, "bold"),
    "body":     ("Segoe UI", 10),
    "small":    ("Segoe UI", 9),
    "badge":    ("Segoe UI", 8, "bold"),
    "mono":     ("Consolas", 10),
    "logo":     ("Segoe UI Black", 22, "bold"),
    "brand":    ("Segoe UI", 11, "bold"),
}

RADIUS = 10  # Bo góc hiện đại mềm mại

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

