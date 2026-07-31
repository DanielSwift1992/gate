@echo off
rem gate on Windows: the same one-file CLI, run by the python already here.
rem Both courts run in the node port on this platform; `gate --version` says so.
python "%~dp0gate" %*
exit /b %errorlevel%
