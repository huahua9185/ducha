# 政府效能督查系统

一个现代化的政府效能督查管理系统，基于 FastAPI + React + TypeScript 构建，支持督办事项管理、工作流审批、监控预警和统计分析等功能。

## 🚀 项目特性

- **督办事项管理**：创建、编辑、跟踪政府督办事项
- **工作流引擎**：支持自定义审批流程和任务分配
- **监控预警**：实时监控督办进度，自动预警逾期事项
- **统计分析**：多维度数据分析和可视化图表
- **用户权限管理**：基于角色的权限控制系统
- **响应式设计**：支持桌面端和移动端访问

## 🛠️ 技术栈

### 后端
- **FastAPI**: 现代高性能 Python Web 框架
- **SQLAlchemy 2.0**: ORM 数据库操作
- **Alembic**: 数据库迁移工具
- **Pydantic**: 数据验证和序列化
- **JWT**: 用户认证和授权
- **PostgreSQL**: 主数据库（支持 SQLite 开发）

### 前端
- **React 18**: 用户界面框架
- **TypeScript**: 类型安全的 JavaScript
- **Antd**: 企业级 UI 组件库
- **React Query**: 数据获取和缓存
- **Zustand**: 轻量级状态管理
- **React Router**: 客户端路由
- **ECharts**: 数据可视化图表

### 基础设施
- **Docker**: 容器化部署
- **Nginx**: 反向代理和静态文件服务
- **Docker Compose**: 服务编排

## 📦 快速开始

### 环境要求

- Node.js >= 16
- Python >= 3.9
- Docker (可选)

### 本地开发

1. **克隆项目**
```bash
git clone https://github.com/yourusername/ducha.git
cd ducha
```

2. **启动后端服务**
```bash
cd backend
pip install -r requirements.txt
python run_simple.py
```

3. **启动前端服务**
```bash
cd frontend
npm install
npm start
```

4. **访问应用**
- 前端: http://localhost:3001
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

### Docker 部署

```bash
# 使用简化版本快速启动
docker-compose -f docker-compose.simple.yml up -d

# 或使用完整版本
docker-compose up -d
```

## 🔑 默认登录账户

- 管理员: `admin` / `admin123456`
- 督查员: `supervisor` / `sup123456`
- 部门主任: `manager1` / `mgr123456`
- 普通用户: `user1` / `user123456`
- **缓存**: Redis

## 核心功能

### 1. 督办事项管理
- 事项创建、分类、分解
- 责任分配和时限设定
- 全生命周期跟踪

### 2. 流程管控
- 标准化督办流程
- 应急督办机制
- 重点督办管理

### 3. 协同办理
- 多部门协作
- 信息共享
- 沟通协调

### 4. 监控预警
- 智能监控体系
- 四级预警机制
- 自动化处理

### 5. 数据分析与决策支持
- 多维效能分析
- 数据可视化
- AI智能决策辅助

### 6. 角色权限管理
- 分层分级权限
- 组织架构映射
- 安全访问控制

## 项目结构

```
ducha/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── db/            # 数据库配置
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic 模式
│   │   ├── services/      # 业务逻辑
│   │   └── utils/         # 工具函数
│   ├── alembic/           # 数据库迁移
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # React 前端
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── pages/         # 页面
│   │   ├── services/      # API 服务
│   │   ├── utils/         # 工具函数
│   │   └── types/         # TypeScript 类型
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml     # Docker Compose 配置
├── nginx.conf            # Nginx 配置
└── README.md
```

## 快速开始

### 使用 Docker Compose 启动

```bash
# 克隆项目
git clone <repository-url>
cd ducha

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 本地开发

#### 后端开发
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发
```bash
cd frontend
npm install
npm start
```

## 服务端口

- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## 环境变量

复制 `.env.example` 文件为 `.env` 并修改相应配置：

```bash
# 数据库配置
DATABASE_URL=postgresql://postgres:password@db:5432/ducha_db

# Redis配置
REDIS_URL=redis://redis:6379

# JWT密钥
SECRET_KEY=your-secret-key

# 其他配置...
```

## API 文档

系统启动后访问 http://localhost:8000/docs 查看完整的 API 文档。

## 部署说明

详细部署说明请参考 `docs/deployment.md`

## 开发指南

详细开发指南请参考 `docs/development.md`

## 许可证

MIT License