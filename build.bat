@echo off
rem Builds sooblivion with its own copy of the Mara compiler (compiler\,
rem not checked in: see compiler\MARA_VERSION.txt for which Mara it is).
cd /d "%~dp0"
compiler\Mara.exe build sooblivion -release
