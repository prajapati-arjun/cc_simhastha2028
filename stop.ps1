<#
.SYNOPSIS
Stops the Simhastha local development stack.

Containers and networks are removed, while named Postgres and Redis volumes
are deliberately retained. Restart with .\start.ps1 to keep local data.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$repoRoot = $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra/docker-compose.yml"
$envFile = Join-Path $repoRoot ".env"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker Desktop (with Docker Compose v2) is required but 'docker' was not found on PATH."
}

if (-not (Test-Path -LiteralPath $composeFile)) {
    throw "Compose file not found: $composeFile"
}

$composeArgs = @("compose")
if (Test-Path -LiteralPath $envFile) {
    $composeArgs += @("--env-file", $envFile)
}
$composeArgs += @("-f", $composeFile)

Set-Location -LiteralPath $repoRoot

Write-Host "Stopping Simhastha development services..." -ForegroundColor Cyan
& docker @composeArgs down
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose could not stop the development stack."
}

Write-Host "Stopped. Local database and Redis volumes were retained." -ForegroundColor Green
