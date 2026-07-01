#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New API 自动签到脚本 (直连 API 版本)
用系统访问令牌 (Authorization 头) 直接调用 POST /api/user/checkin，
不再依赖浏览器 / Playwright，适合 GitHub Actions。
"""

import os
import sys
import json
from datetime import datetime

import requests


class NewAPICheckin:
    def __init__(self, base_url: str, access_token: str, user_id):
        """
        :param base_url:     网站基础 URL，如 https://api.123nhh.com
        :param access_token: 访问令牌 (Authorization 头)
        :param user_id:      数字用户 ID (New-Api-User 头，必填)
        """
        self.base_url = base_url.rstrip('/')
        self.access_token = access_token.strip()
        self.user_id = str(user_id).strip()
        self.session = requests.Session()
        self.session.trust_env = False  # 绕开失效的系统代理；CI 上也安全
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Authorization': self.access_token,
            'New-Api-User': self.user_id,  # 访问令牌鉴权必须带这个头
        })

    def get_user_info(self):
        """
        验证令牌并获取用户信息
        :return: (ok: bool, username: str|None, balance: float, raw: str)
        """
        try:
            resp = self.session.get(f'{self.base_url}/api/user/self', timeout=15)
        except Exception as e:
            return False, None, 0.0, f"请求异常: {e}"

        raw = resp.text[:300]
        if resp.status_code != 200:
            return False, None, 0.0, f"HTTP {resp.status_code}: {raw}"

        try:
            data = resp.json()
        except Exception:
            return False, None, 0.0, f"非 JSON 响应: {raw}"

        if data.get('success'):
            u = data.get('data', {}) or {}
            username = u.get('display_name') or u.get('username', 'Unknown')
            balance = u.get('quota', 0) / 500000  # New API: 500000 quota = $1
            return True, username, balance, raw

        return False, None, 0.0, f"鉴权失败: {data.get('message', raw)}"

    def check_in(self):
        """
        执行签到
        :return: (success: bool, message: str, raw: str)
        """
        try:
            resp = self.session.post(
                f'{self.base_url}/api/user/checkin',
                timeout=15,
            )
        except Exception as e:
            return False, f"请求异常: {e}", ""

        raw = resp.text[:300]

        try:
            data = resp.json()
        except Exception:
            return False, f"非 JSON 响应 (HTTP {resp.status_code}): {raw}", raw

        msg = data.get('message', '') or data.get('data', '') or raw
        if data.get('success'):
            return True, str(msg) or "签到成功", raw

        # 已签到通常返回 success=false + "已签到" 之类的提示，视为非失败
        if any(k in str(msg) for k in ('已签到', '已经签到', 'already', '重复')):
            return True, str(msg), raw

        return False, str(msg), raw


def send_notification(webhook_url: str, title: str, content: str):
    """发送企业微信 markdown 通知"""
    if not webhook_url:
        return
    try:
        requests.post(webhook_url, json={
            "msgtype": "markdown",
            "markdown": {"content": f"## {title}\n\n{content}"}
        }, timeout=5)
    except Exception as e:
        print(f"通知发送失败: {e}")


def write_log(message: str):
    with open('checkin.log', 'a', encoding='utf-8') as f:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{ts}] {message}\n")


def load_accounts():
    """
    优先从环境变量 ACCOUNTS_JSON 读取 (GitHub Actions)，
    否则回退到本地 config.json (本地测试)。
    """
    accounts_json = os.getenv('ACCOUNTS_JSON')
    if accounts_json:
        return json.loads(accounts_json), os.getenv('NOTIFICATION_WEBHOOK', '')

    if os.path.exists('config.json'):
        with open('config.json', encoding='utf-8') as f:
            cfg = json.load(f)
        return cfg.get('accounts', []), cfg.get('notification', {}).get('webhook_url', '')

    return [], ''


def main():
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    print("=" * 50)
    print("New API 自动签到脚本 (直连 API)")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    write_log("=" * 50)
    write_log("开始执行签到任务 (直连 API)")

    try:
        accounts, webhook_url = load_accounts()
    except json.JSONDecodeError as e:
        print(f"配置解析失败: {e}")
        sys.exit(1)

    if not accounts:
        print("未配置任何账号")
        sys.exit(1)

    results = []

    for account in accounts:
        name = account.get('name', 'Unknown')
        base_url = account.get('base_url')
        access_token = account.get('access_token')
        user_id = account.get('user_id')

        print(f"\n处理账号: {name}")
        print("-" * 50)
        write_log(f"处理账号: {name}")

        if not base_url or not access_token or not user_id:
            print("  ⚠️  配置不完整(需要 base_url / access_token / user_id)，跳过")
            results.append(f"❌ {name}: 配置不完整")
            continue

        client = NewAPICheckin(base_url, access_token, user_id)

        ok, username, balance, raw = client.get_user_info()
        if not ok:
            print(f"  ❌ 令牌验证失败: {raw}")
            write_log(f"  令牌验证失败: {raw}")
            results.append(f"❌ {name}: 令牌无效")
            continue

        print(f"  用户: {username}")
        print(f"  余额: ${balance:.2f}")
        write_log(f"  用户: {username}, 余额: ${balance:.2f}")

        success, message, raw = client.check_in()
        print(f"  原始响应: {raw}")
        if success:
            print(f"  ✅ {message}")
            write_log(f"  签到成功: {message}")
            results.append(f"✅ {name}: {message}")
        else:
            print(f"  ❌ {message}")
            write_log(f"  签到失败: {message}")
            results.append(f"❌ {name}: {message}")

    print("\n" + "=" * 50)
    print("签到完成")
    print("=" * 50)

    summary = "\n".join(results)
    print(summary)

    if webhook_url:
        content = f"**运行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "\n\n".join(results)
        send_notification(webhook_url, "New API 签到结果", content)
        print("\n通知已发送")

    write_log("任务结束")


if __name__ == "__main__":
    main()
