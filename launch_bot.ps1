# Discord AI Bot Launcher - PowerShell Version
# Allows you to choose persona/instruction when starting the bot

Write-Host "DISCORD AI BOT LAUNCHER" -ForegroundColor Cyan
Write-Host ("=" * 40) -ForegroundColor Cyan

# Check if instructions directory exists
if (!(Test-Path "instructions")) {
    Write-Host "ERROR: Instructions directory not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Get all instruction files
$instructionFiles = Get-ChildItem -Path "instructions" -Filter "*.txt" | Sort-Object Name

if ($instructionFiles.Count -eq 0) {
    Write-Host "ERROR: No instruction files found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit
}

# Read current config
$currentPersona = "assist"  # default
if (Test-Path "config.yml") {
    $configContent = Get-Content "config.yml" -Raw
    if ($configContent -match "DEFAULT_INSTRUCTION:\s*(\w+)") {
        $currentPersona = $matches[1]
    }
}

Write-Host "Current persona: $currentPersona" -ForegroundColor Yellow
Write-Host ""

# Display available personas
Write-Host "AVAILABLE BOT PERSONAS" -ForegroundColor Magenta
Write-Host ("=" * 60) -ForegroundColor Magenta

for ($i = 0; $i -lt $instructionFiles.Count; $i++) {
    $file = $instructionFiles[$i]
    $personaName = $file.BaseName
    
    # Try to read first line as description
    $description = "Custom persona"
    try {
        $content = Get-Content $file.FullName -First 5 -ErrorAction SilentlyContinue
        foreach ($line in $content) {
            if ($line.Trim() -ne "" -and $line.Trim().Length -gt 10) {
                $description = $line.Trim()
                if ($description.Length -gt 80) {
                    $description = $description.Substring(0, 80) + "..."
                }
                break
            }
        }
    }
    catch {
        # Keep default description
    }
    
    Write-Host ("{0,2}. {1}" -f ($i + 1), $personaName) -ForegroundColor White
    Write-Host "    Description: $description" -ForegroundColor Gray
    Write-Host ""
}

# Get user choice
do {
    $prompt = "Please choose a persona (1-$($instructionFiles.Count)) or press Enter to keep current ($currentPersona)"
    Write-Host $prompt -ForegroundColor Green
    $choice = Read-Host "Your choice"
    
    if ($choice -eq "") {
        Write-Host "Keeping current persona: $currentPersona" -ForegroundColor Green
        $selectedPersona = $currentPersona
        $validChoice = $true
    }
    elseif ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $instructionFiles.Count) {
        $selectedPersona = $instructionFiles[[int]$choice - 1].BaseName
        Write-Host "Selected persona: $selectedPersona" -ForegroundColor Green
        $validChoice = $true
    }
    else {
        Write-Host "Please enter a number between 1 and $($instructionFiles.Count)" -ForegroundColor Red
        $validChoice = $false
    }
} while (-not $validChoice)

# Update config if different persona selected
if ($selectedPersona -ne $currentPersona) {
    Write-Host ""
    Write-Host "Updating config to use persona: $selectedPersona" -ForegroundColor Yellow
    
    try {
        # Read config file
        $configContent = Get-Content "config.yml" -Raw
        
        # Update the DEFAULT_INSTRUCTION line
        if ($configContent -match "DEFAULT_INSTRUCTION:\s*\w+") {
            $configContent = $configContent -replace "DEFAULT_INSTRUCTION:\s*\w+", "DEFAULT_INSTRUCTION: $selectedPersona"
        }
        else {
            # Add the line if it doesn't exist
            $configContent += "`nDEFAULT_INSTRUCTION: $selectedPersona"
        }
        
        # Write back to file
        $configContent | Set-Content "config.yml" -Encoding UTF8
        Write-Host "Config updated successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "Failed to update config: $($_.Exception.Message)" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit
    }
}

# Display selected persona info
Write-Host ""
Write-Host "Ready to start bot with persona: $selectedPersona" -ForegroundColor Cyan

# Try to show persona description
$selectedFile = $instructionFiles | Where-Object { $_.BaseName -eq $selectedPersona }
if ($selectedFile) {
    try {
        $content = Get-Content $selectedFile.FullName -First 5 -ErrorAction SilentlyContinue
        foreach ($line in $content) {
            if ($line.Trim() -ne "" -and $line.Trim().Length -gt 10) {
                Write-Host "Description: $($line.Trim())" -ForegroundColor Gray
                break
            }
        }
    }
    catch {
        Write-Host "Description: Custom persona" -ForegroundColor Gray
    }
}

# Ask if user wants to start the bot
Write-Host ""
$startBot = Read-Host "Start the bot now? (Y/n)"

if ($startBot -eq "" -or $startBot -match '^[Yy]') {
    Write-Host ""
    Write-Host "Starting Discord AI Bot..." -ForegroundColor Cyan
    Write-Host ("=" * 40) -ForegroundColor Cyan
    
    # Start the bot
    try {
        python main.py
    }
    catch {
        Write-Host "Error starting bot: $($_.Exception.Message)" -ForegroundColor Red
        Read-Host "Press Enter to exit"
    }
}
else {
    Write-Host "Bot not started. You can run 'python main.py' later." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}