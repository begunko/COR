# ============================================
# COR Vendor Updater
# Скачивает/обновляет полные версии движков
# ============================================

Write-Host "🔄 Обновление движков..." -ForegroundColor Cyan

# Three.js
$THREE_URL = "https://github.com/mrdoob/three.js/archive/refs/heads/master.zip"
$THREE_ZIP = "vendor/three.js-master.zip"

Write-Host "`n📦 Three.js..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $THREE_URL -OutFile $THREE_ZIP
Expand-Archive -Path $THREE_ZIP -DestinationPath vendor/ -Force
Remove-Item $THREE_ZIP
Write-Host "  ✅ Three.js обновлён" -ForegroundColor Green

# Babylon.js
$BABYLON_URL = "https://github.com/BabylonJS/Babylon.js/archive/refs/heads/master.zip"
$BABYLON_ZIP = "vendor/Babylon.js-master.zip"

Write-Host "`n📦 Babylon.js..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $BABYLON_URL -OutFile $BABYLON_ZIP
Expand-Archive -Path $BABYLON_ZIP -DestinationPath vendor/ -Force
Remove-Item $BABYLON_ZIP
Write-Host "  ✅ Babylon.js обновлён" -ForegroundColor Green

Write-Host "`n🎉 Всё обновлено!" -ForegroundColor Cyan