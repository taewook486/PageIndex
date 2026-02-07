# Claude Code 완전 가이드 PDF 처리 스크립트
$ErrorActionPreference = "Continue"

$pdfPath = "claude_guide.pdf"
$baseUrl = "https://api.z.ai/api/coding/paas/v4"
$model = "glm-4.7"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PageIndex - Claude Code Complete Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "PDF File: $pdfPath" -ForegroundColor Yellow
Write-Host "Model: $model" -ForegroundColor Yellow
Write-Host "API: $baseUrl" -ForegroundColor Yellow
Write-Host ""

# 파일 존재 확인
if (-not (Test-Path $pdfPath)) {
    Write-Host "ERROR: PDF file not found" -ForegroundColor Red
    Write-Host "Path: $pdfPath" -ForegroundColor Red
    exit 1
}

Write-Host "File confirmed!" -ForegroundColor Green
Write-Host ""
Write-Host "Starting process..." -ForegroundColor Green
Write-Host ""

# PageIndex 실행
python run_pageindex.py --pdf_path $pdfPath --base-url $baseUrl --model $model --toc-check-pages 20 --max-pages-per-node 10 --max-tokens-per-node 20000

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Processing complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# 결과 파일 확인
$resultFile = "results\claude_guide_structure.json"
if (Test-Path $resultFile) {
    Write-Host ""
    Write-Host "Result: $resultFile" -ForegroundColor Yellow
    $fileInfo = Get-Item $resultFile
    Write-Host "Size: $($fileInfo.Length) bytes" -ForegroundColor Yellow

    # 첫 번째 항목 표시
    $content = Get-Content $resultFile -Raw | ConvertFrom-Json
    Write-Host ""
    Write-Host "Total pages: $($content[0].total_page_number)" -ForegroundColor Cyan
    Write-Host "Total tokens: $($content[1].total_token)" -ForegroundColor Cyan
}
