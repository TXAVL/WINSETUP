@echo off
chcp 65001 >nul
:: ====================================================================
:: TXA WinSetup - Công cụ nạp và tiêm Driver Offline bằng DISM
:: Tiêm trực tiếp Driver vào phân vùng Windows trước khi khởi động
:: ====================================================================

echo ====================================================================
echo   TXA WinSetup - Offline DISM Driver Injector Module
echo ====================================================================

set /p WINDRIVE=Ký tự ổ đĩa Windows đích (Mặc định C): 
if "%WINDRIVE%"=="" set WINDRIVE=C

set /p DRVPATH=Đường dẫn thư mục chứa Driver (.inf): 
if "%DRVPATH%"=="" (
    echo [LỖI] Đường dẫn thư mục driver không được để trống!
    pause
    exit /b 1
)

if not exist "%DRVPATH%" (
    echo [LỖI] Thư mục "%DRVPATH%" không tồn tại!
    pause
    exit /b 1
)

echo.
echo Đang nạp Driver vào %WINDRIVE%:\Windows ...
dism /Image:"%WINDRIVE%:\" /Add-Driver /Driver:"%DRVPATH%" /Recurse /ForceUnsigned

if errorlevel 0 (
    echo.
    echo [✓] Đã tiêm toàn bộ Driver vào hệ điều hành thành công!
) else (
    echo.
    echo [!] Quá trình nạp Driver có cảnh báo hoặc lỗi. Vui lòng kiểm tra lại.
)

pause
