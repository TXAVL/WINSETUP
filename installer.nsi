; â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
;  TXA WinSetup â€” NSIS Multi-Language Installer Script
;  Há»— trá»£ Äa ngÃ´n ngá»¯ (Tiáº¿ng Viá»‡t & English), EULA Checkbox,
;  Chá»n thÃ nh pháº§n (Components), Tá»± Ä‘á»™ng so sÃ¡nh phiÃªn báº£n (Auto Upgrade).
; â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Unicode True
RequestExecutionLevel admin

!define PRODUCT_NAME "TXA WinSetup"
!define PRODUCT_VERSION "1.5.2"
!define PRODUCT_PUBLISHER "TXA Studio"
!define PRODUCT_WEB_SITE "https://github.com/TXAVL/WINSETUP"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\TXAWinSetup.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor /SOLID lzma

; â”€â”€ Includes â”€â”€
!include "MUI2.nsh"
!include "WordFunc.nsh"
!include "FileFunc.nsh"
!include "LogicLib.nsh"
!include "Sections.nsh"

; â”€â”€ MUI Settings â”€â”€
!define MUI_ABORTWARNING
!define MUI_ICON "assets\icon.ico"
!define MUI_UNICON "assets\icon.ico"

BrandingText "TXA Studio Â© 2026 â€” CÃ i Win Tá»± Äá»™ng"
SetFont "Segoe UI" 9

; LÆ°u vÃ  náº¡p ngÃ´n ngá»¯ Ä‘Ã£ chá»n
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "InstallerLanguage"

; â”€â”€ Trang 1: ChÃ o má»«ng â”€â”€
!define MUI_WELCOMEPAGE_TITLE $(PAGE_WELCOME_TITLE)
!define MUI_WELCOMEPAGE_TEXT $(PAGE_WELCOME_TEXT)
!insertmacro MUI_PAGE_WELCOME

; â”€â”€ Trang 2: Thá»a thuáº­n báº£n quyá»n (Accept EULA Checkbox) â”€â”€
!define MUI_LICENSEPAGE_CHECKBOX
!insertmacro MUI_PAGE_LICENSE $(myLicenseData)

; â”€â”€ Trang 3: Chá»n cÃ¡c má»¥c con (Components Page) â”€â”€
!insertmacro MUI_PAGE_COMPONENTS

; â”€â”€ Trang 4: Chá»n thÆ° má»¥c cÃ i Ä‘áº·t â”€â”€
!insertmacro MUI_PAGE_DIRECTORY

; â”€â”€ Trang 5: Tiáº¿n trÃ¬nh cÃ i Ä‘áº·t â”€â”€
!insertmacro MUI_PAGE_INSTFILES

; â”€â”€ Trang 6: HoÃ n táº¥t â”€â”€
!define MUI_FINISHPAGE_RUN "$INSTDIR\TXAWinSetup.exe"
!define MUI_FINISHPAGE_RUN_TEXT $(FINISH_RUN_TEXT)
!insertmacro MUI_PAGE_FINISH

; â”€â”€ Trang gá»¡ cÃ i Ä‘áº·t â”€â”€
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; â”€â”€ Khai bÃ¡o ngÃ´n ngá»¯ â”€â”€
!insertmacro MUI_LANGUAGE "Vietnamese"
!insertmacro MUI_LANGUAGE "English"

; â”€â”€ Dá»¯ liá»‡u file báº£n quyá»n theo tá»«ng ngÃ´n ngá»¯ (RTF Unicode chá»‘ng lá»—i font tuyá»‡t Ä‘á»‘i) â”€â”€
LicenseLangString myLicenseData ${LANG_VIETNAMESE} "assets\license_vi.rtf"
LicenseLangString myLicenseData ${LANG_ENGLISH} "assets\license_en.rtf"

; â”€â”€ ThÃ´ng tin phiÃªn báº£n & Metadata Windows (File Properties / Details) â”€â”€
VIProductVersion "1.5.2.0"
VIFileVersion "1.5.2.0"

VIAddVersionKey /LANG=${LANG_VIETNAMESE} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "LegalCopyright" "Copyright Â© 2026 TXA Studio"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "FileDescription" "TXA WinSetup â€” TrÃ¬nh cÃ i Ä‘áº·t Windows Tá»± Äá»™ng"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "FileVersion" "${PRODUCT_VERSION}.0"
VIAddVersionKey /LANG=${LANG_VIETNAMESE} "OriginalFilename" "TXAWinSetup_Setup.exe"

VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductVersion" "${PRODUCT_VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${PRODUCT_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "Copyright Â© 2026 TXA Studio"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "TXA WinSetup â€” Automated Windows Installer Setup"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${PRODUCT_VERSION}.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "OriginalFilename" "TXAWinSetup_Setup.exe"

; â”€â”€ Chuá»—i vÄƒn báº£n Ä‘a ngÃ´n ngá»¯ (Multilingual LangStrings) â”€â”€
LangString PAGE_WELCOME_TITLE ${LANG_VIETNAMESE} "ChÃ o má»«ng Ä‘áº¿n vá»›i TrÃ¬nh cÃ i Ä‘áº·t ${PRODUCT_NAME} v${PRODUCT_VERSION}"
LangString PAGE_WELCOME_TITLE ${LANG_ENGLISH} "Welcome to the ${PRODUCT_NAME} v${PRODUCT_VERSION} Setup Wizard"

LangString PAGE_WELCOME_TEXT ${LANG_VIETNAMESE} "CÃ´ng cá»¥ cÃ i Ä‘áº·t Windows tá»± Ä‘á»™ng thÃ´ng minh TXA WinSetup.$\r$\nTÆ°Æ¡ng thÃ­ch hoÃ n háº£o cáº£ Windows thÆ°á»ng láº«n mÃ´i trÆ°á»ng USB Cá»©u há»™ WinPE.$\r$\n$\r$\nKhuyáº¿n nghá»‹ Ä‘Ã³ng cÃ¡c á»©ng dá»¥ng khÃ¡c trÆ°á»›c khi tiáº¿p tá»¥c.$\r$\n$\r$\nNháº¥n 'Tiáº¿p tá»¥c' Ä‘á»ƒ báº¯t Ä‘áº§u."
LangString PAGE_WELCOME_TEXT ${LANG_ENGLISH} "Smart automated Windows installer tool TXA WinSetup.$\r$\nFully compatible with both normal Windows and WinPE Rescue environments.$\r$\n$\r$\nIt is recommended that you close other applications before continuing.$\r$\n$\r$\nClick 'Next' to begin."

LangString FINISH_RUN_TEXT ${LANG_VIETNAMESE} "Khá»Ÿi cháº¡y ${PRODUCT_NAME} ngay"
LangString FINISH_RUN_TEXT ${LANG_ENGLISH} "Launch ${PRODUCT_NAME} now"

LangString SEC_NAME_CORE ${LANG_VIETNAMESE} "${PRODUCT_NAME} (Báº¯t buá»™c)"
LangString SEC_NAME_CORE ${LANG_ENGLISH} "${PRODUCT_NAME} Core (Required)"

LangString SEC_NAME_DESKTOP ${LANG_VIETNAMESE} "Biá»ƒu tÆ°á»£ng ngoÃ i mÃ n hÃ¬nh Desktop"
LangString SEC_NAME_DESKTOP ${LANG_ENGLISH} "Desktop Shortcut"

LangString SEC_NAME_STARTMENU ${LANG_VIETNAMESE} "Lá»‘i táº¯t trong Start Menu"
LangString SEC_NAME_STARTMENU ${LANG_ENGLISH} "Start Menu Shortcuts"

LangString DESC_SEC01 ${LANG_VIETNAMESE} "Tá»‡p chÆ°Æ¡ng trÃ¬nh chÃ­nh TXA WinSetup vÃ  cÃ¡c tiá»‡n Ã­ch cáº§n thiáº¿t (Báº¯t buá»™c)."
LangString DESC_SEC01 ${LANG_ENGLISH} "Core TXA WinSetup program files and necessary components (Required)."

LangString DESC_DESKTOP ${LANG_VIETNAMESE} "Táº¡o biá»ƒu tÆ°á»£ng lá»‘i táº¯t ngoÃ i mÃ n hÃ¬nh Desktop Ä‘á»ƒ má»Ÿ nhanh á»©ng dá»¥ng."
LangString DESC_DESKTOP ${LANG_ENGLISH} "Create a shortcut icon on your Desktop for quick access."

LangString DESC_STARTMENU ${LANG_VIETNAMESE} "Táº¡o thÆ° má»¥c lá»‘i táº¯t TXA WinSetup trong menu Start cá»§a há»‡ Ä‘iá»u hÃ nh."
LangString DESC_STARTMENU ${LANG_ENGLISH} "Create TXA WinSetup shortcut entries in the Windows Start Menu."

LangString MSG_DOWNGRADE_ERROR ${LANG_VIETNAMESE} "PhÃ¡t hiá»‡n phiÃªn báº£n má»›i hÆ¡n ($R0) Ä‘Ã£ Ä‘Æ°á»£c cÃ i Ä‘áº·t trÃªn mÃ¡y tÃ­nh cá»§a báº¡n.$\r$\n$\r$\nKhÃ´ng thá»ƒ cÃ i Ä‘áº·t phiÃªn báº£n cÅ© hÆ¡n (${PRODUCT_VERSION}).$\r$\nVui lÃ²ng gá»¡ cÃ i Ä‘áº·t phiÃªn báº£n hiá»‡n táº¡i trÆ°á»›c náº¿u muá»‘n háº¡ cáº¥p."
LangString MSG_DOWNGRADE_ERROR ${LANG_ENGLISH} "A newer version ($R0) is already installed on your computer.$\r$\n$\r$\nCannot downgrade to version ${PRODUCT_VERSION}.$\r$\nPlease uninstall the existing version first."

LangString MSG_ALREADY_INSTALLED ${LANG_VIETNAMESE} "PhiÃªn báº£n ${PRODUCT_NAME} v${PRODUCT_VERSION} Ä‘Ã£ cÃ³ sáºµn trÃªn mÃ¡y tÃ­nh cá»§a báº¡n.$\r$\n$\r$\nBáº¡n cÃ³ muá»‘n cÃ i Ä‘áº·t láº¡i / cáº­p nháº­t láº¡i (Reinstall / Reupdate) khÃ´ng?$\r$\nâ€¢ Chá»n [YES] Ä‘á»ƒ CÃ i Ä‘áº·t láº¡i / Cáº­p nháº­t láº¡i$\r$\nâ€¢ Chá»n [NO] Ä‘á»ƒ ÄÃ³ng trÃ¬nh cÃ i Ä‘áº·t"
LangString MSG_ALREADY_INSTALLED ${LANG_ENGLISH} "${PRODUCT_NAME} v${PRODUCT_VERSION} is already installed on your computer.$\r$\n$\r$\nWould you like to reinstall / re-update the application?$\r$\nâ€¢ Click [YES] to Reinstall / Reupdate$\r$\nâ€¢ Click [NO] to Close installer"

LangString UNINST_SUCCESS ${LANG_VIETNAMESE} "$(^Name) Ä‘Ã£ Ä‘Æ°á»£c gá»¡ cÃ i Ä‘áº·t hoÃ n toÃ n khá»i mÃ¡y tÃ­nh cá»§a báº¡n."
LangString UNINST_SUCCESS ${LANG_ENGLISH} "$(^Name) was successfully uninstalled from your computer."

LangString UNINST_CONFIRM ${LANG_VIETNAMESE} "Báº¡n cÃ³ cháº¯c cháº¯n muá»‘n gá»¡ bá» hoÃ n toÃ n $(^Name) khÃ´ng?"
LangString UNINST_CONFIRM ${LANG_ENGLISH} "Are you sure you want to completely remove $(^Name)?"

LangString MSG_APP_RUNNING ${LANG_VIETNAMESE} "${PRODUCT_NAME} Ä‘ang cháº¡y trÃªn mÃ¡y tÃ­nh cá»§a báº¡n.$\r$\nVui lÃ²ng Ä‘Ã³ng á»©ng dá»¥ng trÆ°á»›c khi tiáº¿p tá»¥c, hoáº·c nháº¥n [OK] Ä‘á»ƒ tá»± Ä‘á»™ng Ä‘Ã³ng."
LangString MSG_APP_RUNNING ${LANG_ENGLISH} "${PRODUCT_NAME} is currently running on your computer.$\r$\nPlease close the application before continuing, or click [OK] to automatically close it."

LangString SEC_NAME_CONTEXT ${LANG_VIETNAMESE} "TÃ­ch há»£p Menu chuá»™t pháº£i Windows"
LangString SEC_NAME_CONTEXT ${LANG_ENGLISH} "Windows Explorer Context Menu"

LangString DESC_CONTEXT ${LANG_VIETNAMESE} "ThÃªm má»¥c 'Má»Ÿ báº±ng TXA WinSetup' khi click chuá»™t pháº£i vÃ o file .ISO, .WIM, .ESD."
LangString DESC_CONTEXT ${LANG_ENGLISH} "Add 'Open with TXA WinSetup' entry to context menu when right-clicking .ISO, .WIM, .ESD files."

LangString CONTEXT_OPEN ${LANG_VIETNAMESE} "Má»Ÿ báº±ng TXA WinSetup"
LangString CONTEXT_OPEN ${LANG_ENGLISH} "Open with TXA WinSetup"

LangString SEC_NAME_STARTUP ${LANG_VIETNAMESE} "Khá»Ÿi Ä‘á»™ng cÃ¹ng Windows"
LangString SEC_NAME_STARTUP ${LANG_ENGLISH} "Start with Windows"

LangString DESC_STARTUP ${LANG_VIETNAMESE} "Tá»± Ä‘á»™ng cháº¡y á»©ng dá»¥ng TXA WinSetup khi khá»Ÿi Ä‘á»™ng Windows."
LangString DESC_STARTUP ${LANG_ENGLISH} "Automatically launch TXA WinSetup on Windows startup."

LangString SEC_NAME_AUTOUPDATE ${LANG_VIETNAMESE} "Tá»± Ä‘á»™ng kiá»ƒm tra báº£n cáº­p nháº­t má»›i"
LangString SEC_NAME_AUTOUPDATE ${LANG_ENGLISH} "Automatically check for updates"

LangString DESC_AUTOUPDATE ${LANG_VIETNAMESE} "Tá»± Ä‘á»™ng kiá»ƒm tra phiÃªn báº£n má»›i tá»« GitHub khi má»Ÿ á»©ng dá»¥ng TXA WinSetup (KhuyÃªn dÃ¹ng)."
LangString DESC_AUTOUPDATE ${LANG_ENGLISH} "Automatically check for new releases on GitHub upon opening TXA WinSetup (Recommended)."

LangString UNINST_CLEAN_DATA ${LANG_VIETNAMESE} "Báº¡n cÃ³ muá»‘n xÃ³a sáº¡ch toÃ n bá»™ cáº¥u hÃ¬nh, lá»‹ch sá»­ nháº­t kÃ½ (log) vÃ  cÃ¡c file táº¡m cá»§a TXA WinSetup khÃ´ng?"
LangString UNINST_CLEAN_DATA ${LANG_ENGLISH} "Would you like to completely delete all configuration history, log files, and temporary data created by TXA WinSetup?"

; â”€â”€ Installer Config â”€â”€
Name "${PRODUCT_NAME} v${PRODUCT_VERSION}"
OutFile "prod\TXAWinSetup_Setup.exe"
InstallDir "$PROGRAMFILES\TXA WinSetup"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; â”€â”€ Initialization & Version Check â”€â”€
Function .onInit
  ; 1. Hiá»ƒn thá»‹ há»™p thoáº¡i chá»n ngÃ´n ngá»¯ (Bá» qua náº¿u cÃ i Ä‘áº·t im láº·ng /S)
  ${IfNot} ${Silent}
    !insertmacro MUI_LANGDLL_DISPLAY
  ${EndIf}

  ; 2. Kiá»ƒm tra náº¿u TXAWinSetup.exe Ä‘ang cháº¡y -> Cáº£nh bÃ¡o hoáº·c Ä‘Ã³ng an toÃ n
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

  ; 3. Äá»c phiÃªn báº£n Ä‘Ã£ cÃ i trong Registry
  ReadRegStr $R0 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion"
  ReadRegStr $R1 ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "InstallLocation"
  ${If} $R1 == ""
    ReadRegStr $R1 HKLM "${PRODUCT_DIR_REGKEY}" ""
    ${GetParent} "$R1" $R1
  ${EndIf}

  ${If} $R0 != ""
    ; So sÃ¡nh phiÃªn báº£n bá»™ cÃ i (${PRODUCT_VERSION}) vá»›i phiÃªn báº£n trong mÃ¡y ($R0)
    ${VersionCompare} "${PRODUCT_VERSION}" "$R0" $R2
    ; $R2 = 0: Báº±ng nhau
    ; $R2 = 1: Bá»™ cÃ i má»›i hÆ¡n -> Tá»± Ä‘á»™ng cÃ i Ä‘Ã¨ lÃªn
    ; $R2 = 2: Bá»™ cÃ i cÅ© hÆ¡n -> Cháº·n láº¡i bÃ¡o lá»—i

    ${If} $R2 == 1
      ; File cháº¡y > MÃ¡y: Tá»± Ä‘á»™ng ghi Ä‘Ã¨ vÃ  cÃ i Ä‘Ã¨ tháº³ng lÃªn
      ${If} $R1 != ""
        StrCpy $INSTDIR $R1
      ${EndIf}
    ${ElseIf} $R2 == 2
      ; File cháº¡y < MÃ¡y: Cháº·n láº¡i bÃ¡o lá»—i
      ${IfNot} ${Silent}
        MessageBox MB_ICONSTOP|MB_OK "$(MSG_DOWNGRADE_ERROR)"
      ${EndIf}
      Abort
    ${ElseIf} $R2 == 0
      ; Báº±ng nhau: Má»Ÿ há»™p thoáº¡i chá»n YES (Reinstall / Reupdate) hoáº·c NO (ÄÃ³ng trÃ¬nh cÃ i Ä‘áº·t)
      ${If} ${Silent}
        ${If} $R1 != ""
          StrCpy $INSTDIR $R1
        ${EndIf}
      ${Else}
        MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON1 "$(MSG_ALREADY_INSTALLED)" /SD IDYES IDYES do_reinstall
        Abort ; NgÆ°á»i dÃ¹ng báº¥m NO -> ÄÃ³ng trÃ¬nh cÃ i Ä‘áº·t

        do_reinstall:
          ${If} $R1 != ""
            StrCpy $INSTDIR $R1
          ${EndIf}
      ${EndIf}
    ${EndIf}
  ${EndIf}
FunctionEnd

; â”€â”€ CÃ¡c má»¥c con (Sections) â”€â”€
Section "!$(SEC_NAME_CORE)" SEC01
  SectionIn RO ; Báº¯t buá»™c, khÃ´ng cho bá» chá»n
  SetOutPath "$INSTDIR"
  SetOverwrite on

  ; CÃ i Ä‘áº·t file thá»±c thi chÃ­nh TXAWinSetup.exe chuáº©n Ä‘á»™c láº­p
  File /oname=TXAWinSetup.exe "prod\TXAWinSetup_Portable.exe"

  ; TÃ­ch há»£p 3 thÆ° má»¥c chá»©c nÄƒng ngÆ°á»i dÃ¹ng cáº§n: unattend, drivers, tweaks
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
  CreateShortCut "$SMPROGRAMS\TXA WinSetup\Gá»¡ cÃ i Ä‘áº·t (Uninstall).lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\TXA WinSetup\Trang chá»§ TXAVL (GitHub).lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section "$(SEC_NAME_CONTEXT)" SEC_CONTEXT
  ; 1. Menu chuá»™t pháº£i Windows Explorer cho file ISO, WIM, ESD
  WriteRegStr HKCR "SystemFileAssociations\.iso\Shell\TXAWinSetup" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "SystemFileAssociations\.iso\Shell\TXAWinSetup" "Icon" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "SystemFileAssociations\.iso\Shell\TXAWinSetup\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  WriteRegStr HKCR "SystemFileAssociations\.wim\Shell\TXAWinSetup" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "SystemFileAssociations\.wim\Shell\TXAWinSetup" "Icon" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "SystemFileAssociations\.wim\Shell\TXAWinSetup\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  WriteRegStr HKCR "SystemFileAssociations\.esd\Shell\TXAWinSetup" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "SystemFileAssociations\.esd\Shell\TXAWinSetup" "Icon" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "SystemFileAssociations\.esd\Shell\TXAWinSetup\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  ; 2. ÄÄƒng kÃ½ Applications\TXAWinSetup.exe Ä‘á»ƒ xuáº¥t hiá»‡n trong há»™p thoáº¡i "Open With" vÃ  báº£ng chá»n á»©ng dá»¥ng cá»§a Windows
  WriteRegStr HKCR "Applications\TXAWinSetup.exe" "" "${PRODUCT_NAME}"
  WriteRegStr HKCR "Applications\TXAWinSetup.exe" "FriendlyAppName" "${PRODUCT_NAME}"
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\SupportedTypes" ".iso" ""
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\SupportedTypes" ".wim" ""
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\SupportedTypes" ".esd" ""
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\shell\open\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'
  WriteRegStr HKCR "Applications\TXAWinSetup.exe\DefaultIcon" "" "$INSTDIR\TXAWinSetup.exe,0"

  ; 3. ÄÄƒng kÃ½ ProgID riÃªng cho TXAWinSetup
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso" "" "ÄÄ©a cÃ i Ä‘áº·t Windows (ISO)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso" "FriendlyTypeName" "ÄÄ©a cÃ i Ä‘áº·t Windows (ISO)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso\DefaultIcon" "" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso\shell\open" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso\shell\open" "FriendlyAppName" "${PRODUCT_NAME}"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.iso\shell\open\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim" "" "áº¢nh cÃ i Ä‘áº·t Windows WIM"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim" "FriendlyTypeName" "áº¢nh cÃ i Ä‘áº·t Windows WIM"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim\DefaultIcon" "" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim\shell\open" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim\shell\open" "FriendlyAppName" "${PRODUCT_NAME}"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.wim\shell\open\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd" "" "áº¢nh cÃ i Ä‘áº·t nÃ©n Windows ESD"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd" "FriendlyTypeName" "áº¢nh cÃ i Ä‘áº·t nÃ©n Windows ESD"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd\DefaultIcon" "" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd\shell\open" "" "$(CONTEXT_OPEN)"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd\shell\open" "FriendlyAppName" "${PRODUCT_NAME}"
  WriteRegStr HKCR "TXAWinSetup.AssocFile.esd\shell\open\command" "" '"$INSTDIR\TXAWinSetup.exe" "%1"'

  ; 4. ÄÄƒng kÃ½ vÃ o OpenWithProgids & OpenWithList Ä‘á»ƒ Windows gá»£i Ã½ má»Ÿ báº±ng TXA WinSetup
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

  ; 5. ÄÄƒng kÃ½ Default Programs Capabilities vá»›i Windows
  WriteRegStr HKLM "SOFTWARE\RegisteredApplications" "${PRODUCT_NAME}" "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities" "ApplicationDescription" "Bá»™ cÃ i Ä‘áº·t vÃ  triá»ƒn khai Windows Tá»± Äá»™ng chuyÃªn nghiá»‡p"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities" "ApplicationName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities" "ApplicationIcon" "$INSTDIR\TXAWinSetup.exe,0"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities\FileAssociations" ".iso" "TXAWinSetup.AssocFile.iso"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities\FileAssociations" ".wim" "TXAWinSetup.AssocFile.wim"
  WriteRegStr HKLM "SOFTWARE\TXA Studio\TXA WinSetup\Capabilities\FileAssociations" ".esd" "TXAWinSetup.AssocFile.esd"

  ; 6. ThÃ´ng bÃ¡o cho Windows Explorer lÃ m má»›i danh sÃ¡ch liÃªn káº¿t táº­p tin ngay láº­p tá»©c
  System::Call 'shell32.dll::SHChangeNotify(i 0x08000000, i 0, i 0, i 0)'
SectionEnd

Section /o "$(SEC_NAME_STARTUP)" SEC_STARTUP
  ; Khá»Ÿi Ä‘á»™ng cÃ¹ng Windows (Máº·c Ä‘á»‹nh khÃ´ng chá»n, ngÆ°á»i dÃ¹ng cÃ³ thá»ƒ tÃ­ch chá»n)
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "TXAWinSetup" '"$INSTDIR\TXAWinSetup.exe"'
SectionEnd

Section "$(SEC_NAME_AUTOUPDATE)" SEC_AUTOUPDATE
  ; Tá»± Ä‘á»™ng kiá»ƒm tra báº£n cáº­p nháº­t (TÃ­ch chá»n sáºµn theo máº·c Ä‘á»‹nh)
SectionEnd

; â”€â”€ Ghi nháº­n Registry sau khi cÃ i â”€â”€
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

  ; Thiáº¿t láº­p tÃ¹y chá»n Tá»± Ä‘á»™ng kiá»ƒm tra báº£n cáº­p nháº­t
  ${If} ${SectionIsSelected} ${SEC_AUTOUPDATE}
    WriteRegDWORD HKCU "Software\TXA Studio\TXA WinSetup" "AutoCheckUpdate" 1
  ${Else}
    WriteRegDWORD HKCU "Software\TXA Studio\TXA WinSetup" "AutoCheckUpdate" 0
  ${EndIf}

  !insertmacro MUI_LANGDLL_SAVELANGUAGE
SectionEnd

; â”€â”€ MÃ´ táº£ cho tá»«ng Component â”€â”€
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} $(DESC_SEC01)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_DESKTOP} $(DESC_DESKTOP)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTMENU} $(DESC_STARTMENU)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_CONTEXT} $(DESC_CONTEXT)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_STARTUP} $(DESC_STARTUP)
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC_AUTOUPDATE} $(DESC_AUTOUPDATE)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; â”€â”€ Uninstaller â”€â”€
Function un.onInit
  !insertmacro MUI_UNGETLANGUAGE

  ; Kiá»ƒm tra náº¿u TXAWinSetup.exe Ä‘ang cháº¡y trÆ°á»›c khi gá»¡
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
  ; XÃ³a Menu chuá»™t pháº£i Context Menu
  DeleteRegKey HKCR "SystemFileAssociations\.iso\Shell\TXAWinSetup"
  DeleteRegKey HKCR "SystemFileAssociations\.wim\Shell\TXAWinSetup"
  DeleteRegKey HKCR "SystemFileAssociations\.esd\Shell\TXAWinSetup"

  ; XÃ³a liÃªn káº¿t File Association & Open With
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

  ; LÃ m má»›i Windows Shell
  System::Call 'shell32.dll::SHChangeNotify(i 0x08000000, i 0, i 0, i 0)'

  ; XÃ³a má»¥c khá»Ÿi Ä‘á»™ng cÃ¹ng Windows
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "TXAWinSetup"

  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\Uninstall.exe"
  Delete "$INSTDIR\TXAWinSetup.exe"

  Delete "$SMPROGRAMS\TXA WinSetup\TXA WinSetup.lnk"
  Delete "$SMPROGRAMS\TXA WinSetup\Gá»¡ cÃ i Ä‘áº·t (Uninstall).lnk"
  Delete "$SMPROGRAMS\TXA WinSetup\Trang chá»§ TXAVL (GitHub).lnk"
  Delete "$SMPROGRAMS\TXA WinSetup\Trang chá»§ TXA Studio.lnk"
  RMDir "$SMPROGRAMS\TXA WinSetup"

  Delete "$DESKTOP\TXA WinSetup.lnk"

  RMDir /r "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"

  ; TÃ¹y chá»n gá»¡ cÃ i Ä‘áº·t sáº¡ch sáº½ (Clean Uninstall)
  ${IfNot} ${Silent}
    MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "$(UNINST_CLEAN_DATA)" /SD IDNO IDNO skip_clean
      RMDir /r "$LOCALAPPDATA\TXAWinSetup"
      RMDir /r "$TEMP\TXAWinSetup"
      DeleteRegKey HKCU "Software\TXA Studio\TXA WinSetup"
    skip_clean:
  ${EndIf}

  SetAutoClose true
SectionEnd
