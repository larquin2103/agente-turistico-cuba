@echo off
:: iniciar.bat — Lanzador del Agente Turistico Cuba
:: Doble clic para iniciar. No necesita cambiar la politica de PowerShell.
powershell.exe -ExecutionPolicy Bypass -File "%~dp0iniciar.ps1"
