# PowerShell script to clean, build, and upload expressQL package

Write-Host "=== Cleaning previous build artifacts ==="
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

Write-Host "=== Checking version number ==="
$pyproject = Get-Content -Path "pyproject.toml" | Out-String
if ($pyproject -match 'version\s*=\s*"(.*?)"') {
    $version = $Matches[1]
    Write-Host "Version detected: $version"
} else {
    Write-Host "Could not find version in pyproject.toml"
    exit
}

Write-Host "=== Building the package ==="
python -m build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Build failed. Aborting."
    exit
}

Write-Host "=== Uploading to PyPI ==="
python -m twine upload dist/*

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully uploaded version $version to PyPI!"
} else {
    Write-Host "❌ Upload failed. Check errors above."
}
