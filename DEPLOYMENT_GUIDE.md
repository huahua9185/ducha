# 政府效能督查系统部署指南

## 概述

本指南详细说明了如何部署政府效能督查系统。系统采用Docker容器化部署方式，支持开发环境和生产环境的快速部署。

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx (80)    │    │  Frontend (3000)│    │  Backend (8000) │
│   反向代理       │────│  React应用      │────│  FastAPI应用    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Redis (6379)    │    │PostgreSQL(5432) │
                       │ 缓存服务        │    │ 数据库服务      │
                       └─────────────────┘    └─────────────────┘
```

## 环境要求

### 硬件要求
- **最低配置:**
  - CPU: 2核
  - 内存: 4GB
  - 存储: 20GB
  
- **推荐配置:**
  - CPU: 4核及以上
  - 内存: 8GB及以上
  - 存储: 50GB及以上

### 软件要求
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (用于代码拉取)

### 操作系统支持
- Ubuntu 20.04+
- CentOS 8+
- Windows 10/11 (Docker Desktop)
- macOS 10.15+ (Docker Desktop)

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd ducha
```

### 2. 环境配置
复制环境配置文件：
```bash
cp .env.example .env
```

编辑`.env`文件，配置必要的环境变量：
```env
# 数据库配置
POSTGRES_DB=ducha_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# 应用配置
SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost"]

# 邮件配置 (可选)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. 启动服务

#### 开发环境
```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f
```

#### 生产环境
```bash
# 启动生产环境服务 (包含Nginx)
docker-compose --profile production up -d

# 或使用生产配置文件
docker-compose -f docker-compose.prod.yml up -d
```

### 4. 初始化数据
```bash
# 创建数据库表
docker-compose exec backend python -m alembic upgrade head

# 初始化基础数据
docker-compose exec backend python scripts/init_data.py

# 创建管理员用户
docker-compose exec backend python scripts/create_admin.py
```

### 5. 访问系统
- **前端应用:** http://localhost:3000
- **后端API:** http://localhost:8000
- **API文档:** http://localhost:8000/docs
- **生产环境:** http://localhost (通过Nginx)

## 详细配置

### 数据库配置

#### PostgreSQL优化
```yaml
# docker-compose.yml 中的PostgreSQL配置优化
db:
  image: postgres:15
  environment:
    POSTGRES_DB: ducha_db
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --locale=C"
  command: |
    postgres
    -c shared_preload_libraries=pg_stat_statements
    -c pg_stat_statements.track=all
    -c max_connections=200
    -c shared_buffers=256MB
    -c effective_cache_size=1GB
    -c work_mem=4MB
    -c maintenance_work_mem=64MB
```

#### 数据备份
```bash
# 创建数据库备份
docker-compose exec db pg_dump -U postgres ducha_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库备份
docker-compose exec -T db psql -U postgres ducha_db < backup.sql
```

### Redis配置

#### Redis持久化配置
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes --appendfsync everysec
  volumes:
    - redis_data:/data
    - ./redis.conf:/usr/local/etc/redis/redis.conf
```

### 后端配置

#### 环境变量说明
```env
# 数据库连接
DATABASE_URL=postgresql://user:password@host:port/database

# Redis连接
REDIS_URL=redis://host:port/db

# JWT配置
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# 跨域配置
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# 文件上传
MAX_UPLOAD_SIZE=10485760  # 10MB
UPLOAD_DIR=/app/uploads

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# 监控配置
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
```

#### 性能优化
```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
  environment:
    - WORKERS=4
    - WORKER_CLASS=uvicorn.workers.UvicornWorker
    - WORKER_CONNECTIONS=1000
    - MAX_REQUESTS=1000
    - MAX_REQUESTS_JITTER=100
```

### 前端配置

#### 环境变量
```env
# API配置
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws

# 应用配置
REACT_APP_TITLE=政府效能督查系统
REACT_APP_VERSION=1.0.0

# 功能开关
REACT_APP_ENABLE_MONITORING=true
REACT_APP_ENABLE_ANALYTICS=true
```

#### 构建优化
```dockerfile
# 多阶段构建优化
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
```

### Nginx配置

#### 基础配置
```nginx
server {
    listen 80;
    server_name localhost;
    
    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket支持
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

#### HTTPS配置
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 其他配置...
}
```

## 监控和日志

### 应用监控

#### Prometheus + Grafana
```yaml
# docker-compose.monitoring.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
  volumes:
    - grafana_data:/var/lib/grafana
```

#### 健康检查
```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

### 日志管理

#### 集中化日志
```yaml
# ELK Stack
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
  environment:
    - discovery.type=single-node
    - "ES_JAVA_OPTS=-Xms1g -Xmx1g"

logstash:
  image: docker.elastic.co/logstash/logstash:8.5.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf

kibana:
  image: docker.elastic.co/kibana/kibana:8.5.0
  ports:
    - "5601:5601"
```

#### 日志配置
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 安全配置

### 网络安全
```yaml
networks:
  ducha_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 容器安全
```yaml
backend:
  security_opt:
    - no-new-privileges:true
  user: "1000:1000"
  read_only: true
  tmpfs:
    - /tmp
    - /app/tmp
```

### 密钥管理
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt

services:
  backend:
    secrets:
      - db_password
      - jwt_secret
```

## 备份和恢复

### 自动备份脚本
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 数据库备份
docker-compose exec -T db pg_dump -U postgres ducha_db > $BACKUP_DIR/db_$DATE.sql

# 文件备份
docker run --rm -v ducha_uploads:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/files_$DATE.tar.gz -C /data .

# 清理旧备份 (保留7天)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

### 定时备份
```bash
# 添加到crontab
0 2 * * * /path/to/backup.sh
```

## 故障排除

### 常见问题

#### 服务无法启动
```bash
# 查看容器状态
docker-compose ps

# 查看错误日志
docker-compose logs service_name

# 重启服务
docker-compose restart service_name
```

#### 数据库连接问题
```bash
# 检查数据库连接
docker-compose exec backend python -c "from app.db.session import engine; engine.connect()"

# 检查数据库状态
docker-compose exec db psql -U postgres -c "SELECT version();"
```

#### 性能问题
```bash
# 查看资源使用情况
docker stats

# 查看容器进程
docker-compose top

# 查看网络连接
docker network ls
```

### 调试模式

#### 开发调试
```yaml
backend:
  environment:
    - DEBUG=true
    - LOG_LEVEL=DEBUG
  volumes:
    - ./backend:/app
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 远程调试
```yaml
backend:
  ports:
    - "8000:8000"
    - "5678:5678"  # debugpy端口
  environment:
    - PYTHONPATH=/app
    - PYTHONDONTWRITEBYTECODE=1
```

## 生产环境优化

### 性能优化建议
1. **数据库优化**
   - 配置适当的连接池大小
   - 定期执行VACUUM和ANALYZE
   - 监控慢查询

2. **应用优化**
   - 启用HTTP/2
   - 配置Gzip压缩
   - 使用CDN分发静态资源

3. **缓存策略**
   - Redis缓存热点数据
   - 浏览器缓存静态资源
   - API响应缓存

4. **负载均衡**
   - 多实例部署
   - 会话保持配置
   - 健康检查设置

### 安全加固
1. **网络安全**
   - 配置防火墙规则
   - 限制容器间通信
   - 使用专用网络

2. **访问控制**
   - 最小权限原则
   - 定期更新密钥
   - 审计日志记录

3. **数据安全**
   - 数据加密传输
   - 敏感信息脱敏
   - 定期安全扫描

## 更新和维护

### 应用更新
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose build

# 滚动更新
docker-compose up -d --no-deps backend frontend
```

### 数据库迁移
```bash
# 生成迁移文件
docker-compose exec backend alembic revision --autogenerate -m "migration description"

# 执行迁移
docker-compose exec backend alembic upgrade head
```

### 版本回滚
```bash
# 回滚到指定版本
git checkout v1.0.0
docker-compose build
docker-compose up -d

# 数据库回滚
docker-compose exec backend alembic downgrade -1
```

## 支持和文档

### 获取帮助
- 技术文档: `docs/`目录
- API文档: http://localhost:8000/docs
- 问题反馈: GitHub Issues
- 技术支持: support@example.com

### 相关资源
- [Docker官方文档](https://docs.docker.com/)
- [PostgreSQL文档](https://www.postgresql.org/docs/)
- [Redis文档](https://redis.io/documentation)
- [FastAPI文档](https://fastapi.tiangolo.com/)
- [React文档](https://reactjs.org/docs/)

---

*本部署指南持续更新中，如有问题请及时反馈*