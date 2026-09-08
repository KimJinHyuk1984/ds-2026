# 템플릿의 공통 파일만 강의 저장소에 복사합니다.
# 사용법: .\sync-shared.ps1 ..\ai-squat-king
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$TargetPath
)

$ErrorActionPreference = "Stop"
$sourceDirectory = [System.IO.Path]::GetFullPath($PSScriptRoot)

if (-not (Test-Path -LiteralPath $TargetPath -PathType Container)) {
  Write-Error "오류: 대상 디렉터리가 없습니다: $TargetPath"
  exit 1
}

$targetDirectory = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $TargetPath).Path)
if ($sourceDirectory.TrimEnd('\') -eq $targetDirectory.TrimEnd('\')) {
  Write-Error "오류: 템플릿 자신을 동기화 대상으로 지정할 수 없습니다."
  exit 1
}

$sharedFiles = @(
  "DESIGN.md",
  "assets/css/tokens.css",
  "assets/css/base.css",
  "assets/js/shared.js"
)
$changedFiles = [System.Collections.Generic.List[string]]::new()

foreach ($relativePath in $sharedFiles) {
  $sourceFile = Join-Path $sourceDirectory $relativePath
  if (-not (Test-Path -LiteralPath $sourceFile -PathType Leaf)) {
    Write-Error "오류: 공통 원본 파일이 없습니다: $sourceFile"
    exit 1
  }
  $targetFile = Join-Path $targetDirectory $relativePath
  if ((Test-Path -LiteralPath $targetFile) -and -not (Test-Path -LiteralPath $targetFile -PathType Leaf)) {
    Write-Error "오류: 대상이 일반 파일이 아닙니다: $targetFile"
    exit 1
  }
  if (-not (Test-Path -LiteralPath $targetFile -PathType Leaf)) {
    $changedFiles.Add($relativePath)
    continue
  }
  $sourceHash = (Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash
  $targetHash = (Get-FileHash -LiteralPath $targetFile -Algorithm SHA256).Hash
  if ($sourceHash -ne $targetHash) { $changedFiles.Add($relativePath) }
}

Write-Host "템플릿: $sourceDirectory"
Write-Host "대상: $targetDirectory"
foreach ($relativePath in $changedFiles) {
  $sourceFile = Join-Path $sourceDirectory $relativePath
  $targetFile = Join-Path $targetDirectory $relativePath
  Write-Host "`n--- $targetFile"
  Write-Host "+++ $sourceFile"
  $oldLines = if (Test-Path -LiteralPath $targetFile -PathType Leaf) { @(Get-Content -LiteralPath $targetFile -Encoding UTF8) } else { @() }
  $newLines = @(Get-Content -LiteralPath $sourceFile -Encoding UTF8)
  if ($oldLines.Count -eq 0) {
    $newLines | ForEach-Object { Write-Host ("+ " + $_) }
  } elseif ($newLines.Count -eq 0) {
    $oldLines | ForEach-Object { Write-Host ("- " + $_) }
  } else {
    Compare-Object -ReferenceObject $oldLines -DifferenceObject $newLines -SyncWindow 3 | ForEach-Object {
      $prefix = if ($_.SideIndicator -eq "=>") { "+ " } else { "- " }
      Write-Host ($prefix + $_.InputObject)
    }
  }
}

if ($changedFiles.Count -eq 0) {
  Write-Host "이미 최신 상태입니다. 변경할 파일이 없습니다."
  exit 0
}

$answer = Read-Host "`n위 차이의 공통 파일 $($changedFiles.Count)개를 복사할까요? [y/n]"
if ($answer -notmatch '^[yY]$') {
  Write-Host "취소했습니다. 파일을 변경하지 않았습니다."
  exit 0
}

foreach ($relativePath in $changedFiles) {
  $sourceFile = Join-Path $sourceDirectory $relativePath
  $targetFile = Join-Path $targetDirectory $relativePath
  $targetParent = Split-Path -Parent $targetFile
  if (-not (Test-Path -LiteralPath $targetParent -PathType Container)) {
    New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
  }
  Copy-Item -LiteralPath $sourceFile -Destination $targetFile -Force
  Write-Host "복사 완료: $relativePath"
}
