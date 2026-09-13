@echo off
setlocal
where pwsh >nul 2>nul
if %errorlevel%==0 (
  pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_ALL.ps1" %*
) else (
  powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_ALL.ps1" %*
)
set RC=%errorlevel%
exit /b %RC%
