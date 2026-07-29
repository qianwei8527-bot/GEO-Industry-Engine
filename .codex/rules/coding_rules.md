# GEO-Industry-Engine 编码规则

> 所有开发人员（包括 AI Agent）必须遵守的编码规范。

---

## 一、代码质量要求

| 要求 | 说明 |
|------|------|
| 可维护 | 清晰命名，必要时注释，单一职责 |
| 可扩展 | 接口设计预留扩展点 |
| 模块化 | 低耦合高内聚，独立可测试 |
| 配置分离 | 配置项与代码分离，环境变量管理 |
| 避免硬编码 | 常量、枚举、配置集中管理 |

---

## 二、命名规范

### Python (FastAPI)
- 模块名：snake_case
- 类名：PascalCase
- 函数名：snake_case
- 变量名：snake_case
- 常量名：UPPER_SNAKE_CASE

### TypeScript (Next.js)
- 组件名：PascalCase
- 文件名：snake_case.tsx
- 函数名：camelCase
- 变量名：camelCase
- 接口名：IPascalCase

### 数据库
- 表名：snake_case (复数)
- 字段名：snake_case
- 主键：id (UUID)
- 时间戳：created_at, updated_at

---

## 三、注释规范

- 公共 API 必须有文档字符串
- 复杂逻辑必须有行注释
- 禁止无意义的注释（"设置变量 x"）
- TODO 必须关联 issue 编号

---

## 四、Git 规范

```
格式：{type}: {description}

类型：feat | fix | refactor | docs | db | infra | test
示例：feat: add company registration API
```

---

## 五、API 规范

- 所有 API 以 /api/v1/ 开头
- 向后兼容：新增字段不许删除旧字段
- 认证：JWT Bearer Token
- 统一响应格式

---

## 六、测试要求

- 核心模块测试覆盖率 >= 80%
- 所有 API 端点必须有测试
- 数据库迁移必须有回滚测试
- 前端核心组件必须有渲染测试

---

> 版本：v1.0 | 2026-07-28
