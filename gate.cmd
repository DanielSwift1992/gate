@echo off
rem gate on Windows: the tool is one binary, and this finds it the same way the
rem posix shim does: an explicit GATE_CLI, then the clone's own build, then a
rem copy a team carried in, then one on PATH.
rem
rem ── AND THE CODE THE TOOL EXITS WITH IS THE CODE THIS EXITS WITH. Each rung
rem used to be one line, `( "%%bin%%" %%* & exit /b %%errorlevel%% )`, and cmd
rem expands a variable inside a bracketed block when it READS the block, not
rem when it runs it: %%errorlevel%% was the value from before the tool ran,
rem which is nought. Every refusal this tool makes on this platform came back
rem as success to whatever asked. The rungs pick the binary and nothing else
rem now, and the call stands on its own line, where the code is read after it.
setlocal
set "GATE_BIN="
if not "%GATE_CLI%"=="" if exist "%GATE_CLI%" set "GATE_BIN=%GATE_CLI%"
if not defined GATE_BIN if exist "%~dp0bin\gate-cli.exe" set "GATE_BIN=%~dp0bin\gate-cli.exe"
if not defined GATE_BIN if exist "%~dp0.gate\bin\gate-cli.exe" set "GATE_BIN=%~dp0.gate\bin\gate-cli.exe"
if not defined GATE_BIN for %%I in (gate-cli.exe) do if not "%%~$PATH:I"=="" set "GATE_BIN=%%~$PATH:I"
if not defined GATE_BIN goto :nobinary
"%GATE_BIN%" %*
exit /b %errorlevel%

:nobinary
echo gate: no binary here, and this tool is one binary. 1>&2
echo   build it: bin\build-cli.sh, which needs swiftc and takes about a minute 1>&2
echo   or take one from the releases at github.com/DanielSwift1992/gate 1>&2
exit /b 1
