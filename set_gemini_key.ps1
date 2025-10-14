# Set Gemini API Key for current session
$env:GOOGLE_API_KEY="AIzaSyBAXWlXvoEgO36ZW7dQlxsq06y_5v_MEi8"

Write-Host "✅ Gemini API Key set!" -ForegroundColor Green
Write-Host "   Key: $($env:GOOGLE_API_KEY.Substring(0,20))..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Now you can:" -ForegroundColor Yellow
Write-Host "  1. Run app: python run_spark_gui/main.py" -ForegroundColor White
Write-Host "  2. Go to AI Engine V7.2 tab" -ForegroundColor White
Write-Host "  3. Select 'Gemini Pro' provider" -ForegroundColor White
Write-Host "  4. Click 'Initialize' (API key auto-loaded)" -ForegroundColor White
Write-Host ""
