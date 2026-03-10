@echo off
echo ================================================
echo   SelfMaster - Build EXE
echo ================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Install from https://python.org
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
pip install matplotlib pyinstaller --quiet

echo [2/4] Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/4] Building EXE...
pyinstaller selfmaster.spec --clean --noconfirm

echo [4/4] Done!
echo.
if exist dist\SelfMaster.exe (
    echo SUCCESS! File: dist\SelfMaster.exe
    echo Size: 
    for %%A in (dist\SelfMaster.exe) do echo %%~zA bytes
) else (
    echo [ERROR] Build failed. Check output above.
)

echo.
pause
