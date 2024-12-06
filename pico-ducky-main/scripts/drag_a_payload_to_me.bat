@echo off
REM Verify that a file has been dragged
if "%~1"=="" (
    echo Please drag a .dd file onto the script.
    pause
    exit /b
)

REM Prompt the user to enter the payload number to overwrite
set /p payloadNum=Enter the payload number to overwrite (1, 2, 3, or 4): 

REM Check that the payload number is between 1 and 4
if %payloadNum% lss 1 (
    echo The payload number must be between 1 and 4.
    pause
    exit /b
)
if %payloadNum% gtr 4 (
    echo The payload number must be between 1 and 4.
    pause
    exit /b
)

REM Define the destination path on the PicoDucky, adjusting the name based on the chosen number
cd ..
if %payloadNum%==1 (
    set "location=%CD%payload.dd"
) else (
    set "location=%CD%payload%payloadNum%.dd"
)


REM Copy the dragged file to the destination, overwriting the existing file
copy /Y "%~1" "%location%"

echo The file has been successfully overwritten at %location%.
pause
