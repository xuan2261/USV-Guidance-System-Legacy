[CmdletBinding()]
param(
    [string]$OutputPath = ''
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$HarnessRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($OutputPath)) { $OutputPath = Join-Path $HarnessRoot 'PRECHECK_REPORT.json' }
& (Join-Path $HarnessRoot 'scripts\preflight_windows.ps1') -OutputPath $OutputPath
exit $LASTEXITCODE
