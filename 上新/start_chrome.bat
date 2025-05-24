@echo off
echo 正在启动Chrome浏览器...

:: 尝试多个可能的Chrome安装路径
set CHROME_PATHS=^
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" ^
"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"

:: 遍历所有可能的路径
for %%p in (%CHROME_PATHS%) do (
    if exist %%p (
        echo 找到Chrome: %%p
        start "" "%%p" --remote-debugging-port=9222
        goto :found
    )
)

:not_found
echo 未找到Chrome浏览器，请确保已安装Chrome
pause
exit /b 1

:found
echo Chrome已启动，请在浏览器中打开任意网页
echo 然后运行python main.py
pause 