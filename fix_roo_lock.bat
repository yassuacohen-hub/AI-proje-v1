@echo off
echo Stopping Cursor and related processes...
taskkill /f /im Cursor.exe >nul 2>&1
taskkill /f /im "Cursor Helper.exe" >nul 2>&1
taskkill /f /im Roo.exe >nul 2>&1
echo Backing up Roo data to desktop...
xcopy "%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline" "%USERPROFILE%\Desktop\rooveterinaryinc.roo-cline_backup\" /e /h /i
if errorlevel 1 (
    echo Backup failed. Please check if the folder exists and you have permissions.
    goto end
)
echo Renaming Roo data folder...
rename "%APPDATA%\Cursor\User\globalStorage\rooveterinaryinc.roo-cline" "rooveterinaryinc.roo-cline_old"
if errorlevel 1 (
    echo Rename failed. The folder might not exist or is already renamed.
    goto end
)
echo Done. Please restart Cursor.
:end