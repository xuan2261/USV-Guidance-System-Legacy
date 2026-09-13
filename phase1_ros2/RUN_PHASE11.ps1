param(
  [switch]$SkipPull,
  [switch]$KeepBuildTree
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Out = Join-Path $Root 'phase11_out'
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$Image = 'usv-guidance-phase11:jazzy'
$Base = 'ros:jazzy-ros-base-noble'
$failure = $null

function Write-Json($Path, $Object) {
  $Object | ConvertTo-Json -Depth 12 | Set-Content -Encoding UTF8 $Path
}

try {
  $docker = Get-Command docker -ErrorAction Stop
  $null = & docker version --format '{{.Server.Os}}/{{.Server.Arch}}'
  if ($LASTEXITCODE -ne 0) { throw 'Docker daemon is unavailable.' }

  if (-not $SkipPull) {
    & docker pull $Base | Tee-Object -FilePath (Join-Path $Out 'docker_pull.log')
    if ($LASTEXITCODE -ne 0) { throw "docker pull failed: $Base" }
  }
  $digest = (& docker image inspect $Base --format '{{json .RepoDigests}}' 2>$null)
  Write-Json (Join-Path $Out 'base_image_identity.json') @{
    image = $Base
    repo_digests_json = $digest
    captured_at = (Get-Date).ToString('o')
  }

  & docker build -f (Join-Path $Root 'Dockerfile.phase11') -t $Image $Root 2>&1 |
    Tee-Object -FilePath (Join-Path $Out 'docker_build.log')
  if ($LASTEXITCODE -ne 0) { throw 'Phase 1.1 Docker build failed.' }

  $mount = "type=bind,source=$Root,target=/work"
  $args = @('run','--rm','--mount',$mount)
  if ($KeepBuildTree) { $args += @('-e','USV_KEEP_BUILD_TREE=1') }
  $args += @($Image,'bash','/work/scripts/run_phase11_build.sh')
  & docker @args 2>&1 | Tee-Object -FilePath (Join-Path $Out 'docker_run.log')
  if ($LASTEXITCODE -ne 0) { throw 'Phase 1.1 qualification failed inside Docker.' }
}
catch {
  $failure = $_.Exception.Message
  Write-Json (Join-Path $Out 'wrapper_error.json') @{
    status = 'FAIL'
    message = $failure
    captured_at = (Get-Date).ToString('o')
  }
}
finally {
  $zip = Join-Path $Root 'PHASE11_RETURN.zip'
  if (Test-Path $zip) { Remove-Item -Force $zip }
  if (Test-Path $Out) {
    Compress-Archive -Path (Join-Path $Out '*') -DestinationPath $zip -Force
  }
  if ($failure) {
    Write-Host "FAIL: $failure" -ForegroundColor Red
    Write-Host "Evidence bundle: $zip"
    exit 1
  }
  Write-Host "PASS: Phase 1.1 build/test harness completed."
  Write-Host "Evidence bundle: $zip"
}
