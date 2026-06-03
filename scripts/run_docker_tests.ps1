param(
    [switch]$Build
)

$ErrorActionPreference = "Stop"

function Run-Step {
    param(
        [string]$Name,
        [string]$Command
    )

    Write-Host ""
    Write-Host "==> $Name"
    Invoke-Expression $Command
}

if ($Build) {
    Run-Step "Build test images" "docker compose --profile test build backend backend_unit_tests backend_integration_tests frontend_tests mobile_tests"
}

Run-Step "Start runtime stack" "docker compose up -d db backend frontend"
Run-Step "Seed demo data (idempotent)" "docker compose exec -T backend python -m seed"

Run-Step "Backend unit tests" "docker compose --profile test run --rm backend_unit_tests"
Run-Step "Backend integration tests" "docker compose --profile test run --rm backend_integration_tests"
Run-Step "Frontend unit tests" "docker compose --profile test run --rm frontend_tests"
Run-Step "Mobile unit tests" "docker compose --profile test run --rm mobile_tests"

Write-Host ""
Write-Host "All Docker tests passed."
