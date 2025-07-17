; Sourcehold Maps Converter Installer
; NSIS Script for creating a single installer with all dependencies

!define PRODUCT_NAME "Sourcehold Maps Converter"
!define PRODUCT_VERSION "1.1.0"
!define PRODUCT_PUBLISHER "Sourcehold Team"
!define PRODUCT_WEB_SITE "https://github.com/sourcehold/sourcehold-maps"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\sourcehold-converter.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"
!include "nsDialogs.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!include "StrFunc.nsh"
${StrLoc}

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "LICENSE"
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\sourcehold-converter.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Russian"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "SourceholdMapsConverter-Setup.exe"
InstallDir "$PROGRAMFILES\Sourcehold Maps Converter"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

; Variables
Var PythonInstalled
Var VCRedistInstalled
Var DotNetInstalled

Section "Main Application" SEC01
  SectionIn RO
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  
  ; Main application files
  File "dist\sourcehold-converter.exe"
  File "dist\sourcehold-converter-cli.exe"
  File "README.md"
  File "LICENSE"
  
  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\Sourcehold Maps Converter.lnk" "$INSTDIR\sourcehold-converter.exe"
  
  ; Create start menu shortcut
  CreateDirectory "$SMPROGRAMS\Sourcehold Maps Converter"
  CreateShortCut "$SMPROGRAMS\Sourcehold Maps Converter\Sourcehold Maps Converter.lnk" "$INSTDIR\sourcehold-converter.exe"
  CreateShortCut "$SMPROGRAMS\Sourcehold Maps Converter\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section "Python Runtime" SEC02
  SectionIn RO
  DetailPrint "Checking Python installation..."
  
  ; Check if Python 3.8+ is installed
  nsExec::ExecToStack 'python --version'
  Pop $0
  Pop $1
  
  ${If} $0 == 0
    ; Python is installed, check version
    ${If} ${StrContains} "Python 3.8" $1
    ${OrIf} $1 Contains "Python 3.9"
    ${OrIf} $1 Contains "Python 3.10"
    ${OrIf} $1 Contains "Python 3.11"
    ${OrIf} $1 Contains "Python 3.12"
      StrCpy $PythonInstalled "1"
      DetailPrint "Python is already installed: $1"
    ${Else}
      DetailPrint "Python version too old: $1"
      StrCpy $PythonInstalled "0"
    ${EndIf}
  ${Else}
    DetailPrint "Python not found"
    StrCpy $PythonInstalled "0"
  ${EndIf}
  
  ${If} $PythonInstalled == "0"
    DetailPrint "Installing Python 3.11..."
    SetOutPath "$TEMP"
    File "dependencies\python-3.11.8-amd64.exe"
    ExecWait '"$TEMP\python-3.11.8-amd64.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0'
    Delete "$TEMP\python-3.11.8-amd64.exe"
  ${EndIf}
SectionEnd

Section "Visual C++ Redistributable" SEC03
  SectionIn RO
  DetailPrint "Checking Visual C++ Redistributable..."
  
  ; Check if VC++ Redistributable is installed
  ReadRegStr $0 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" "Version"
  ${If} $0 != ""
    StrCpy $VCRedistInstalled "1"
    DetailPrint "Visual C++ Redistributable is already installed"
  ${Else}
    StrCpy $VCRedistInstalled "0"
  ${EndIf}
  
  ${If} $VCRedistInstalled == "0"
    DetailPrint "Installing Visual C++ Redistributable..."
    SetOutPath "$TEMP"
    File "dependencies\vc_redist.x64.exe"
    ExecWait '"$TEMP\vc_redist.x64.exe" /quiet /norestart'
    Delete "$TEMP\vc_redist.x64.exe"
  ${EndIf}
SectionEnd

Section "Python Dependencies" SEC04
  SectionIn RO
  DetailPrint "Installing Python dependencies..."
  
  ; Install required Python packages
  nsExec::ExecToStack 'python -m pip install --upgrade pip'
  Pop $0
  
  nsExec::ExecToStack 'python -m pip install Pillow pymem dclimplode numpy opencv-python'
  Pop $0
  
  ${If} $0 != 0
    DetailPrint "Error installing Python dependencies"
    MessageBox MB_OK|MB_ICONSTOP "Failed to install Python dependencies. Please check your internet connection and try again."
  ${EndIf}
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\Sourcehold Maps Converter\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\sourcehold-converter.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\sourcehold-converter.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Main application files and shortcuts"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "Python 3.11 runtime (required for the application)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Visual C++ Redistributable 2015-2022 (required for Python packages)"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC04} "Python packages: Pillow, pymem, dclimplode, numpy, opencv-python (includes AIV conversion support)"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\sourcehold-converter.exe"
  Delete "$INSTDIR\README.md"
  Delete "$INSTDIR\LICENSE"

  Delete "$SMPROGRAMS\Sourcehold Maps Converter\Uninstall.lnk"
  Delete "$SMPROGRAMS\Sourcehold Maps Converter\Website.lnk"
  Delete "$SMPROGRAMS\Sourcehold Maps Converter\Sourcehold Maps Converter.lnk"

  RMDir "$SMPROGRAMS\Sourcehold Maps Converter"
  RMDir "$INSTDIR"

  Delete "$DESKTOP\Sourcehold Maps Converter.lnk"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
