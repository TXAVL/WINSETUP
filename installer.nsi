; ════════════════════════════════════════════════════════════════
;  TXA WinSetup — NSIS Multi-Language Installer Script
;  Hỗ trợ Đa ngôn ngữ (Tiếng Việt & English), EULA Checkbox,
;  Chọn thành phần (Components), Tự động so sánh phiên bản (Auto Upgrade).
; ════════════════════════════════════════════════════════════════

Unicode True
RequestExecutionLevel admin

!define PRODUCT_NAME "TXA WinSetup"
!define PRODUCT_VERSION "1.3.0"
!define PRODUCT_PUBLISHER "TXA Studio"
!define PRODUCT_WEB_SITE "https://github.com/TXAVL/WINSETUP"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\TXAWinSetup.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor /SOLID lzma

; ── Includes ──
!include "MUI2.nsh"
!include "WordFunc.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "Sections.nsh"

; ── MUI Settings ──
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icon.ico"
!define MUI_UNICON "assets\icon.ico"

BrandingText "TXA Studio © 2026 — Cài Win Tự Động"
SetFont "Segoe UI" 9

; Lưu và nạp ngôn ngữ đã chọn
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "InstallerLanguage"

; ── Trang 1: Chào mừng ──
!define MUI_WELCOMEPAGE_TITLE $(PAGE_WELCOME_TITLE)
!define MUI_WELCOMEPAGE_TEXT $(PAGE_WELCOME_TEXT)
!insertmacro MUI_PAGE_WELCOME

; ── Trang 2: Thỏa thuận bản quyền (Accept EULA Checkbox) ──
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE $(myLicenseData)

; ── Trang 3: Chọn các mục con (Components Page) ──
!insertmacro MUI_PAGE_COMPONENTS

; ── Trang 4: Chọn thư mục cài đặt ──
!insertmacro MUI_PAGE_DIRECTORY

; ── Trang 5: Tiến trình cài đặt ──
!insertmacro MUI_PAGE_INSTFILES

; ── Trang 6: Hoàn tất ──
!define MUI_FINISHPAGE_RUN "$INSTDIR\TXAWinSetup.exe"
!define MUI_FINISHPAGE_RUN_TEXT $(FINISH_RUN_TEXT)
!insertmacro MUI_PAGE_FINISH

; ── Trang gỡ cài đặt ──
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; ── Khai báo ngôn ngữ ──
!insertmacro MUI_LANGUAGE "Vietnamese"
!insertmacro MUI_LANGUAGE "English"

; ── Dữ liệu file bản quyền theo từng ngôn ngữ (RTF Unicode chống lỗi font tuyệt đối) ──
LicenseLangString myLicenseData ${LANG_VIETNAMESE} "assets\license_vi.rtf"
LicenseLangString myLicenseData ${LANG_ENGLISH} "assets\license_en.rtf"

; ── Thông tin phiên bản & Metadata Windows (File Properties / Details) ──
VIProductVersion "1.3.0.0"
VIFileVersion "1.3.0.0"

VIAddVersionKey /LANG=${LANG_VIETNAMESE} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "LegalCopyright" "Copyright © 2026 TXA Studio"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "FileDescription" "TXA WinSetup — Trình cài đặt Windows Tự Động"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "FileVersion" "${PRODUCT_VERSION}.0"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "OriginalFilename" "TXAWinSetup_Setup.exe"

VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "Copyright © 2026 TXA Studio"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "TXA WinSetup — Automated Windows Installer Setup"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${PRODUCT_VERSION}.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "OriginalFilename" "TXAWinSetup_Setup.exe"

; ── Chuỗi văn bản đa ngôn ngữ (Multilingual LangStrings) ──
LangString PAGE_WELCOME_TITLE ${LANG_VIETNAMESE} "Chào mừng đến với Trình cài đặt ${PRODUCT_NAME} v${PRODUCT_VERSION}"
LangString PAGE_WELCOME_TITLE ${LANG_ENGLISH} "Welcome to the ${PRODUCT_NAME} v${PRODUCT_VERSION} Setup Wizard"

LangString PAGE_WELCOME_TEXT ${LANG_VIETNAMESE} "Công cụ cài đặt Windows tự động thông minh TXA WinSetup.$\r$\nTương thích hoàn hảo cả Windows thường lẫn môi trường USB Cứu hộ WinPE.$\r$\n$\r$\nKhuyến nghị đóng các ứng dụng khác trước khi tiếp tục.$\r$\n$\r$\nNhấn 'Tiếp tục' để bắt đầu."
LangString PAGE_WELCOME_TEXT ${LANG_ENGLISH} "Smart automated Windows installer tool TXA WinSetup.$\r$\nFully compatible with both normal Windows and WinPE Rescue environments.$\r$\n$\r$\nIt is recommended that you close other applications before continuing.$\r$\n$\r$\nClick 'Next' to begin."

LangString FINISH_RUN_TEXT ${LANG_VIETNAMESE} "Khởi chạy ${PRODUCT_NAME} ngay"
LangString FINISH_RUN_TEXT ${LANG_ENGLISH} "Launch ${PRODUCT_NAME} now"

LangString SEC_NAME_CORE ${LANG_VIETNAMESE} "${PRODUCT_NAME} (Bắt buộc)"
LangString SEC_NAME_CORE ${LANG_ENGLISH} "${PRODUCT_NAME} Core (Required)"

LangString SEC_NAME_DESKTOP ${LANG_VIETNAMESE} "Biểu tượng ngoài màn hình Desktop"
LangString SEC_NAME_DESKTOP ${LANG_ENGLISH} "Desktop Shortcut"

LangString SEC_NAME_STARTMENU ${LANG_VIETNAMESE} "Lối tắt trong Start Menu"
LangString SEC_NAME_STARTMENU ${LANG_ENGLISH} "Start Menu Shortcuts"

LangString DESC_SEC01 ${LANG_VIETNAMESE} "Tệp chương trình chính TXA WinSetup và các tiện ích cần thiết (Bắt buộc)."
LangString DESC_SEC01 ${LANG_ENGLISH} "Core TXA WinSetup program files and necessary components (Required)."

LangString DESC_DESKTOP ${LANG_VIETNAMESE} "Tạo biểu tượng lối tắt ngoài màn hình Desktop để mở nhanh ứng dụng."
LangString DESC_DESKTOP ${LANG_ENGLISH} "Create a shortcut icon on your Desktop for quick access."

LangString DESC_STARTMENU ${LANG_VIETNAMESE} "Tạo thư mục lối tắt TXA WinSetup trong menu Start của hệ điều hành."
LangString DESC_STARTMENU ${LANG_ENGLISH} "Create TXA WinSetup shortcut entries in the Windows Start Menu."

LangString MSG_DOWNGRADE_ERROR ${LANG_VIETNAMESE} "Phát hiện phiên bản mới hơn ($R0) đã được cài đặt trên máy tính của bạn.$\r$\n$\r$\nKhông thể cài đặt phiên bản cũ hơn (${PRODUCT_VERSION}).$\r$\nVui lòng gỡ cài đặt phiên bản hiện tại trước nếu muốn hạ cấp."
LangString MSG_DOWNGRADE_ERROR ${LANG_ENGLISH} "A newer version ($R0) is already installed on your computer.$\r$\n$\r$\nCannot downgrade to version ${PRODUCT_VERSION}.$\r$\nPlease uninstall the existing version first."

LangString MSG_ALREADY_INSTALLED ${LANG_VIETNAMESE} "Phiên bản ${PRODUCT_NAME} v${PRODUCT_VERSION} đã có sẵn trên máy tính của bạn.$\r$\n$\r$\nBạn có muốn cài đặt lại / cập nhật lại (Reinstall / Reupdate) không?$\r$\n• Chọn [YES] để Cài đặt lại / Cập nhật lại$\r$\n• Chọn [NO] để Đóng trình cài đặt"
LangString MSG_ALREADY_INSTALLED ${LANG_ENGLISH} "${PRODUCT_NAME} v${PRODUCT_VERSION} is already installed on your computer.$\r$\n$\r$\nWould you like to reinstall / re-update the application?$\r$\n• Click [YES] to Reinstall / Reupdate$\r$\n• Click [NO] to Close installer"

LangString UNINST_SUCCESS ${LANG_VIETNAMESE} "$(^Name) đã được gỡ cài đặt hoàn toàn khỏi máy tính của bạn."
LangString UNINST_SUCCESS ${LANG_ENGLISH} "$(^Name) was successfully uninstalled from your computer."

LangString UNINST_CONFIRM ${LANG_VIETNAMESE} "Bạn có chắc chắn muốn gỡ bỏ hoàn toàn $(^Name) không?"
LangString UNINST_CONFIRM ${LANG_ENGLISH} "Are you sure you want to completely remove $(^Name)?"

LangString MSG_APP_RUNNING ${LANG_VIETNAMESE} "${PRODUCT_NAME} đang chạy trên máy tính của bạn.$\r$\nVui lòng đóng ứng dụng trước khi tiếp tục, hoặc nhấn [OK] để tự động đóng."
LangString MSG_APP_RUNNING ${LANG_ENGLISH} "${PRODUCT_NAME} is currently running on your computer.$\r$\nPlease close the application before continuing, or click [OK] to automatically close it."

LangString SEC_NAME_CONTEXT ${LANG_VIETNAMESE} "Tích hợp Menu chuột phải Windows"
LangString SEC_NAME_CONTEXT ${LANG_ENGLISH} "Windows Explorer Context Menu"

LangString DESC_CONTEXT ${LANG_VIETNAMESE} "Thêm mục 'Mở bằng TXA WinSetup' khi click chuột phải vào file .ISO, .WIM, .ESD."
LangString DESC_CONTEXT ${LANG_ENGLISH} "Add 'Open with TXA WinSetup' entry to context menu when right-clicking .ISO, .WIM, .ESD files."

LangString CONTEXT_OPEN ${LANG_VIETNAMESE} "Mở bằng TXA WinSetup"
LangString CONTEXT_OPEN ${LANG_ENGLISH} "Open with TXA WinSetup"

LangString SEC_NAME_STARTUP ${LANG_VIETNAMESE} "Khởi động cùng Windows"
LangString SEC_NAME_STARTUP ${LANG_ENGLISH} "Start with Windows"

LangString DESC_STARTUP ${LANG_VIETNAMESE} "Tự động chạy ứng dụng TXA WinSetup khi khởi động Windows."
LangString DESC_STARTUP ${LANG_ENGLISH} "Automatically launch TXA WinSetup on Windows startup."

LangString SEC_NAME_AUTOUPDATE ${LANG_VIETNAMESE} "Tự động kiểm tra bản cập nhật mới"
LangString SEC_NAME_AUTOUPDATE ${LANG_ENGLISH} "Automatically check for updates"

LangString DESC_AUTOUPDATE ${LANG_VIETNAMESE} "Tự động kiểm tra phiên bản mới từ GitHub khi mở ứng dụng TXA WinSetup (Khuyên dùng)."
LangString DESC_AUTOUPDATE ${LANG_ENGLISH} "Automatically check for new releases on GitHub upon opening TXA WinSetup (Recommended)."

LangString UNINST_CLEAN_DATA ${LANG_VIETNAMESE} "Bạn có muốn xóa sạch toàn bộ cấu hình, lịch sử nhật ký (log) và các file tạm của TXA WinSetup không?"
LangString UNINST_CLEAN_DATA ${LANG_ENGLISH} "Would you like to completely delete all configuration history, log files, and temporary data created by TXA WinSetup?"

; ── Installer Config ──
Name "${PRODUCT_NAME} v${PRODUCT_VERSION}"
OutFile "prod\TXAWinSetup_Setup.exe"
InstallDir "$PROGRAMFILES\TXA WinSetup"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; ── Initialization & Version Check ──
Function .onInit
  ; 1. Hiển thị hộp thoại chọn ngôn ngữ (Bỏ qua nếu cài đặt im lặng /S)
  ${IfNot} ${Silent}
    !insertmacro MUI_LANGDLL_DISPLAY
  ${EndIf}

  ; 2. Kiểm tra nếu TXAWinSetup.exe đang chạy -> Cảnh báo hoặc đóng an toàn
  check_running:
    nsExec::ExecToStack 'cmd /c tasklist /FI "IMAGENAME eq TXAWinSetup.exe" 2>NUL | findstr /I "TXAWinSetup.exe"'
    Pop $R4
    Pop $R5
    ${If} $R4 == 0
      ${If} ${Silent}
        nsExec::Exec 'taskkill /F /IM TXAWinSetup.exe /T'
        Sleep 800
      ${Else}
        MessageBox MB_ICONEXCLAMATION|MB_OKCANCEL "$(MSG_APP_RUNNING)" IDOK do_kill IDCANCEL do_abort
        do_kill:
          nsExec::Exec 'taskkill /F /IM TXAWinSetup.exe /T'
          Sleep 800
          Goto check_running
        do_abort:
          Abort
      ${EndIf}
    ${EndIf}

  ; 3. Đọc phiên bản đã cài trong Registry
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion"
  ReadRegStr $R1 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "InstallLocation"
  ${If} $R1 == ""
    ReadRegStr $R1 HKLM "${PRODUCT_DIR_REGKEY}" ""
    ${GetParent} "$R1" $R1
  ${EndIf}

  ${If} $R0 != ""
    ; So sánh phiên bản bộ cài (${PRODUCT_VERSION}) với phiên bản trong máy ($R0)
    ${VersionCompare} "${PRODUCT_VERSION}" "$R0" $R2
    ; $R2 = 0: Bằng nhau
    ; $R2 = 1: Bộ cài mới hơn -> Tự động cài đè lên
    ; $R2 = 2: Bộ cài cũ hơn -> Chặn lại báo lỗi

    ${If} $R2 == 1
      ; File chạy > Máy: Tự động ghi đè và cài đè thẳng lên
      ${If} $R1 != ""
        StrCpy $INSTDIR $R1
      ${EndIf}
    ${ElseIf} $R2 == 2
      ; File chạy < Máy: Chặn lại báo lỗi
      ${IfNot} ${Silent}
        MessageBox MB_ICONSTOP|MB_OK "$(MSG_DOWNGRADE_ERROR)"
      ${EndIf}
      Abort
    ${ElseIf} $R2 == 0
      ; Bằng nhau: Mở hộp thoại chọn YES (Reinstall / Reupdate) hoặc NO (Đóng trình cài đặt)
      ${If} ${Silent}
        ${If} $R1 != ""
          StrCpy $INSTDIR $R1
        ${EndIf}
      ${Else}
        MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON1 "$(MSG_ALREADY_INSTALLED)" /SD IDYES IDYES do_reinstall
        Abort ; Người dùng bấm NO -> Đóng trình cài đặt

        do_reinstall:
          ${If} $R1 != ""
            StrCpy $INSTDIR $R1
          ${EndIf}
      ${EndIf}
    ${EndIf}
  ${EndIf}
FunctionEnd

; ── Các mục con (Sections) ──
Section "!$(SEC_NAME_CORE)" SEC01
  SectionIn RO ; Bắt buộc, không cho bỏ chọn
  SetOutPath "$INSTDIR"
  SetOverwrite on

  ; Cài đặt file thực thi chính TXAWinSetup.exe chuẩn độc lập
  File /oname=TXAWinSetup.exe "prod\TXAWinSetup_Portable.exe"

  ; Tích hợp 3 thư mục chức năng người dùng cần: unattend, drivers, tweaks
  SetOutPath "$INSTDIR\unattend"
  File /r "unattend\*"

  SetOutPath "$INSTDIR\drivers"
  File /r "drivers\*"

  SetOutPath "$INSTDIR\tweaks"
  File /r "tweaks\*"

  SetOutPath "$INSTDIR"
SectionEnd

Section "$(SEC_NAME_DESKTOP)" SEC_DESKTOP
  SetOutPath "$INSTDIR"
  CreateShortCut "$DESKTOP\TXA WinSetup.lnk" "$INSTDIR\TXAWinSetup.exe" "" "$INSTDIR\TXAWinSetup.exe" 0
SectionEnd

Section "$(SEC_NAME_STARTMENU)" SEC_STARTMENU
  SetOutPath "$INSTDIR"
  CreateDirectory "$SMPROGRAMS\TXA WinSetup"
  CreateShortCut "$SMPROGRAMS\TXA WinSetup\TXA WinSetup.lnk" "$INSTDIR\TXAWinSetup.exe" "" "$INSTDIR\TXAWinSetup.exe" 0
  CreateShortCut "$SMPROGRAMS\TXA WinSetup\Gỡ cài đặt (Uninstall).lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\TXA WinSetup\Trang chủ TXAVL (GitHub).lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section "$(SEC_NAME_CONTEXT)" SEC_CONTEXT
  ; 1. Menu chuột phải Windows Explorer cho file ISO, WIM, ESD
  WriteRegStr HKCR "SystemFileAssociations\.iso\Shell\TXAWinSetup" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "SystemFileAssociations\.iso\Shell\TXAWinSetup" "Icon" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "SystemFileAssociations\.iso\Shell\TXAWinSetup\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  WriteRegStr HKCR "SystemFileAssociations\.wim\Shell\TXAWinSetup" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "SystemFileAssociations\.wim\Shell\TXAWinSetup" "Icon" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "SystemFileAssociations\.wim\Shell\TXAWinSetup\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  WriteRegStr HKCR "SystemFileAssociations\.esd\Shell\TXAWinSetup" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "SystemFileAssociations\.esd\Shell\TXAWinSetup" "Icon" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "SystemFileAssociations\.esd\Shell\TXAWinSetup\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  ; 2. Đăng ký Applications\TXAWinSetup.exe để xuất hiện trong hộp thoại "Open With" và bảng chọn ứng dụng của Windows
  WriteRegStr HKCR "Applications\TXAWinSetup.exe" "" "${PRODUCT_NAME}"
  WriteRegStr HKCR "Applications\TXAWinSetup.exe" "FriendlyAppName" "${PRODUCT_NAME}"
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\SupportedTypes" ".iso" ""
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\SupportedTypes" ".wim" ""
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\SupportedTypes" ".esd" ""
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\shell\open\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\DefaultIcon" "" "$INSTDIR\TXAWinSetup.exe,0"

  ; 3. Đăng ký ProgID riêng cho TXAWinSetup
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso" "" "Đĩa cài đặt Windows (ISO)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso" "FriendlyTypeName" "Đĩa cài đặt Windows (ISO)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso\DefaultIcon" "" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso\shell\open" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso\shell\open" "FriendlyAppName" "${PRODUCT_NAME}"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso\shell\open\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim" "" "Ảnh cài đặt Windows WIM"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim" "FriendlyTypeName" "Ảnh cài đặt Windows WIM"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim\DefaultIcon" "" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim\shell\open" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim\shell\open" "FriendlyAppName" "${PRODUCT_NAME}"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim\shell\open\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd" "" "Ảnh cài đặt nén Windows ESD"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd" "FriendlyTypeName" "Ảnh cài đặt nén Windows ESD"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd\DefaultIcon" "" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd\shell\open" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd\shell\open" "FriendlyAppName" "${PRODUCT_NAME}"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd\shell\open\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  ; 4. Đăng ký vào OpenWithProgids & OpenWithList để Windows gợi ý mở bằng TXA WinSetup
  WriteRegStr HKCR ".iso\OpenWithProgids" "TXAWinSetup.AssocFile.iso" ""
  WriteRegStr HKCR ".iso\OpenWithList\TXAWinSetup.exe" "" ""
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.iso\OpenWithProgids" "TXAWinSetup.AssocFile.iso" ""
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.iso\OpenWithList" "TXA" "TXAWinSetup.exe"

  WriteRegStr HKCR ".wim\OpenWithProgids" "TXAWinSetup.AssocFile.wim" ""
  WriteRegStr HKCR ".wim\OpenWithList\TXAWinSetup.exe" "" ""
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.wim\OpenWithProgids" "TXAWinSetup.AssocFile.wim" ""

  WriteRegStr HKCR ".esd\OpenWithProgids" "TXAWinSetup.AssocFile.esd" ""
  WriteRegStr HKCR ".esd\OpenWithList\TXAWinSetup.exe" "" ""
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.esd\OpenWithProgids" "TXAWinSetup.AssocFile.esd" ""

  ; 5. Đăng ký Default Programs Capabilities với Windows
  WriteRegStr HKLM "SOFTWARE\RegisteredApplications" "${PRODUCT_NAME}" "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities" "ApplicationDescription" "Bộ cài đặt và triển khai Windows Tự Động chuyên nghiệp"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities" "ApplicationName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities" "ApplicationIcon" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities\FileAssociations" ".iso" "TXAWinSetup.AssocFile.iso"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities\FileAssociations" ".wim" "TXAWinSetup.AssocFile.wim"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities\FileAssociations" ".esd" "TXAWinSetup.AssocFile.esd"

  ; 6. Thông báo cho Windows Explorer làm mới danh sách liên kết tập tin ngay lập tức
  System::Call 'shell32.dll::SHChangeNotify(i 0x08000000, i 0, i 0, i 0)'
SectionEnd

Section /o "$(SEC_NAME_STARTUP)" SEC_STARTUP
  ; Khởi động cùng Windows (Mặc định không chọn, người dùng có thể tích chọn)
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "TXAWinSetup" '"$INSTDIR\TXAWinSetup.exe"'
SectionEnd

Section "$(SEC_NAME_AUTOUPDATE)" SEC_AUTOUPDATE
  ; Tự động kiểm tra bản cập nhật (Tích chọn sẵn theo mặc định)
SectionEnd

; ── Ghi nhận Registry sau khi cài ──
Section -Post
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\TXAWinSetup.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\TXAWinSetup.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "EstimatedSize" 16384
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "NoModify" 1
  WriteRegDWORD ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "NoRepair" 0
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "HelpLink" "${PRODUCT_WEB_SITE}"

  ; Thiết lập tùy chọn Tự động kiểm tra bản cập nhật
  ${If} ${SectionIsSelected} ${SEC_AUTOUPDATE}
    WriteRegDWORD HKCU "Software\TXA Studio\TXA WinSetup" "AutoCheckUpdate" 1
  ${Else}
    WriteRegDWORD HKCU "Software\TXA Studio\TXA WinSetup" "AutoCheckUpdate" 0
  ${EndIf}

  !insertmacro MUI_LANGDLL_SAVELANGUAGE
SectionEnd

; ── Mô tả cho từng Component ──
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} $(DESC_SEC01)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} $(DESC_DESKTOP)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTMENU} $(DESC_STARTMENU)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_CONTEXT} $(DESC_CONTEXT)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTUP} $(DESC_STARTUP)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_AUTOUPDATE} $(DESC_AUTOUPDATE)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; ── Uninstaller ──
Function un.onInit
  !insertmacro MUI_UNGETLANGUAGE

  ; Kiểm tra nếu TXAWinSetup.exe đang chạy trước khi gỡ
  un_check_running:
    nsExec::ExecToStack 'cmd /c tasklist /FI "IMAGENAME eq TXAWinSetup.exe" 2>NUL | findstr /I "TXAWinSetup.exe"'
    Pop $R4
    Pop $R5
    ${If} $R4 == 0
      MessageBox MB_ICONEXCLAMATION|MB_OKCANCEL "$(MSG_APP_RUNNING)" IDOK un_do_kill IDCANCEL un_do_abort
      un_do_kill:
        nsExec::Exec 'taskkill /F /IM TXAWinSetup.exe /T'
        Sleep 800
        Goto un_check_running
      un_do_abort:
        Abort
    ${EndIf}

  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "$(UNINST_CONFIRM)" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(UNINST_SUCCESS)"
FunctionEnd

Section Uninstall
  ; Xóa Menu chuột phải Context Menu
  DeleteRegKey HKCR "SystemFileAssociations\.iso\Shell\TXAWinSetup"
  DeleteRegKey HKCR "SystemFileAssociations\.wim\Shell\TXAWinSetup"
  DeleteRegKey HKCR "SystemFileAssociations\.esd\Shell\TXAWinSetup"

  ; Xóa liên kết File Association & Open With
  DeleteRegKey HKCR "Applications\TXAWinSetup.exe"
  DeleteRegKey HKCR "TXAWinSetup.AssocFile.iso"
  DeleteRegKey HKCR "TXAWinSetup.AssocFile.wim"
  DeleteRegKey HKCR "TXAWinSetup.AssocFile.esd"
  DeleteRegValue HKCR ".iso\OpenWithProgids" "TXAWinSetup.AssocFile.iso"
  DeleteRegKey HKCR ".iso\OpenWithList\TXAWinSetup.exe"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.iso\OpenWithProgids" "TXAWinSetup.AssocFile.iso"
  DeleteRegValue HKCR ".wim\OpenWithProgids" "TXAWinSetup.AssocFile.wim"
  DeleteRegKey HKCR ".wim\OpenWithList\TXAWinSetup.exe"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.wim\OpenWithProgids" "TXAWinSetup.AssocFile.wim"
  DeleteRegValue HKCR ".esd\OpenWithProgids" "TXAWinSetup.AssocFile.esd"
  DeleteRegKey HKCR ".esd\OpenWithList\TXAWinSetup.exe"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.esd\OpenWithProgids" "TXAWinSetup.AssocFile.esd"
  DeleteRegValue HKLM "SOFTWARE\RegisteredApplications" "${PRODUCT_NAME}"
  DeleteRegKey HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities"

  ; Làm mới Windows Shell
  System::Call 'shell32.dll::SHChangeNotify(i 0x08000000, i 0, i 0, i 0)'

  ; Xóa mục khởi động cùng Windows
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "TXAWinSetup"

  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\Uninstall.exe"
  Delete "$INSTDIR\TXAWinSetup.exe"

  Delete "$SMPROGRAMS\TXA WinSetup\TXA WinSetup.lnk"
  Delete "$SMPROGRAMS\TXA WinSetup\Gỡ cài đặt (Uninstall).lnk"
  Delete "$SMPROGRAMS\TXA WinSetup\Trang chủ TXAVL (GitHub).lnk"
  Delete "$SMPROGRAMS\TXA WinSetup\Trang chủ TXA Studio.lnk"
  RMDir "$SMPROGRAMS\TXA WinSetup"

  Delete "$DESKTOP\TXA WinSetup.lnk"

  RMDir /r "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; Tùy chọn gỡ cài đặt sạch sẽ (Clean Uninstall)
  ${IfNot} ${Silent}
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "$(UNINST_CLEAN_DATA)" /SD IDNO IDNO skip_clean
      RMDir /r "$LOCALAPPDATA\TXAWinSetup"
      RMDir /r "$TEMP\TXAWinSetup"
      DeleteRegKey HKCU "Software\TXA Studio\TXA WinSetup"
    skip_clean:
  ${EndIf}

  SetAutoClose true
SectionEnd
