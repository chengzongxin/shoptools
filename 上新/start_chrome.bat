 @echo off
chcp 65001 > nul
echo Starting Chrome browser...

:: Check Chrome installation path
if not exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo Error: Chrome browser not found, please make sure Chrome is installed
    pause
    exit /b 1
)

:: Check and create user data directory
if not exist "C:\selenum\ChromeProfile" (
    echo Creating Chrome user data directory...
    mkdir "C:\selenum\ChromeProfile"
)

:: Check if Chrome is already running
tasklist /FI "IMAGENAME eq chrome.exe" 2>NUL | find /I /N "chrome.exe">NUL
if errorlevel 1 (
    echo Chrome is not running, starting new instance...
) else (
    echo Warning: Chrome is already running
    echo Do you want to start a new instance? (Y/N)
    set /p choice=
    if /i "%choice%"=="N" exit /b 0
)

:: Start Chrome
echo Starting Chrome browser...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"

echo Chrome browser has been started!
echo Please wait for the browser to load completely...
timeout /t 5 /nobreak

echo If the browser did not open automatically, please run the following command manually:
echo "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"
pause