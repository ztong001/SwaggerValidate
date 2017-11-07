:: Set PY_HOME to the home directory of your Python installation
:: You can install Python through the Software Centre
:: set PY_HOME=C:/Python27

@echo off
set "psCommand="(new-object -COM 'Shell.Application')^
.BrowseForFolder(0,'Please choose a directory for validation',0,0).self.path""

for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "folder=%%I"

setlocal enabledelayedexpansion
%~dp0\PortablePython\App\python validate.py %folder% 
choice /M "Will you like to modify the swagger docs automatically?"
echo %ERRORLEVEL%
IF ERRORLEVEL 2 (
GOTO END
)
IF ERRORLEVEL 1 ( 
GOTO MODIFY
)

:MODIFY
%~dp0\PortablePython\App\python modify.py %folder% 

:END
echo End of script
cmd /k