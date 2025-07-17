@echo off
echo ========================================
echo Sourcehold Maps Converter Builder
echo ========================================
echo.

echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

echo.
echo Starting build process...
python build_installer.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
) else (
    echo.
    echo Build completed successfully!
    echo Installer created: SourceholdMapsConverter-Setup.exe
    echo.
    pause
)