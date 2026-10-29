@echo off
rem Builds sooblivion with its own copy of the Mara compiler (compiler\,
rem not checked in: MARA_VERSION.txt says which Mara it is, and
rem update_compiler.bat brings in Mara's latest release). What it builds,
rem and where else its modules are (C:\Code\og), is in build.mara.
cd /d "%~dp0"
compiler\Mara.exe build
