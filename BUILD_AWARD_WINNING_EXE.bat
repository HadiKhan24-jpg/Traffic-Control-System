@echo off
echo ====================================================
echo   TRAFFIC CONTROL SYSTEM - One-Click Desktop EXE Builder
echo ====================================================
echo.
echo [1/3] Installing essential requirements...
pip install PyQt5 PyQtWebEngine pyinstaller

echo.
echo [2/3] Building Optimized 3D Binary...
echo (This may take 2-3 minutes)
pyinstaller --noconsole --onefile --icon=NONE --add-data "TrafficSystem3D.html;." --add-data "libs;libs" DesktopLauncher.py

echo.
echo [3/3] Finalizing Submission Assets...
if exist dist\DesktopLauncher.exe (
    copy dist\DesktopLauncher.exe TRAFFIC_CONTROL_SYSTEM_DESKTOP.exe
    echo.
    echo SUCCESS! Your standalone EXE is ready: TRAFFIC_CONTROL_SYSTEM_DESKTOP.exe
) else (
    echo.
    echo ERROR: Build failed. Please ensure Python is in your PATH.
)
pause
