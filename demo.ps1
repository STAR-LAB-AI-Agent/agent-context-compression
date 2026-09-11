$ErrorActionPreference = 'Stop'

Write-Host '场景 1：通用上下文压缩'
python -m context_compactor examples/sample_chat.txt --root . --pretty

Write-Host "`n场景 2：主题聚焦压缩"
python -m context_compactor examples/sample_chat.txt -i '围绕安全约束保留信息' --ratio 0.30 --root . --pretty

Write-Host "`n场景 3：压缩质量与 Token 对比"
python -m context_compactor examples/sample_chat.json -i '评估压缩前后 Token 和质量' --root . --pretty

Write-Host "`n自动化测试"
pytest -q
