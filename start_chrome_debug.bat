@echo off
chcp 65001 >nul

echo Закрываю все процессы Chrome...
taskkill /F /IM chrome.exe /T >nul 2>&1
timeout /t 3 /nobreak >nul

set DEBUG_PROFILE=%LOCALAPPDATA%\Google\Chrome\chrome-debug-profile

echo Запускаю Chrome с отладочным портом 9222...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%DEBUG_PROFILE%" ^
  --no-first-run ^
  --no-default-browser-check

echo.
echo Chrome запущен на порту 9222 с профилем: %DEBUG_PROFILE%
echo Теперь можно запускать: python main.py
