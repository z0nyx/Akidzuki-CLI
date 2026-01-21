@echo off
echo Installing akidzuki SSH CLI Manager...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Installing package...
pip install -e .

if errorlevel 1 (
    echo.
    echo Installation failed. Trying with --user flag...
    pip install -e . --user
    if errorlevel 1 (
        echo.
        echo Installation failed!
        pause
        exit /b 1
    )
)

echo.
echo Checking if akidzuki command is available...

where akidzuki >nul 2>&1
if errorlevel 1 (
    echo.
    echo 'akidzuki' command not found in PATH. Adding Scripts directory to PATH...
    echo.
    
    for /f "delims=" %%i in ('python -c "import site, os; print(os.path.join(os.path.dirname(site.getusersitepackages()), 'Scripts'))"') do set USER_SCRIPTS=%%i
    
    if exist "%USER_SCRIPTS%\akidzuki.exe" (
        echo Found akidzuki.exe in: %USER_SCRIPTS%
        echo.
        
        echo %PATH% | findstr /C:"%USER_SCRIPTS%" >nul
        if %errorlevel% == 0 (
            echo This directory is already in PATH.
        ) else (
            echo Adding to PATH...
            setx PATH "%PATH%;%USER_SCRIPTS%" >nul 2>&1
            
            if errorlevel 1 (
                echo.
                echo WARNING: Failed to add to PATH automatically.
                echo.
                echo Please add this directory manually to your PATH:
                echo   %USER_SCRIPTS%
                echo.
                echo Or restart your terminal/command prompt and run:
                echo   set PATH=%%PATH%%;%USER_SCRIPTS%
            ) else (
                echo SUCCESS: Directory added to PATH!
                echo.
                echo Please close and reopen your terminal/command prompt for changes to take effect.
            )
        )
    ) else (
        for /f "delims=" %%i in ('python -c "import sysconfig; print(sysconfig.get_path('scripts'))"') do set SCRIPTS_DIR=%%i
        
        if exist "%SCRIPTS_DIR%\akidzuki.exe" (
            echo Found akidzuki.exe in: %SCRIPTS_DIR%
            echo.
            echo This directory should already be in PATH.
            echo If 'akidzuki' still doesn't work, restart your terminal/command prompt.
        ) else (
            echo.
            echo ERROR: akidzuki.exe not found in Scripts directories.
            echo Please check the installation.
        )
    )
) else (
    echo.
    echo SUCCESS: 'akidzuki' command is available!
    echo.
    echo You can now run 'akidzuki' from anywhere in the command line.
)

echo.
pause
