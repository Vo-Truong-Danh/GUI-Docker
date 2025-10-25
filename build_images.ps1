# PowerShell script to build images and start compose with BuildKit and pip cache
# Usage: Right-click -> Run with PowerShell or from terminal: .\build_images.ps1

# Enable BuildKit for faster and cacheable builds
$env:DOCKER_BUILDKIT = "1"

Write-Host "Building spark-worker image with BuildKit and pip cache..."
docker-compose build --pull spark-worker

if ($LastExitCode -ne 0) {
    Write-Error "docker-compose build failed (exit $LastExitCode)"
    exit $LastExitCode
}

Write-Host "Bringing up services..."
$env:DOCKER_BUILDKIT = "1"
docker-compose up -d

if ($LastExitCode -ne 0) {
    Write-Error "docker-compose up failed (exit $LastExitCode)"
    exit $LastExitCode
}

Write-Host "Done. Use 'docker-compose ps' to check services."
