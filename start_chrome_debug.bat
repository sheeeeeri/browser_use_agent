@echo off
echo Закрываю все процессы Chrome...
taskkill /F /IM chrome.exe /T >nul 2>&1
timeout /t 3 /nobreak >nul

echo Запускаю Chrome с отладочным портом 9222...
"C:\Program Files\Google\Chrome\Application\chrome.exe" ^
  --remote-debugging-port=9222 ^
  --user-data-dir="%LOCALAPPDATA%\Google\Chrome\User Data" ^
  --profile-directory=Default

echo.
echo Chrome запущен. Теперь можно запускать: python main.py
