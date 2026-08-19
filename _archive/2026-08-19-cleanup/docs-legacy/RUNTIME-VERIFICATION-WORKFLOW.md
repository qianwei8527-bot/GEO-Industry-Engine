# GEO-Industry-Engine 后端验证标准流程

**适用场景**: ORM/model/API 代码修改后验证后端是否正常

## 步骤（不要跳、不要变顺序）

### 1. 全杀 Python 进程
```powershell
Get-Process -Name python* -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
```

### 2. 清除所有 __pycache__
```powershell
cd D:\GEO-Industry-Engine\backend
Get-ChildItem -Recurse -Filter "__pycache__" -Directory | ForEach-Object { Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue }
```

### 3. 启动后端（非 --reload，避免增量缓存）
```powershell
$proc = Start-Process python -ArgumentList "-m","uvicorn","app.main:app","--host","127.0.0.1","--port","8080" -PassThru -WindowStyle Hidden
Start-Sleep 5
```

### 4. 健康检查
```powershell
Invoke-RestMethod "http://127.0.0.1:8080/health"
```

### 5. 验证三条核心 API（按依赖顺序）
```powershell
$id = (Invoke-RestMethod "http://127.0.0.1:8080/api/v1/companies/")[0].id
# Context Engine
Invoke-RestMethod "http://127.0.0.1:8080/api/v1/context/company/$id"
# Decision Engine
Invoke-RestMethod "http://127.0.0.1:8080/api/v1/decision/company/$id"
# Agent
$body = @{query="企业分析";params=@{company_id=$id}} | ConvertTo-Json
Invoke-RestMethod "http://127.0.0.1:8080/api/v1/agent/analyze" -Method POST -Body $body -ContentType "application/json"
```

### 如果任何步骤 500
1. 运行直接引擎测试（绕开 HTTP 层定位问题）：
```powershell
cd D:\GEO-Industry-Engine\backend
python -c "import asyncio,sys; sys.path.insert(0,'.'); from app.database import async_session; ..."
```
2. 检查 ORM 字段名是否与 DB 列名一致
3. 检查 Pydantic schema 类型是否匹配 ORM 类型
4. 修复后重复步骤 1-5

### 关键原则
- `metadata_` 这类 Python 保留字字段必须映射列名: `mapped_column("metadata", JSONB, ...)`
- 所有 YAML 权重值必须用 `float()` 或 `WeightsLoader.get_weights()` 获取（不用 `WeightsLoader.load()` 直接传入）
- Agent Tool 使用前必须 `set_db(db)`（在 API 路由中注入）
- IntentionRouter 优先看 params（company_id/industry_id）再匹配关键词
- 每次新增 Entity/Model 必须同步: domain -> ORM -> migration -> schema -> API -> 前端类型
