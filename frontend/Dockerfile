# 多阶段构建
FROM node:18-alpine as base

WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm install --production=false

# 开发阶段
FROM base as development
COPY . .
EXPOSE 3000
CMD ["npm", "start"]

# 构建阶段
FROM base as build
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine as production
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]