@echo off
rem Updates sothrone's copy of the Mara compiler (compiler\) from Mara's
rem release folder, which release.sh fills from a clean commit after the
rem full suite passes. MARA_VERSION.txt says which Mara it is: the one in
rem compiler\, and the one here, checked in, so each commit says which
rem compiler built it. (The same as sooblivion's.)
setlocal
cd /d "%~dp0"
set RELEASE=C:\Code\Mara\release
if not exist "%RELEASE%\Mara.exe" (
	echo There's no release in %RELEASE%: release.sh in C:\Code\Mara makes one.
	exit /b 1
)
rem code\ and runtime\ mirrored: what the release doesn't have goes, the
rem libraries and objects built from older sources with it.
robocopy "%RELEASE%\code" compiler\code /MIR /NJH /NJS /NFL /NDL /NP
if errorlevel 8 goto failed
robocopy "%RELEASE%\runtime" compiler\runtime /MIR /NJH /NJS /NFL /NDL /NP
if errorlevel 8 goto failed
rem tools\ (clang, the linker) copied only where changed: they're big.
robocopy "%RELEASE%\tools" compiler\tools /E /NJH /NJS /NFL /NDL /NP
if errorlevel 8 goto failed
copy /y "%RELEASE%\Mara.exe" compiler\Mara.exe >nul || goto failed
copy /y "%RELEASE%\MARA_VERSION.txt" compiler\MARA_VERSION.txt >nul || goto failed
copy /y "%RELEASE%\MARA_VERSION.txt" MARA_VERSION.txt >nul || goto failed
type MARA_VERSION.txt
exit /b 0

:failed
echo Couldn't copy all of the release: compiler\ may be half updated. Run this again.
exit /b 1
