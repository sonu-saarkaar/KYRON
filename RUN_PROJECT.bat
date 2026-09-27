@echo off
title KYRON - Project Runner
echo ========================================================
echo   Starting KYRON Project (Bypassing PowerShell Policy)
echo ========================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0RUN_PROJECT.ps1"
