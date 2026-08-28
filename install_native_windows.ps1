param (
    [switch]$SkipSpaceCheck = $false
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " MeshTrain Native Windows Installer" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "This script will install:"
Write-Host "1. Microsoft C++ Build Tools (Required for libp2p cryptography)"
Write-Host "2. PyTorch with NVIDIA CUDA Support (Required for local AI processing)"
Write-Host ""

# Check Disk Space First
$drive = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeSpaceGB = [math]::truncate($drive.FreeSpace / 1GB)

Write-Host "Free Space on C: Drive: $freeSpaceGB GB"

if ($freeSpaceGB -lt 15 -and -not $SkipSpaceCheck) {
    Write-Host "ERROR: You only have $freeSpaceGB GB of free space." -ForegroundColor Red
    Write-Host "You need at least 15 GB of free space to install the C++ Build Tools and PyTorch CUDA libraries." -ForegroundColor Red
    Write-Host "Please free up some disk space and run this script again." -ForegroundColor Yellow
    exit 1
}

# 1. Install Visual Studio C++ Build Tools
Write-Host "`n[1/3] Installing Visual Studio C++ Build Tools (This will take a while)..." -ForegroundColor Yellow
$vs_installer = "$env:TEMP\vs_buildtools.exe"
Invoke-WebRequest -Uri "https://aka.ms/vs/17/release/vs_buildtools.exe" -OutFile $vs_installer

# Run silently with the Desktop C++ workload
Write-Host "Running VS Installer in the background..."
$process = Start-Process -FilePath $vs_installer -ArgumentList "--quiet --wait --norestart --nocache --add Microsoft.VisualStudio.Workload.VCTools" -Wait -PassThru

if ($process.ExitCode -eq 0 -or $process.ExitCode -eq 3010) {
    Write-Host "✓ Visual Studio C++ Build Tools installed successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠ VS Build Tools installation exited with code $($process.ExitCode). You may need to run it manually." -ForegroundColor Red
}

# 2. Install PyTorch with CUDA
Write-Host "`n[2/3] Installing PyTorch with CUDA 12.1..." -ForegroundColor Yellow
# We run pip directly. We uninstall the CPU-only versions first just in case.
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 3. Install MeshTrain native dependencies
Write-Host "`n[3/3] Installing MeshTrain ML and Network dependencies..." -ForegroundColor Yellow
pip install -e ".[ml,api]"
pip install --force-reinstall libp2p fastecdsa

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host " Installation Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "You can now run: python -m meshtrain.cli.main start" -ForegroundColor Cyan
Write-Host "The node will now use your native GPU for AI tasks and connect to the real P2P swarm!"
