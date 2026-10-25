@echo off
chcp 65001 >nul
title TXA WinSetup Production Builder
cd /d "%~dp0"

:: Ngăn hoàn toàn Python sinh file cache .pyc và thư mục __pycache__
set PYTHONDONTWRITEBYTECODE=1

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python build_prod.py %*
    goto :DONE
)

if exist "%LocalAppData%\Programs\Python\Python314\python.exe" (
    "%LocalAppData%\Programs\Python\Python314\python.exe" build_prod.py %*
    goto :DONE
)

echo [LOI] Khong tim thay Python tren he thong!
pause
exit /b 1

:DONE
:: Tự động dọn sạch mọi thư mục __pycache__ nếu có
for /d /r "%~dp0" %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
pause
