# PowerShell Test Runner Script for Windows

$ErrorActionPreference = "Stop"

Write-Host "🧪 Starting Test Suite..." -ForegroundColor Yellow
Write-Host "=========================" -ForegroundColor Yellow

# Set Python path
$env:PYTHONPATH = $PWD

# Test Backend
Write-Host "`n📦 Testing Backend..." -ForegroundColor Cyan
pytest tests/ -v `
    --cov=src `
    --cov-report=html `
    --cov-report=term `
    --cov-report=xml `
    --maxfail=3 `
    --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend tests passed!" -ForegroundColor Green
} else {
    Write-Host "❌ Backend tests failed!" -ForegroundColor Red
    exit 1
}

# Show coverage summary
Write-Host "`n📊 Coverage Summary:" -ForegroundColor Cyan
coverage report --skip-empty

# Check coverage threshold
coverage report --fail-under=60 --skip-empty
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Coverage threshold met (>60%)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Coverage below 60%" -ForegroundColor Yellow
}

# Run linting
Write-Host "`n🔍 Running Linting..." -ForegroundColor Cyan
flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

Write-Host "`n✅ All checks passed!" -ForegroundColor Green
Write-Host "`n📝 Coverage report available at: htmlcov\index.html" -ForegroundColor Cyan
