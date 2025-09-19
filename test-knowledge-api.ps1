# Test Knowledge Management API Endpoints

$baseUrl = "http://localhost:8000"

Write-Host "🧪 Testing Knowledge Management API Endpoints" -ForegroundColor Cyan
Write-Host "=" * 50

# Test 1: Get Knowledge Stats
Write-Host "`n📊 Testing GET /api/knowledge/stats" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/knowledge/stats" -Method GET
    Write-Host "✅ Success:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Check Topic Coverage
Write-Host "`n🔍 Testing POST /api/knowledge/check-topic" -ForegroundColor Yellow
$topicCheckBody = @{
    topic = "Testing API from PowerShell"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/knowledge/check-topic" -Method POST -Body $topicCheckBody -ContentType "application/json"
    Write-Host "✅ Success:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Reset Topics (commented out for safety)
Write-Host "`n🗑️ Testing POST /api/knowledge/reset (topics)" -ForegroundColor Yellow
Write-Host "⚠️ Skipping reset test for safety - would reset topic data" -ForegroundColor Yellow

Write-Host "`n🎉 API Testing Complete!" -ForegroundColor Green