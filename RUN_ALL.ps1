[CmdletBinding()]
param(
    [ValidateSet('none','smoke','all')]
    [string]$RuntimeMode = 'smoke',
    [string]$DockerImage = 'usv-guidance-legacy-qualification:0.3',
    [string]$WorkRoot = '',
    [switch]$SkipDockerBuild
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$HarnessRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($WorkRoot)) { $WorkRoot = Join-Path $HarnessRoot '_qualification_work' }
$Workspace = Join-Path $WorkRoot 'workspace'
$ReturnDir = Join-Path $HarnessRoot 'qualification_return'
$ZipPath = Join-Path $HarnessRoot 'QUALIFICATION_RETURN.zip'
$ZipHashPath = "$ZipPath.sha256"
$finalRc = 99

function Write-Step([string]$Message) { Write-Host "`n=== $Message ===" -ForegroundColor Cyan }
function Write-JsonFile([string]$Path, $Object) { $Object | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $Path -Encoding UTF8 }
function Package-Return {
    try {
        Write-Step 'Package qualification return (always)'
        if (-not (Test-Path $ReturnDir)) { New-Item -ItemType Directory -Force -Path $ReturnDir | Out-Null }
        if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
        Compress-Archive -Path (Join-Path $ReturnDir '*') -DestinationPath $ZipPath -CompressionLevel Optimal -Force
        $sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $ZipPath).Hash.ToLowerInvariant()
        "$sha  QUALIFICATION_RETURN.zip" | Set-Content -LiteralPath $ZipHashPath -Encoding ASCII
        Write-Host "`nQualification return: $ZipPath" -ForegroundColor Green
        Write-Host "SHA-256: $sha" -ForegroundColor Green
    } catch {
        Write-Warning "Could not package qualification return: $($_.Exception.Message)"
    }
}

New-Item -ItemType Directory -Force -Path $WorkRoot, $Workspace, $ReturnDir | Out-Null
Get-ChildItem -LiteralPath $ReturnDir -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $ReturnDir | Out-Null

try {
    Write-Step 'Windows / Docker preflight'
    & (Join-Path $HarnessRoot 'scripts\preflight_windows.ps1') -OutputPath (Join-Path $ReturnDir 'preflight.json') *> (Join-Path $ReturnDir 'preflight.log')
    if ($LASTEXITCODE -ne 0) { throw "Mandatory preflight failed (rc=$LASTEXITCODE)." }

    Write-Step 'Environment capture'
    $envInfo = [ordered]@{
        schema = 'usv-qualification-environment/v1'
        timestamp_utc = [DateTime]::UtcNow.ToString('o')
        computer_name = $env:COMPUTERNAME
        os = [System.Environment]::OSVersion.VersionString
        powershell = $PSVersionTable.PSVersion.ToString()
        runtime_mode = $RuntimeMode
        docker_image = $DockerImage
    }
    Write-JsonFile (Join-Path $ReturnDir 'environment.json') $envInfo

    if (-not $SkipDockerBuild) {
        Write-Step 'Build pinned legacy qualification image'
        $buildLog = Join-Path $ReturnDir 'docker-build.log'
        & docker build --pull=false --platform linux/amd64 -t $DockerImage -f (Join-Path $HarnessRoot 'Dockerfile.legacy') $HarnessRoot 2>&1 | Tee-Object -FilePath $buildLog
        $dockerBuildOk = ($LASTEXITCODE -eq 0)
        Write-JsonFile (Join-Path $ReturnDir 'docker_build.json') ([ordered]@{status=if($dockerBuildOk){'PASS'}else{'FAIL'}; image=$DockerImage; rc=$LASTEXITCODE})
        if (-not $dockerBuildOk) { throw 'Docker image build failed. See docker-build.log.' }
    } else {
        & docker image inspect $DockerImage *> (Join-Path $ReturnDir 'docker-image-inspect.log')
        $exists = ($LASTEXITCODE -eq 0)
        Write-JsonFile (Join-Path $ReturnDir 'docker_build.json') ([ordered]@{status=if($exists){'SKIPPED'}else{'FAIL'}; image=$DockerImage; image_present=$exists})
        if (-not $exists) { throw "-SkipDockerBuild requested but image '$DockerImage' does not exist locally." }
    }

    Write-Step 'Run qualification inside container'
    $HarnessMount = (Resolve-Path $HarnessRoot).Path -replace '\\','/'
    $WorkspaceMount = (Resolve-Path $Workspace).Path -replace '\\','/'
    $ReturnMount = (Resolve-Path $ReturnDir).Path -replace '\\','/'
    $dockerArgs = @(
        'run','--rm','--platform','linux/amd64',
        '--mount',"type=bind,source=$HarnessMount,target=/harness,readonly",
        '--mount',"type=bind,source=$WorkspaceMount,target=/workspace",
        '--mount',"type=bind,source=$ReturnMount,target=/return",
        '-e',"RUNTIME_MODE=$RuntimeMode",
        $DockerImage,'bash','/harness/scripts/run_qualification.sh','/workspace','/return'
    )
    & docker @dockerArgs
    $finalRc = $LASTEXITCODE
} catch {
    $msg = $_.Exception.Message
    Write-Error $msg -ErrorAction Continue
    Write-JsonFile (Join-Path $ReturnDir 'harness_error.json') ([ordered]@{
        timestamp_utc=[DateTime]::UtcNow.ToString('o'); status='FAIL'; message=$msg; category='HOST_OR_WRAPPER'
    })
    if (-not (Test-Path (Join-Path $ReturnDir 'docker_build.json'))) {
        Write-JsonFile (Join-Path $ReturnDir 'docker_build.json') ([ordered]@{status='NOT_REACHED'; image=$DockerImage})
    }
    $finalRc = 90
} finally {
    Package-Return
}
exit $finalRc
