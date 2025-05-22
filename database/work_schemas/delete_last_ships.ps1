# PowerShell script to run the Python script to delete ships with ID > threshold
# Usage: .\delete_last_ships.ps1 [threshold_id]
# If threshold_id is not provided, default 1000 will be used

param(
    [Parameter(Mandatory=$false)]
    [int]$ThresholdId = 100
)

# Get the directory of this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Activate virtual environment if it exists
$VenvPath = Join-Path -Path (Join-Path -Path (Split-Path -Parent $ScriptDir) -ChildPath "..") -ChildPath "venv"
$ActivateScript = Join-Path -Path $VenvPath -ChildPath "Scripts\Activate.ps1"

if (Test-Path $ActivateScript) {
    Write-Host "Activating virtual environment..."
    & $ActivateScript
}

# Run the Python script with argument if provided
$PythonScript = Join-Path -Path $ScriptDir -ChildPath "delete_last_100000_ships.py"

Write-Host "Deleting ships with ID > $ThresholdId..."
python $PythonScript $ThresholdId

# Deactivate virtual environment if it was activated
if (Test-Path $ActivateScript) {
    Write-Host "Deactivating virtual environment..."
    deactivate
}

Write-Host "Operation completed." 