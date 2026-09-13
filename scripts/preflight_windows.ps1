[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$checks = New-Object System.Collections.Generic.List[object]
function Add-Check([string]$Name, [string]$Status, [string]$Detail, [bool]$Mandatory=$true) {
    $checks.Add([ordered]@{name=$Name; status=$Status; detail=$Detail; mandatory=$Mandatory})
}
function Try-Text([scriptblock]$Block) {
    try { return ((& $Block 2>&1) | Out-String).Trim() } catch { return $_.Exception.Message }
}

$docker = Get-Command docker -ErrorAction SilentlyContinue
if ($docker) { Add-Check 'docker_cli' 'PASS' $docker.Source $true } else { Add-Check 'docker_cli' 'FAIL' 'docker.exe not found in PATH' $true }

$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) { Add-Check 'git_cli' 'PASS' ((git --version) | Out-String).Trim() $false } else { Add-Check 'git_cli' 'WARN' 'git.exe not found; source fetch can still run inside Docker' $false }

$dockerInfo = $null
if ($docker) {
    try {
        $raw = (& docker info --format '{{json .}}' 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -eq 0) {
            $dockerInfo = $raw | ConvertFrom-Json
            Add-Check 'docker_daemon' 'PASS' 'Docker daemon reachable' $true
            $osType = [string]$dockerInfo.OSType
            Add-Check 'docker_linux_containers' $(if ($osType -eq 'linux') {'PASS'} else {'FAIL'}) "OSType=$osType" $true
            $arch = [string]$dockerInfo.Architecture
            Add-Check 'docker_architecture' $(if ($arch -match 'x86_64|amd64') {'PASS'} else {'WARN'}) "Architecture=$arch; qualification requests linux/amd64" $false
            $cpus = [int]$dockerInfo.NCPU
            Add-Check 'docker_cpu' $(if ($cpus -ge 2) {'PASS'} else {'WARN'}) "NCPU=$cpus" $false
            $memGiB = [Math]::Round(([double]$dockerInfo.MemTotal / 1GB),2)
            Add-Check 'docker_memory' $(if ($memGiB -ge 8) {'PASS'} elseif ($memGiB -ge 4) {'WARN'} else {'WARN'}) "MemGiB=$memGiB; >=8 GiB preferred for later VRX work" $false
        } else {
            Add-Check 'docker_daemon' 'FAIL' $raw $true
        }
    } catch { Add-Check 'docker_daemon' 'FAIL' $_.Exception.Message $true }
}

$wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
if ($wsl) {
    $status = Try-Text { wsl.exe --status }
    Add-Check 'wsl_present' 'PASS' $status $false
} else { Add-Check 'wsl_present' 'WARN' 'wsl.exe not found; Docker Desktop may be using another backend' $false }

try {
    $drive = Get-PSDrive -Name ([IO.Path]::GetPathRoot($PSScriptRoot).TrimEnd(':','\\')) -ErrorAction Stop
    $freeGiB = [Math]::Round($drive.Free / 1GB,2)
    Add-Check 'host_free_disk' $(if ($freeGiB -ge 15) {'PASS'} else {'WARN'}) "FreeGiB=$freeGiB; >=15 GiB recommended" $false
} catch { Add-Check 'host_free_disk' 'WARN' $_.Exception.Message $false }

$mandatoryFail = @($checks | Where-Object {$_.mandatory -and $_.status -eq 'FAIL'}).Count -gt 0
$result = [ordered]@{
    schema = 'usv-qualification-preflight/v1'
    timestamp_utc = [DateTime]::UtcNow.ToString('o')
    status = $(if ($mandatoryFail) {'FAIL'} else {'PASS'})
    checks = $checks
}
$parent = Split-Path -Parent $OutputPath
if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
$result | ConvertTo-Json -Depth 8
exit $(if ($mandatoryFail) {2} else {0})
