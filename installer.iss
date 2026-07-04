#define MyAppName "Baglanti Indirici"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Yusufygc"
#define MyAppExeName "BaglantiIndirici.exe"

[Setup]
AppId={{B6C3B9C0-9D2A-4E9F-9E77-BAGLANTIINDIRICI}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=installer_output
OutputBaseFilename=BaglantiIndirici_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "Masaustu simgesi olustur"; GroupDescription: "Ek simgeler:"

[Files]
; onedir build: exe + tum bagimliliklar (DLL'ler, QtWebEngineProcess.exe,
; kaynaklar, lib\yt_dlp) dist\BaglantiIndirici\ klasorunde. Klasorun tamami {app}'e.
Source: "dist\BaglantiIndirici\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{#MyAppName} baslat"; Flags: nowait postinstall skipifsilent
