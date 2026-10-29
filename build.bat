@echo off
rem Builds sothrone with its own copy of the Mara compiler (compiler\,
rem not checked in: MARA_VERSION.txt says which Mara it is, and
rem update_compiler.bat brings in Mara's latest release).
cd /d "%~dp0"
compiler\Mara.exe build sothrone -release
