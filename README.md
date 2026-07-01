# New API 自动签到脚本

自动化每日签到，适用于开启了"每日签到"功能的 New API 类站点（如 https://api.123nhh.com）。

直连 API（`POST /api/user/checkin`），**不依赖浏览器 / Playwright**，可本地跑，也可用 GitHub Actions 每天自动签到。

## 工作原理

签到就是一个接口调用（前端"每日签到"按钮点下去执行的就是这个）：

```
POST /api/user/checkin
Header: Authorization: <访问令牌>
Header: New-Api-User: <数字用户ID>
```

- 未签到 → 返回 `success:true`，发放 quota 奖励
- 已签到 → 返回 `{"success":false,"message":"今日已签到"}`，脚本会识别为"已完成"而非失败

## 获取凭证（access_token 和 user_id）

用**访问令牌**鉴权，比 session cookie 稳定，不会天天失效。

最可靠的取法（浏览器 DevTools）：

1. 登录网站，按 `F12` 打开开发者工具，切到 **Network（网络）** 标签
2. 刷新页面，随便点开一个 `/api/` 开头的请求
3. 看 **请求头 Request Headers**，直接抄这两个值：
   ```
   Authorization: V9xz............     ← 这是 access_token
   New-Api-User: 1638                  ← 这是 user_id（数字）
   ```

> 也可在 **Application → Local Storage** 的 `user` 对象里找到 `id`（= user_id）和 `access_token`。

## 本地运行

```bash
pip install -r requirements.txt      # 只需 requests

# 复制模板并填入你的凭证
cp config.example.json config.json
# 编辑 config.json，填 access_token 和 user_id

python checkin_api.py
```

> 本机若有失效系统代理导致联网报错，脚本已内置 `trust_env=False` 绕过。

### config.json 格式

```json
{
  "accounts": [
    {
      "name": "主账号",
      "base_url": "https://api.123nhh.com",
      "access_token": "你的访问令牌",
      "user_id": 1638
    }
  ],
  "notification": {
    "enabled": false,
    "webhook_url": ""
  }
}
```

- 支持多账号，数组里加多个对象即可，脚本依次签到
- `name` 仅用于日志显示
- `config.json` 已被 `.gitignore` 忽略，**不会**提交

## GitHub Actions 自动签到

### 1. Fork / Push 本项目到你的 GitHub

### 2. 配置 Secrets

**Settings → Secrets and variables → Actions → New repository secret**

#### `ACCOUNTS_JSON`（必需）

粘贴账号数组（就是 `config.json` 里 `accounts` 的值）：

```json
[
  {
    "name": "主账号",
    "base_url": "https://api.123nhh.com",
    "access_token": "你的访问令牌",
    "user_id": 1638
  }
]
```

#### `NOTIFICATION_WEBHOOK`（可选）

企业微信机器人 Webhook，用于推送签到结果：

```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key
```

### 3. 启用并测试

- **Actions** 标签 → 启用工作流
- **New API 自动签到 → Run workflow** 手动跑一次，看日志

### 4. 定时执行

默认每天北京时间 9:00（UTC 1:00）。改时间就编辑 `.github/workflows/checkin.yml` 的 cron：

```yaml
schedule:
  - cron: '0 1 * * *'   # UTC 1:00 = 北京 9:00
```

常用对照：北京 9:00 → `0 1 * * *`；12:00 → `0 4 * * *`；18:00 → `0 10 * * *`

## 安全提示

⚠️ access_token 等于登录凭证，务必只放进 `config.json`（本地）或 GitHub **Secrets**，**不要**写进任何会提交的文件。

## 项目结构

```
newapi-checkin/
├── .github/workflows/checkin.yml   # GitHub Actions 工作流
├── checkin_api.py                  # 签到脚本（直连 API）
├── config.example.json             # 配置模板
├── config.json                     # 本地配置（被 .gitignore 忽略）
├── requirements.txt                # 依赖：requests
├── .gitignore
└── README.md
```

## 许可证

MIT License
