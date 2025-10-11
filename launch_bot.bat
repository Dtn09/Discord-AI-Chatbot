@echo off
setlocal enabledelayedexpansion
title Discord AI Bot Launcher

echo 🤖 DISCORD AI BOT LAUNCHER
echo ========================================

:: Check if instructions directory exists
if not exist "instructions" (
    echo ❌ Instructions directory not found!
    pause
    exit /b 1
)

:: Get list of instruction files
set count=0
for %%f in (instructions\*.txt) do (
    set /a count+=1
    set "file!count!=%%~nf"
    set "fullpath!count!=%%f"
)

if !count! equ 0 (
    echo ❌ No instruction files found in instructions directory!
    pause
    exit /b 1
)

:: Read current config
set "currentPersona=assist"
if exist "config.yml" (
    for /f "tokens=2 delims=: " %%a in ('findstr /r "DEFAULT_INSTRUCTION:" config.yml 2^>nul') do (
        set "currentPersona=%%a"
    )
)

echo 🎯 Current persona: !currentPersona!
echo.

:: Display available personas
echo 🎭 AVAILABLE BOT PERSONAS
echo ============================================================

for /l %%i in (1,1,!count!) do (
    echo  %%i. !file%%i!
    
    :: Try to read first non-empty line as description
    set "desc=No description available"
    for /f "usebackq delims=" %%a in ("!fullpath%%i!") do (
        set "line=%%a"
        if not "!line!"=="" (
            if not "!line:~0,1!"==" " (
                set "desc=!line!"
                goto :nextfile%%i
            )
        )
    )
    :nextfile%%i
    
    :: Truncate description if too long
    if "!desc:~80,1!" neq "" (
        set "desc=!desc:~0,80!..."
    )
    
    echo     📝 !desc!
    echo.
)

:: Get user choice
:getchoice
set /p choice="Please choose a persona (1-!count!) or press Enter to keep current (!currentPersona!): "

if "!choice!"=="" (
    echo ✅ Keeping current persona: !currentPersona!
    set "selectedPersona=!currentPersona!"
    goto :updateconfig
)

:: Validate choice
if !choice! geq 1 if !choice! leq !count! (
    set "selectedPersona=!file%choice%!"
    echo ✅ Selected persona: !selectedPersona!
    goto :updateconfig
) else (
    echo ❌ Please enter a number between 1 and !count!
    goto :getchoice
)

:updateconfig
:: Update config if different persona selected
if not "!selectedPersona!"=="!currentPersona!" (
    echo.
    echo 🔄 Updating config to use persona: !selectedPersona!
    
    :: Create temporary file with updated config
    if exist "config_temp.yml" del "config_temp.yml"
    
    for /f "usebackq delims=" %%a in ("config.yml") do (
        set "line=%%a"
        if "!line:DEFAULT_INSTRUCTION=!" neq "!line!" (
            echo DEFAULT_INSTRUCTION: !selectedPersona!>> config_temp.yml
        ) else (
            echo !line!>> config_temp.yml
        )
    )
    
    :: Replace original config
    move "config_temp.yml" "config.yml" >nul 2>&1
    if errorlevel 1 (
        echo ❌ Failed to update config!
        pause
        exit /b 1
    )
    
    echo ✅ Config updated successfully!
)

:: Display selected persona info
echo.
echo 🚀 Ready to start bot with persona: !selectedPersona!

:: Try to show persona description
for /l %%i in (1,1,!count!) do (
    if "!file%%i!"=="!selectedPersona!" (
        for /f "usebackq delims=" %%a in ("!fullpath%%i!") do (
            set "line=%%a"
            if not "!line!"=="" (
                if not "!line:~0,1!"==" " (
                    echo 📝 Description: !line!
                    goto :startprompt
                )
            )
        )
    )
)

:startprompt
echo.
set /p startBot="Start the bot now? (Y/n): "

if "!startBot!"=="" goto :startbot
if /i "!startBot!"=="y" goto :startbot
if /i "!startBot!"=="yes" goto :startbot

echo 👋 Bot not started. You can run 'python main.py' later.
pause
exit /b 0

:startbot
echo.
echo 🤖 Starting Discord AI Bot...
echo ========================================

python main.py

if errorlevel 1 (
    echo.
    echo ❌ Error starting bot!
    pause
)

endlocal