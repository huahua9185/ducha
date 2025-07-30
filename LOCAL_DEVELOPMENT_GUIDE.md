# 本地开发环境指南

由于Docker镜像构建遇到网络问题，这里提供本地开发环境的快速启动方法。

## 前提条件

- Python 3.11+
- Node.js 18+
- Docker 和 Docker Compose（用于数据库服务）

## 快速启动

### 1. 启动基础服务（数据库和Redis）

```bash
# 在项目根目录下运行
docker-compose -f docker-compose.simple.yml up -d

# 检查服务状态
docker-compose -f docker-compose.simple.yml ps
```

### 2. 启动后端服务

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install fastapi uvicorn sqlalchemy psycopg2-binary redis pydantic python-jose passlib bcrypt python-multipart

# 设置环境变量
export DATABASE_URL="postgresql://postgres:password@localhost:5432/ducha_db"
export REDIS_URL="redis://localhost:6379"
export SECRET_KEY="your-super-secret-key-for-development"

# 启动FastAPI服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Windows用户使用：
```cmd
set DATABASE_URL=postgresql://postgres:password@localhost:5432/ducha_db
set REDIS_URL=redis://localhost:6379
set SECRET_KEY=your-super-secret-key-for-development
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 启动前端服务

打开新的终端窗口：

```bash
# 进入前端目录
cd frontend

# 启动React开发服务器
npm start
```

## 服务访问地址

启动完成后，可以通过以下地址访问服务：

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **数据库**: localhost:5432 (postgres/password)
- **Redis**: localhost:6379

## 初始化数据

### 方法1：使用测试数据初始化脚本

```bash
cd backend
python scripts/init_test_data.py
```

### 方法2：手动创建管理员用户

通过API接口或数据库直接创建用户数据。

## 测试验证

### 1. 后端API测试

```bash
# 健康检查
curl http://localhost:8000/health

# API连通性测试
curl http://localhost:8000/api/v1/ping
```

### 2. 前端连接测试

在浏览器中打开 http://localhost:3000，应该能看到登录页面。

### 3. 运行集成测试

```bash
# 运行之前创建的集成测试脚本
python frontend_api_test.py
```

## 开发工作流

### 后端开发
1. 修改Python代码会自动重载（由于使用了--reload参数）
2. 数据库变更需要创建迁移文件
3. API文档会自动更新，可在 http://localhost:8000/docs 查看

### 前端开发
1. 修改React代码会自动热重载
2. 新增页面需要添加路由配置
3. API调用通过axios进行，配置在services目录

## 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查Docker服务是否运行
   docker-compose -f docker-compose.simple.yml ps
   
   # 重启数据库服务
   docker-compose -f docker-compose.simple.yml restart db
   ```

2. **端口被占用**
   ```bash
   # Windows查看端口占用
   netstat -ano | findstr :8000
   netstat -ano | findstr :3000
   
   # 终止进程（替换PID）
   taskkill /PID <PID> /F
   ```

3. **前端依赖问题**
   ```bash
   # 清除node_modules重新安装
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **后端依赖问题**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或 venv\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   ```

### 调试模式

#### 后端调试
```bash
# 启用DEBUG模式
export DEBUG=true
export LOG_LEVEL=DEBUG
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

#### 前端调试
浏览器开发者工具 → Console 标签页查看日志输出

## 数据库管理

### 连接数据库
```bash
# 使用Docker执行psql
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d ducha_db

# 或使用本地psql客户端
psql -h localhost -p 5432 -U postgres -d ducha_db
```

### 常用SQL命令
```sql
-- 查看所有表
\dt

-- 查看用户表数据
SELECT * FROM users;

-- 查看督办事项
SELECT * FROM supervision_items;

-- 重置数据库（谨慎使用）
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

## 性能监控

### 后端性能
- FastAPI自带的性能统计：访问 http://localhost:8000/docs 查看响应时间
- 数据库查询优化：检查慢查询日志

### 前端性能
- Chrome DevTools → Performance 标签页
- React Developer Tools 扩展

## 部署到生产环境

当Docker构建问题解决后，可以使用以下命令部署：

```bash
# 完整部署（包含应用容器）
docker-compose up -d

# 生产环境部署
docker-compose --profile production up -d
```

## 环境变量配置

创建 `.env` 文件配置环境变量：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:password@localhost:5432/ducha_db
REDIS_URL=redis://localhost:6379

# 应用配置
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=480
DEBUG=false

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# 邮件配置（可选）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 测试账户

系统预置了以下测试账户：

- **管理员**: admin / admin123456
- **督查员**: supervisor / sup123456  
- **测试用户**: test_admin / test123456

## 技术支持

如果遇到问题，请：

1. 检查服务日志输出
2. 确认端口没有被占用
3. 验证数据库连接状态
4. 查看前端浏览器控制台错误信息

---

本指南提供了完整的本地开发环境配置方法，可以在不依赖Docker镜像构建的情况下快速启动系统进行开发和测试。