@echo off
chcp 65001 >nul
:: ====================================================================
:: TXA WinSetup - Công cụ tự động sửa lỗi khởi động BCD Bootloader
:: Hỗ trợ cả 2 chuẩn UEFI (ESP FAT32) và Legacy BIOS (Active Partition)
:: ====================================================================

echo [TXA WinSetup] Đang quét và kiểm tra hệ thống khởi động Windows...

set /p WINDRIVE=Nhập ký tự ổ đĩa chứa Windows (Ví dụ C hoặc W): 
if "%WINDRIVE%"=="" set WINDRIVE=C

if not exist "%WINDRIVE%:\Windows\System32" (
    echo [LỖI] Không tìm thấy thư mục %WINDRIVE%:\Windows\System32!
    pause
    exit /b 1
)

echo.
echo [1/3] Đang nạp lại file bootloader qua bcdboot...
bcdboot %WINDRIVE%:\Windows /l vi-VN /s %WINDRIVE%: /f ALL >nul 2>&1
if errorlevel 1 (
    bcdboot %WINDRIVE%:\Windows /l en-US /s %WINDRIVE%: /f ALL
)

echo [2/3] Đang cập nhật BCD store...
bootrec /fixmbr >nul 2>&1
bootrec /fixboot >nul 2>&1
bootrec /rebuildbcd >nul 2>&1

echo [3/3] Hoàn tất quá trình nạp Bootloader thành công!
echo.
pause
