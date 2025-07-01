@echo off
echo.
echo ========================================
echo   FISERV AUTOMATION TASKBAR BUILDER
echo ========================================
echo.
echo This will build a distributable .exe file
echo from the Python source code.
echo.
pause

python build_exe.py

echo.
echo Build process completed!
echo Check the dist/ folder for the executable.
echo.
pause 