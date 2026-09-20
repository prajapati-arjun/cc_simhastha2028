<#
.SYNOPSIS
Starts the Simhastha local development stack.

Builds and starts Postgres/PostGIS, Redis, the FastAPI API and the Next.js
web app in Docker Compose. It then applies migrations and loads the idempotent
development seed data, so a fresh checkout is usable once this script exits.
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
} else {
    Write-Warning ".env was not found. Docker Compose defaults from infra/docker-compose.yml will be used."
}
$composeArgs += @("-f", $composeFile)

Set-Location -LiteralPath $repoRoot

Write-Host "Starting Simhastha development services..." -ForegroundColor Cyan
& docker @composeArgs up --build --detach
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose could not start the development stack."
}

Write-Host "Applying database migrations..." -ForegroundColor Cyan
& docker @composeArgs exec -T api alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    throw "Database migrations failed. Run 'docker compose ... logs api' for details."
}

Write-Host "Loading development seed data..." -ForegroundColor Cyan
& docker @composeArgs exec -T api python -m app.seed
if ($LASTEXITCODE -ne 0) {
    throw "Database seeding failed."
}

& docker @composeArgs ps
if ($LASTEXITCODE -ne 0) {
    throw "The stack started, but its status could not be read."
}

Write-Host "`nReady:" -ForegroundColor Green
Write-Host "  Web:      http://localhost:3000/en"
Write-Host "  API:      http://localhost:8000/docs"
Write-Host "  Health:   http://localhost:8000/health"
