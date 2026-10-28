@echo off
rem Builds sooblivion with its own copy of the Mara compiler (compiler\,
rem not checked in: MARA_VERSION.txt says which Mara it is, and
rem update_compiler.bat brings in Mara's latest release): the game,
rem sooblivion.exe, here; the tools, tools\tools.exe, apart from it, so
rem their crashes go to tools\crash.txt and not into the game's crash.txt.
setlocal
cd /d "%~dp0"
compiler\Mara.exe build sooblivion -release || exit /b 1
compiler\Mara.exe build tools -release || exit /b 1
rem (Mara builds a module here, beside its sources: the tools are moved.)
if not exist tools mkdir tools
move /y tools.exe tools\tools.exe >nul || exit /b 1
if exist tools.pdb move /y tools.pdb tools\tools.pdb >nul
copy /y SDL3.dll tools\SDL3.dll >nul
