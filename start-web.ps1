#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start CrewAI Flow Control Center Web Server

.DESCRIPTION
    This script starts the CrewAI Flow Control Center web interface.
    It checks dependencies, creates required directories, and launches the FastAPI server.
    
    Can be run without any parameters using sensible defaults:
    - Port: 8000
    - Host: localhost  
    - Auto-reload: disabled

.PARAMETER Port
    Port number to run the server on (default: 8000)

.PARAMETER Host
    Host address to bind to (default: localhost)

.PARAMETER Reload
    Enable auto-reload for development (default: true)

.EXAMPLE
    .\start-web.ps1
    Start the server with default settings (localhost:8000, no auto-reload)

.EXAMPLE
    .\start-web.ps1 -Port 3000 -Host 0.0.0.0
    Start the server on port 3000, accessible from any host

.EXAMPLE
    .\start-web.ps1 -Reload
    Start the server with auto-reload for development
#>

param(
    # Keep defaults so script can be run without arguments
    [int]$Port = 8000,
    # allow a commonly-used name 'Host' while keeping HostAddress for backward compat
    [Alias('Host')][string]$HostAddress = "localhost",
    [switch]$Reload=$true
)

# Colors for output
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

function Write-InfoMessage {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $InfoColor
}

function Write-SuccessMessage {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $SuccessColor
}

function Write-ErrorMessage {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $ErrorColor
}

function Write-WarningMessage {
    param([string]$Message)
    Write-Host $Message -ForegroundColor $WarningColor
}

# Main execution
try {
    Write-Host ""
    Write-Host "🚀 CrewAI Flow Control Center - Startup Script" -ForegroundColor Magenta
    Write-Host "=" * 60 -ForegroundColor Gray
    
    # Check if we're in the correct directory
    if (-not (Test-Path "web_server.py")) {
        Write-ErrorMessage "❌ Error: web_server.py not found in current directory"
        Write-InfoMessage "Please run this script from the CrewAI project root directory"
        exit 1
    }
    
    Write-InfoMessage "📁 Project directory: $(Get-Location)"
    
    # Create required directories
    Write-InfoMessage "📂 Creating required directories..."
    $directories = @("www\plots", "output\posts")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-SuccessMessage "   ✅ Created: $dir"
        } else {
            Write-InfoMessage "   📁 Exists: $dir"
        }
    }
    
    # Check Python
    Write-InfoMessage "🐍 Checking Python installation..."
    $pythonCmd = "python"
    $pipCmd = "pip"
    try {
        $pythonVersion = & $pythonCmd --version 2>&1
        Write-SuccessMessage "   ✅ $pythonVersion"
    } catch {
        Write-ErrorMessage "❌ Python not found. Please install Python and add it to PATH"
        exit 1
    }
    
    # Check dependencies
    Write-InfoMessage "📦 Checking web server dependencies..."
    try {
    & $pythonCmd -c "import fastapi, uvicorn" 2>$null
        Write-SuccessMessage "   ✅ FastAPI dependencies found"
    } catch {
        Write-WarningMessage "   ⚠️  Web server dependencies missing"
        $response = Read-Host "Install dependencies from requirements.txt? (Y/n)"
        if ($response -eq "" -or $response -match "^[Yy]") {
            Write-InfoMessage "   📥 Installing dependencies..."
            & $pipCmd install -r requirements.txt
            if ($LASTEXITCODE -eq 0) {
                Write-SuccessMessage "   ✅ Dependencies installed successfully"
            } else {
                Write-ErrorMessage "   ❌ Failed to install dependencies"
                exit 1
            }
        } else {
            Write-ErrorMessage "   ❌ Cannot start without dependencies"
            exit 1
        }
    }
    
    # Display startup information
    Write-Host ""
    Write-Host "🌐 Starting CrewAI Flow Control Center..." -ForegroundColor Magenta
    Write-Host "-" * 60 -ForegroundColor Gray
    Write-InfoMessage "🖥️  Host: $HostAddress"
    Write-InfoMessage "🔌 Port: $Port"
    Write-InfoMessage "🔄 Auto-reload: $($Reload.IsPresent)"
    Write-InfoMessage "🌍 URL: http://$HostAddress`:$Port"
    Write-Host ""
    Write-SuccessMessage "✨ Web interface will be available at: http://$HostAddress`:$Port"
    Write-InfoMessage "📊 Flow plots will be saved to: www/plots/"
    Write-InfoMessage "📝 Generated posts will be saved to: output/posts/"
    Write-Host ""
    Write-WarningMessage "💡 Press Ctrl+C to stop the server"
    Write-Host "-" * 60 -ForegroundColor Gray
    
    # Build command arguments
    $arguments = @("web_server.py", "--host", $HostAddress, "--port", "${Port}")
    if ($Reload) {
        $arguments += "--reload"
    }
    
    # Start the server
    Write-InfoMessage "🚀 Launching FastAPI server..."
    Write-Host ""
    
    # Launch the server with constructed arguments. Use call operator to invoke python.
    & $pythonCmd @arguments
    
} catch {
    Write-ErrorMessage "❌ Unexpected error: $($_.Exception.Message)"
    exit 1
} finally {
    Write-Host ""
    Write-InfoMessage "👋 CrewAI Flow Control Center stopped"
}