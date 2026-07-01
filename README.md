# New API 自动签到脚本

自动化签到脚本，适用于 New API 类型的网站（如 https://api.123nhh.com）

## 功能特性

- ✅ 支持多账号批量签到
- ✅ 自动获取用户信息和余额
- ✅ 支持企业微信通知
- ✅ 智能重试和错误处理
- ✅ 可配合 Windows 任务计划实现定时签到

## 安装步骤

### 1. 安装 Python

确保已安装 Python 3.7+

```bash
python --version
```

### 2. 安装依赖

```bash
cd newapi-checkin
pip install requests
```

如果遇到代理问题，参考你的记忆设置：
```bash
set NO_PROXY=*
pip install requests
```

## 配置说明

### 获取 Session Token

1. 打开浏览器，登录 https://api.123nhh.com
2. 按 `F12` 打开开发者工具
3. 切换到 **Network（网络）** 标签
4. 刷新页面或点击任意功能
5. 查找请求头中的 Cookie，找到类似以下内容：
   ```
   Cookie: session=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
6. 复制 `session=` 后面的完整值

### 编辑配置文件

编辑 `config.json`：

```json
{
  "accounts": [
    {
      "name": "主账号",
      "base_url": "https://api.123nhh.com",
      "session_token": "你的_session_token"
    },
    {
      "name": "备用账号",
      "base_url": "https://api.123nhh.com",
      "session_token": "另一个_token"
    }
  ],
  "notification": {
    "enabled": false,
    "webhook_url": ""
  }
}
```

**多账号说明：**
- 可以添加多个账号，脚本会依次签到
- `name` 字段仅用于日志显示

**通知配置（可选）：**
```json
"notification": {
  "enabled": true,
  "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key"
}
```

## 使用方法

### 手动运行

```bash
python checkin.py
```

### 定时任务

#### Windows 任务计划

1. 打开 **任务计划程序**
2. 创建基本任务
3. 设置触发器：每天上午 9:00
4. 操作：
   - 程序：`C:\Python\python.exe`（你的 Python 路径）
   - 参数：`C:\Users\l\newapi-checkin\checkin.py`
   - 起始于：`C:\Users\l\newapi-checkin`

#### Linux Crontab

```bash
# 每天 9:00 执行
0 9 * * * cd /path/to/newapi-checkin && python3 checkin.py >> checkin.log 2>&1
```

## 常见问题

### 1. 签到失败：登录已失效

**原因：** Session token 过期

**解决：**
- 重新从浏览器获取最新的 session token
- 更新 `config.json` 中的 `session_token`

### 2. 无法找到签到接口

**原因：** 网站 API 路径可能不同

**解决：**
1. 手动在网站上点击签到按钮
2. 在浏览器开发者工具的 Network 标签查看请求
3. 找到签到接口的完整 URL
4. 修改 `checkin.py` 中的 `check_in_urls` 列表

### 3. 中文输出乱码

参考你的记忆配置，脚本已使用 UTF-8 编码处理

## 安全提示

⚠️ **重要：**
- Session token 相当于你的登录凭证，请妥善保管
- 不要将包含真实 token 的 `config.json` 上传到公开仓库
- 建议添加 `.gitignore` 忽略配置文件：
  ```
  config.json
  *.log
  ```

## GitHub Actions 自动签到

### 1. Fork 本项目到你的 GitHub

### 2. 配置 Secrets

进入你的仓库：**Settings → Secrets and variables → Actions → New repository secret**

添加以下 Secrets：

#### ACCOUNTS_JSON（必需）

存储账号信息的 JSON 数组：

```json
[
  {
    "name": "主账号",
    "base_url": "https://api.123nhh.com",
    "session_token": "你的_session_token"
  },
  {
    "name": "备用账号",
    "base_url": "https://api.123nhh.com",
    "session_token": "另一个_token"
  }
]
```

**注意：** 直接粘贴完整的 JSON 数组，确保格式正确。

#### NOTIFICATION_WEBHOOK（可选）

企业微信机器人 Webhook URL：

```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key
```

### 3. 启用 GitHub Actions

- 进入仓库的 **Actions** 标签
- 点击 **I understand my workflows, go ahead and enable them**

### 4. 手动测试

- 进入 **Actions** → **New API 自动签到**
- 点击 **Run workflow** → **Run workflow**
- 查看运行日志

### 5. 定时执行

工作流已配置为每天北京时间 9:00 (UTC 1:00) 自动执行。

如需修改时间，编辑 `.github/workflows/checkin.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '0 1 * * *'  # UTC 1:00 = 北京时间 9:00
```

**常用时间对照：**
- 北京时间 9:00 → `0 1 * * *`
- 北京时间 12:00 → `0 4 * * *`
- 北京时间 18:00 → `0 10 * * *`

### 获取 Session Token 方法

参见上面的"获取 Session Token"章节。

## 项目结构

```
newapi-checkin/
├── .github/
│   └── workflows/
│       └── checkin.yml      # GitHub Actions 工作流
├── checkin.py               # 本地运行脚本
├── checkin_github.py        # GitHub Actions 脚本
├── config.json              # 本地配置文件（不提交）
├── requirements.txt         # Python 依赖
├── .gitignore              # Git 忽略文件
└── README.md               # 说明文档
```

## 许可证

MIT License
