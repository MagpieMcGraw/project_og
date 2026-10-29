@echo off
rem Builds oblivion with project_og's Mara compiler (..\compiler\, not
rem checked in: ..\MARA_VERSION.txt says which Mara it is, and
rem ..\update_compiler.bat brings in Mara's latest release). What it
rem builds, and where else its modules are (..\og), is in build.mara.
cd /d "%~dp0"
..\compiler\Mara.exe build
