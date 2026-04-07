# 316寝室值日表 - 部署说明

## 项目结构

```
316duty/
├── index.html          # 前端页面
└── backend/
    ├── app.py          # Flask 主程序
    ├── models.py       # 数据库模型
    └── requirements.txt # Python 依赖
```

## 功能特性

- ✅ 身份验证（姓名名单校验）
- ✅ 实时数据同步（WebSocket）
- ✅ 请假调班功能（所有人可用）
- ✅ 手动校准功能（仅管理员）
- ✅ 操作日志记录
- ✅ 回滚功能（仅管理员）
- ✅ 修改预览确认弹窗

---

## 方案一：Render.com 部署（推荐，免费）

### 步骤 1：准备 GitHub 仓库

1. 在 GitHub 创建新仓库
2. 上传项目文件

### 步骤 2：注册 Render

1. 访问 https://render.com
2. 使用 GitHub 账号登录

### 步骤 3：创建 Web Service

1. 点击 "New" → "Web Service"
2. 连接你的 GitHub 仓库
3. 配置：
   - **Name**: `duty-316`（自定义）
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python app.py`
   - **Plan**: Free

4. 点击 "Create Web Service"

### 步骤 4：等待部署完成

部署成功后会获得一个网址，如：`https://duty-316.onrender.com`

---

## 方案二：Railway.app 部署（免费额度）

### 步骤 1：注册 Railway

1. 访问 https://railway.app
2. 使用 GitHub 账号登录

### 步骤 2：部署项目

1. 点击 "New Project"
2. 选择 "Deploy from GitHub repo"
3. 选择你的仓库
4. 配置：
   - **Root Directory**: `backend`
   - **Start Command**: `python app.py`

### 步骤 3：获取网址

部署完成后，在 "Settings" → "Domains" 添加自定义域名或使用默认域名

---

## 方案三：本地运行（开发测试）

### 步骤 1：安装 Python

确保已安装 Python 3.8+

### 步骤 2：安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 步骤 3：运行服务

```bash
python app.py
```

### 步骤 4：访问

打开浏览器访问 `http://localhost:5000`

---

## 方案四：内网穿透（免费，适合临时使用）

如果你的电脑可以长期开机，可以使用内网穿透：

### 使用 ngrok

1. 注册 ngrok: https://ngrok.com
2. 下载并解压 ngrok
3. 运行本地服务：
   ```bash
   cd backend
   python app.py
   ```
4. 另开终端运行 ngrok：
   ```bash
   ngrok http 5000
   ```
5. 获得公网地址，如 `https://xxxx.ngrok.io`

### 使用 cpolar（国内访问更快）

1. 注册 cpolar: https://www.cpolar.com
2. 下载安装 cpolar
3. 运行：
   ```bash
   cpolar http 5000
   ```

---

## 常见问题

### Q: 微信浏览器无法访问？

A: 确保使用 HTTPS 地址。Render 和 Railway 默认提供 HTTPS。

### Q: 数据会丢失吗？

A: Render 免费版会在一段时间无访问后休眠，SQLite 数据会保留。建议定期备份数据库文件。

### Q: 如何备份数据？

A: 从服务器下载 `backend/duty.db` 文件即可。

### Q: 如何添加新用户？

A: 修改 `backend/app.py` 中的 `VALID_NAMES` 列表，添加新姓名后重新部署。

---

## 用户名单

当前已授权用户：
- 夏蒋全（管理员）
- 黄诗颖
- 宋子慧
- 方圆圆
- 朱晨依

---

## 费用说明

| 方案 | 费用 | 优点 | 缺点 |
|------|------|------|------|
| Render.com | 免费 | 自动 HTTPS、稳定 | 休眠后冷启动慢 |
| Railway.app | 免费额度 | 速度快 | 有使用限制 |
| 内网穿透 | 免费 | 完全控制 | 需电脑常开 |
| 本地运行 | 免费 | 最简单 | 仅本机访问 |

**推荐使用 Render.com，完全免费且稳定可靠！**
