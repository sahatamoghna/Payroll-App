; ——————————————————————————————————————————————
; Payroll App Installer Script
; ——————————————————————————————————————————————

[Setup]
; AppId removed
AppName=Payroll App
AppVersion=1.0.0
AppPublisher=Tamoghna Saha
DefaultDirName={commonpf}\Payroll App
DefaultGroupName=Payroll App
OutputDir=.
OutputBaseFilename=PayrollAppInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
SetupIconFile=logo.ico
UninstallDisplayIcon={app}\PayrollApp.exe
UninstallDisplayName=Payroll App 1.0.0;
    
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Main executable—everything’s bundled inside PayrollApp.exe
Source: "dist\PayrollApp.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcuts
Name: "{group}\Payroll App"; Filename: "{app}\PayrollApp.exe"
Name: "{group}\Uninstall Payroll App"; Filename: "{uninstallexe}"
; Optional Desktop shortcut
Name: "{userdesktop}\Payroll App"; Filename: "{app}\PayrollApp.exe"; Tasks: desktopicon

[Run]
; Offer to launch immediately after install
Filename: "{app}\PayrollApp.exe"; Description: "Launch Payroll App"; Flags: nowait postinstall skipifsilent
