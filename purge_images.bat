@echo off
echo Purging all uploaded images...

set UPLOADS_DIR=router\uploads

if exist "%UPLOADS_DIR%" (
    echo Deleting all files in %UPLOADS_DIR%...
    del /Q "%UPLOADS_DIR%\*.*"
    echo All images purged.
) else (
    echo Uploads directory not found: %UPLOADS_DIR%
)

pause
