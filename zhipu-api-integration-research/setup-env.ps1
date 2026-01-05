# 环境变量设置脚本 (Windows PowerShell)

# 智谱 API Key
$env:ZHIPU_API_KEY = "your-zhipu-api-key-here"

# OpenRouter API Key (可选，用于中转访问)
$env:OPENROUTER_API_KEY = "your-openrouter-api-key-here"

# Gemini CLI 相关 (如果使用)
$env:GOOGLE_API_KEY = "your-google-api-key-here"

Write-Host "Environment variables set successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage examples:"
Write-Host "  codex --provider zhipu --model glm-4.7 `"your prompt`""
Write-Host "  codex --oss --provider zhipu"

# 永久设置环境变量 (取消注释以启用)
# [Environment]::SetEnvironmentVariable("ZHIPU_API_KEY", "your-api-key", "User")
