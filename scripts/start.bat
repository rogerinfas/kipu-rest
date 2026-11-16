@echo off
rem Arranca la demo de KipuRest Live Vision en http://localhost:5000
setlocal
cd /d "%~dp0..\backend"
if "%KIPU_PORT%"=="" set KIPU_PORT=5000

uv run python ..\scripts\check_env.py
if errorlevel 1 (
  echo Corrige los problemas antes de la demo.
  pause
  exit /b 1
)

start "" /b cmd /c "timeout /t 8 >nul && start http://localhost:%KIPU_PORT%"
echo Demo en http://localhost:%KIPU_PORT%  (F = pantalla completa, C = calibrar, Ctrl+C = salir)
uv run uvicorn app.main:app --host 127.0.0.1 --port %KIPU_PORT% --timeout-graceful-shutdown 2
