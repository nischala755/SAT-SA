param([Parameter(Mandatory=$true)][string]$Command)
$ErrorActionPreference = 'Continue'
$root = Split-Path $PSScriptRoot -Parent
$logDir = Join-Path $root 'artifacts/verification'
New-Item -ItemType Directory -Force $logDir | Out-Null
$id = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfff')
$logPath = Join-Path $logDir "$id.log"
$global:LASTEXITCODE = 0
& { Invoke-Expression $Command } *>&1 | Tee-Object -FilePath $logPath
$code = $LASTEXITCODE
[ordered]@{ time=$id; command=$Command; exit_code=$code; log="artifacts/verification/$id.log" } | ConvertTo-Json -Compress | Add-Content (Join-Path $logDir 'commands.jsonl')
Write-Output "EXIT_CODE=$code LOG=$logPath"
exit $code
