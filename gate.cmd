@echo off
rem gate on Windows: the tool is one binary, and this finds it the same way the
rem posix shim does: an explicit GATE_CLI, then the clone's own build, then a
rem copy a team carried in, then one on PATH.
setlocal
if not "%GATE_CLI%"=="" if exist "%GATE_CLI%" ( "%GATE_CLI%" %* & exit /b %errorlevel% )
if exist "%~dp0bin\gate-cli.exe" ( "%~dp0bin\gate-cli.exe" %* & exit /b %errorlevel% )
if exist "%~dp0.gate\bin\gate-cli.exe" ( "%~dp0.gate\bin\gate-cli.exe" %* & exit /b %errorlevel% )
where gate-cli.exe >nul 2>nul && ( gate-cli.exe %* & exit /b %errorlevel% )
echo gate: no binary here, and this tool is one binary. 1>&2
echo   build it: bin\build-cli.sh, which needs swiftc and takes about a minute 1>&2
echo   or take one from the releases at github.com/DanielSwift1992/gate 1>&2
exit /b 1
