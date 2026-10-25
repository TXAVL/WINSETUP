"""
Tạo unattend.xml — bỏ qua OOBE, tạo local account, bypass TPM/SecureBoot
"""
from pathlib import Path
import xml.etree.ElementTree as ET

# Các lệnh Bypass TPM, SecureBoot, RAM, CPU chuyên dụng của TXA
TPM_BYPASS_REG = """
<RunSynchronousCommand wcm:action="add">
    <Order>1</Order>
    <Path>reg add HKLM\\SYSTEM\\Setup\\MoSetup /v AllowUpgradesWithUnsupportedTPMOrCPU /t REG_DWORD /d 1 /f</Path>
</RunSynchronousCommand>
<RunSynchronousCommand wcm:action="add">
    <Order>2</Order>
    <Path>reg add HKLM\\SYSTEM\\Setup\\LabConfig /v BypassTPMCheck /t REG_DWORD /d 1 /f</Path>
</RunSynchronousCommand>
<RunSynchronousCommand wcm:action="add">
    <Order>3</Order>
    <Path>reg add HKLM\\SYSTEM\\Setup\\LabConfig /v BypassSecureBootCheck /t REG_DWORD /d 1 /f</Path>
</RunSynchronousCommand>
<RunSynchronousCommand wcm:action="add">
    <Order>4</Order>
    <Path>reg add HKLM\\SYSTEM\\Setup\\LabConfig /v BypassRAMCheck /t REG_DWORD /d 1 /f</Path>
</RunSynchronousCommand>
<RunSynchronousCommand wcm:action="add">
    <Order>5</Order>
    <Path>reg add HKLM\\SYSTEM\\Setup\\LabConfig /v BypassCPUCheck /t REG_DWORD /d 1 /f</Path>
</RunSynchronousCommand>
<RunSynchronousCommand wcm:action="add">
    <Order>6</Order>
    <Path>reg add HKLM\\SYSTEM\\Setup\\LabConfig /v BypassStorageCheck /t REG_DWORD /d 1 /f</Path>
</RunSynchronousCommand>
<RunSynchronousCommand wcm:action="add">
    <Order>7</Order>
    <Path>reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\OOBE /v BypassNRO /t REG_DWORD /d 1 /f</Path>
</RunSynchronousCommand>
"""

def generate_setup_complete(
    classic_context_menu: bool = True,
    disable_bitlocker: bool = True,
    disable_telemetry: bool = True,
    disable_hibernation: bool = True,
    disable_search_indexing: bool = False,
    high_performance_power: bool = True,
    auto_activate: bool = True,
    product_key: str = "",
) -> str:
    """Tạo nội dung SetupComplete.cmd để chạy ngầm tinh chỉnh sau khi cài xong."""
    cmds = ["@echo off", "chcp 65001 >nul", ":: TXA WinSetup - Post Install Tweaks"]

    if disable_bitlocker:
        cmds.append(":: [TXA] Tat ma hoa o dia tu dong BitLocker")
        cmds.append('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\BitLocker" /v PreventDeviceEncryption /t REG_DWORD /d 1 /f >nul 2>&1')

    if disable_telemetry:
        cmds.append(":: [TXA] Tat theo doi Telemetry va quang cao")
        cmds.append('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f >nul 2>&1')
        cmds.append('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\AdvertisingInfo" /v DisabledByGroupPolicy /t REG_DWORD /d 1 /f >nul 2>&1')

    if classic_context_menu:
        cmds.append(":: [TXA] Khoi phuc Menu chuot phai co dien Windows 10 tren Win 11")
        cmds.append('reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve >nul 2>&1')
        cmds.append('reg add "HKU\\.DEFAULT\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f /ve >nul 2>&1')

    if disable_hibernation:
        cmds.append(":: [TXA] Tat che do ngu dong de tiet kiem o C:")
        cmds.append("powercfg -h off >nul 2>&1")

    if disable_search_indexing:
        cmds.append(":: [TXA] Tat Search Indexing giam 100% Disk")
        cmds.append("sc config WSearch start= disabled >nul 2>&1")
        cmds.append("net stop WSearch >nul 2>&1")

    if high_performance_power:
        cmds.append(":: [TXA] Bat che do nguon High Performance")
        cmds.append("powercfg -duplicatescheme 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1")
        cmds.append("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1")

    if auto_activate and product_key:
        cmds.append(":: [TXA] Tu dong kich hoat ban quyen")
        cmds.append(f'cscript //nologo %windir%\\system32\\slmgr.vbs /ipk {product_key} >nul 2>&1')
        cmds.append('cscript //nologo %windir%\\system32\\slmgr.vbs /ato >nul 2>&1')

    cmds.append(":: [TXA] Nap va thuc thi toan bo file Tweaks .reg duoc chon")
    cmds.append('if exist "%~dp0Tweaks" (')
    cmds.append('    for %%f in ("%~dp0Tweaks\\*.reg") do (')
    cmds.append('        regedit.exe /s "%%f" >nul 2>&1')
    cmds.append('    )')
    cmds.append(')')

    cmds.append("exit /b 0")
    return "\r\n".join(cmds) + "\r\n"

def generate(
    username: str,
    password: str,
    computer_name: str,
    timezone: str = "SE Asia Standard Time",
    language: str = "en-US",
    product_key: str = "",
    bypass_tpm: bool = True,
    auto_logon: bool = True,
    runonce_cmd: str = "",
    output_path: str = "",
) -> str:
    """
    Tạo unattend.xml hoàn chỉnh.
    Trả về nội dung XML dạng string.
    """
    # Escape XML special chars
    def xe(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

    key_section = f"<ProductKey>{xe(product_key)}</ProductKey>" if product_key else ""

    tpm_section = ""
    if bypass_tpm:
        tpm_section = TPM_BYPASS_REG

    runonce_section = ""
    if runonce_cmd:
        runonce_section = f"""
        <FirstLogonCommands>
            <SynchronousCommand wcm:action="add">
                <Order>1</Order>
                <CommandLine>{xe(runonce_cmd)}</CommandLine>
                <RequiresUserInput>false</RequiresUserInput>
            </SynchronousCommand>
        </FirstLogonCommands>"""

    xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend"
          xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">

  <!-- ════════════════════════════════════════════════
       TXA WinSetup — Auto Install Configuration
       Generated by TXA WinSetup Tool
       ════════════════════════════════════════════════ -->

  <!-- windowsPE: Cài đặt Windows trên đĩa -->
  <settings pass="windowsPE">
    <component name="Microsoft-Windows-International-Core-WinPE"
               processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35"
               language="neutral" versionScope="nonSxS">
      <SetupUILanguage>
        <UILanguage>{language}</UILanguage>
      </SetupUILanguage>
      <InputLocale>{language}</InputLocale>
      <SystemLocale>{language}</SystemLocale>
      <UILanguage>{language}</UILanguage>
      <UserLocale>{language}</UserLocale>
    </component>

    <component name="Microsoft-Windows-Setup"
               processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35"
               language="neutral" versionScope="nonSxS">
      {key_section}
      <ImageInstall>
        <OSImage>
          <InstallTo>
            <DiskID>0</DiskID>
            <PartitionID>3</PartitionID>
          </InstallTo>
          <WillShowUI>OnError</WillShowUI>
        </OSImage>
      </ImageInstall>
      <UserData>
        <ProductKey>
          <WillShowUI>Never</WillShowUI>
        </ProductKey>
        <AcceptEula>true</AcceptEula>
      </UserData>
      <RunSynchronous>{tpm_section}
      </RunSynchronous>
    </component>
  </settings>

  <!-- offlineServicing: Áp dụng trước khi boot lần đầu -->
  <settings pass="offlineServicing">
    <component name="Microsoft-Windows-LUA-Settings"
               processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35"
               language="neutral" versionScope="nonSxS">
      <EnableLUA>false</EnableLUA>
    </component>
  </settings>

  <!-- specialize: Cài đặt máy tính -->
  <settings pass="specialize">
    <component name="Microsoft-Windows-Shell-Setup"
               processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35"
               language="neutral" versionScope="nonSxS">
      <ComputerName>{xe(computer_name)}</ComputerName>
      <TimeZone>{xe(timezone)}</TimeZone>
      <RegisteredOrganization>TXA</RegisteredOrganization>
      <RegisteredOwner>{xe(username)}</RegisteredOwner>
    </component>

    <component name="Microsoft-Windows-International-Core"
               processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35"
               language="neutral" versionScope="nonSxS">
      <InputLocale>{language}</InputLocale>
      <SystemLocale>{language}</SystemLocale>
      <UILanguage>{language}</UILanguage>
      <UserLocale>{language}</UserLocale>
    </component>
  </settings>

  <!-- oobeSystem: Bỏ qua toàn bộ OOBE, tạo tài khoản local -->
  <settings pass="oobeSystem">
    <component name="Microsoft-Windows-Shell-Setup"
               processorArchitecture="amd64"
               publicKeyToken="31bf3856ad364e35"
               language="neutral" versionScope="nonSxS">
      <OOBE>
        <HideEULAPage>true</HideEULAPage>
        <HideLocalAccountScreen>false</HideLocalAccountScreen>
        <HideOEMRegistrationScreen>true</HideOEMRegistrationScreen>
        <HideOnlineAccountScreens>true</HideOnlineAccountScreens>
        <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
        <NetworkLocation>Work</NetworkLocation>
        <ProtectYourPC>3</ProtectYourPC>
        <SkipMachineOOBE>true</SkipMachineOOBE>
        <SkipUserOOBE>true</SkipUserOOBE>
      </OOBE>
      <UserAccounts>
        <LocalAccounts>
          <LocalAccount wcm:action="add">
            <Password>
              <Value>{xe(password)}</Value>
              <PlainText>true</PlainText>
            </Password>
            <Description>TXA Setup Account</Description>
            <DisplayName>{xe(username)}</DisplayName>
            <Group>Administrators</Group>
            <Name>{xe(username)}</Name>
          </LocalAccount>
        </LocalAccounts>
      </UserAccounts>
      {"<AutoLogon><Password><Value>" + xe(password) + "</Value><PlainText>true</PlainText></Password><Enabled>true</Enabled><LogonCount>5</LogonCount><Username>" + xe(username) + "</Username></AutoLogon>" if auto_logon else ""}{runonce_section}
    </component>
  </settings>

</unattend>
"""
    if output_path:
        Path(output_path).write_text(xml_content, encoding="utf-8")
    return xml_content
