# Docker 部署问题解决指南

## 遇到的问题

在运行 `docker-compose up -d` 时遇到了以下错误：

```
failed to do request: Head "https://registry-1.docker.io/v2/library/node/manifests/18-alpine": 
writing response to registry-1.docker.io:443: connecting to 127.0.0.1:10808: 
dial tcp 127.0.0.1:10808: connectex: No connection could be made because the target machine actively refused it.
```

## 问题原因分析

1. **网络代理问题**: Docker尝试通过代理服务器(127.0.0.1:10808)访问Docker Hub，但代理服务器不可用
2. **Docker镜像源访问问题**: 无法连接到 registry-1.docker.io
3. **防火墙或网络配置问题**: 网络连接被阻止

## 解决方案

### 方案1: 配置Docker镜像加速器

#### 1.1 使用阿里云镜像加速器

在Docker Desktop设置中添加镜像加速器：

```json
{
  "registry-mirrors": [
    "https://your-id.mirror.aliyuncs.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
```

#### 1.2 配置步骤
1. 打开Docker Desktop
2. 进入Settings → Docker Engine
3. 添加上述配置到JSON中
4. 点击"Apply & Restart"

### 方案2: 解决代理问题

#### 2.1 清除Docker代理设置

在Docker Desktop中：
1. Settings → Resources → Proxies
2. 取消选择 "Manual proxy configuration"
3. 或者正确配置代理服务器地址

#### 2.2 临时禁用代理

```bash
# Windows CMD
set HTTP_PROXY=
set HTTPS_PROXY=
set NO_PROXY=

# PowerShell
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
$env:NO_PROXY=""
```

### 方案3: 使用本地构建的镜像

#### 3.1 预拉取基础镜像

```bash
# 先手动拉取基础镜像
docker pull node:18-alpine
docker pull python:3.11-slim
docker pull postgres:15
docker pull redis:7-alpine
docker pull nginx:alpine
```

#### 3.2 检查镜像是否可用

```bash
docker images
```

### 方案4: 修改Dockerfile使用国内镜像源

#### 4.1 修改前端Dockerfile

```dockerfile
# 使用阿里云镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/node:18-alpine as base

WORKDIR /app

# 设置npm镜像源
RUN npm config set registry https://registry.npm.taobao.org

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install --production=false

# 其他配置保持不变...
```

#### 4.2 修改后端Dockerfile

```dockerfile
# 使用阿里云镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.11-slim

# 设置pip镜像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 其他配置保持不变...
```

### 方案5: 离线部署方案

#### 5.1 创建简化版docker-compose

我们已经创建了 `docker-compose.simple.yml`，只包含数据库服务：

```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    # 配置...
  redis:
    image: redis:7-alpine
    # 配置...
```

#### 5.2 手动运行应用

参考 `LOCAL_DEVELOPMENT_GUIDE.md` 中的说明。

## 网络诊断命令

### 检查网络连接

```bash
# 测试Docker Hub连接
curl -I https://registry-1.docker.io/v2/

# 测试DNS解析
nslookup registry-1.docker.io

# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Windows下检查网络连接
telnet registry-1.docker.io 443
```

### 检查Docker配置

```bash
# 查看Docker信息
docker info

# 查看Docker版本
docker version

# 检查Docker守护进程状态
docker system info
```

## 推荐的解决顺序

1. **首先尝试**: 配置Docker镜像加速器（方案1）
2. **其次尝试**: 检查并修复代理设置（方案2）
3. **如果仍有问题**: 手动拉取镜像（方案3）
4. **最后方案**: 使用本地开发环境（方案5）

## 验证修复结果

修复后，运行以下命令验证：

```bash
# 测试基础镜像拉取
docker pull hello-world
docker run hello-world

# 测试完整构建
docker-compose build

# 测试服务启动
docker-compose up -d
```

## 生产环境建议

### 1. 使用私有镜像仓库

```yaml
services:
  backend:
    image: your-registry.com/ducha-backend:latest
  frontend:
    image: your-registry.com/ducha-frontend:latest
```

### 2. 预构建镜像

```bash
# 构建并推送镜像
docker build -t your-registry.com/ducha-backend:latest ./backend
docker build -t your-registry.com/ducha-frontend:latest ./frontend

docker push your-registry.com/ducha-backend:latest
docker push your-registry.com/ducha-frontend:latest
```

### 3. 使用多阶段构建优化

```dockerfile
# 优化的Dockerfile示例
FROM node:18-alpine AS dependencies
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 当前状态

✅ **已解决**: 数据库和Redis服务正常运行  
✅ **可用**: 本地开发环境完全可用  
⚠️ **待解决**: Docker镜像构建网络问题  
📋 **建议**: 使用本地开发环境进行开发，生产环境使用预构建镜像

## 联系支持

如果问题仍然存在，请提供以下信息：

1. 操作系统版本
2. Docker Desktop版本
3. 网络环境（是否使用代理）
4. 完整的错误日志
5. `docker info` 命令输出

---

本指南提供了Docker部署问题的完整解决方案，建议按顺序尝试各种方法直到问题解决。