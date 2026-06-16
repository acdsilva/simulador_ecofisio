@echo off
title EcoFisioLab
cd /d "%~dp0backend"
echo ============================================
echo   EcoFisioLab - iniciando o servidor
echo   O navegador vai abrir em alguns segundos.
echo   Para PARAR o app, feche esta janela.
echo ============================================
echo.
start "" /min cmd /c "timeout /t 5 /nobreak >nul & start http://localhost:8001"
".venv\Scripts\python.exe" server.py
echo.
echo O servidor foi encerrado. Pode fechar esta janela.
pause
