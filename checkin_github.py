#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New API 自动签到脚本 - GitHub Actions 版本
从环境变量读取配置，适配 GitHub Actions
"""

import os
import sys
import json
import time
import requests
from datetime import datetime


class NewAPICheckin:
    def __init__(self, base_url: str, session_token: str, user_id: str = None, b_user_id: str = None):
        """
        初始化签到客户端
        :param base_url: 网站基础URL，如 https://api.123nhh.com
        :param session_token: 登录后的 session token (从浏览器 Cookie 中获取)
        :param user_id: 用户ID（用于 New-Api-User 请求头）
        :param b_user_id: b-user-id Cookie 值
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })

        # 设置必需的请求头
        if user_id:
            self.session.headers['New-Api-User'] = str(user_id)

        # 设置 Cookies
        if b_user_id:
            self.session.cookies.set('b-user-id', b_user_id, domain=self._get_domain())
        self.session.cookies.set('session', session_token, domain=self._get_domain())

    def _get_domain(self):
        """从 base_url 提取域名"""
        from urllib.parse import urlparse
        return urlparse(self.base_url).netloc

    def check_in(self):
        """
        执行签到操作
        :return: (success: bool, message: str, reward: float)
        """
        try:
            # 尝试常见的签到 API 端点
            check_in_urls = [
                f'{self.base_url}/api/user/check_in',
                f'{self.base_url}/api/user/checkin',
                f'{self.base_url}/api/check-in',
            ]

            for url in check_in_urls:
                try:
                    resp = self.session.post(url, timeout=10)

                    # 如果返回 404，尝试下一个 URL
                    if resp.status_code == 404:
                        continue

                    # 如果返回 401，说明 token 失效
                    if resp.status_code == 401:
                        return False, "登录已失效，请更新 session token", 0.0

                    # 尝试解析 JSON 响应
                    data = resp.json()

                    # 根据常见的响应格式判断成功
                    if data.get('success') or data.get('code') == 0 or resp.status_code == 200:
                        reward = data.get('reward', 0) or data.get('data', {}).get('reward', 0)
                        message = data.get('message', '签到成功')
                        return True, message, reward
                    else:
                        message = data.get('message', '签到失败')
                        return False, message, 0.0

                except requests.exceptions.RequestException:
                    continue

            # 所有 URL 都失败
            return False, "无法找到签到接口，请检查网站地址", 0.0

        except Exception as e:
            return False, f"签到异常: {str(e)}", 0.0

    def get_user_info(self):
        """
        获取用户信息（用于验证登录状态）
        :return: (success: bool, username: str, balance: float)
        """
        try:
            url = f'{self.base_url}/api/user/self'
            resp = self.session.get(url, timeout=10)

            if resp.status_code == 401:
                return False, None, 0.0

            data = resp.json()
            if data.get('success') or data.get('code') == 0:
                user_data = data.get('data', {})
                username = user_data.get('username', 'Unknown')
                balance = user_data.get('quota', 0) / 500000  # 转换为美元
                return True, username, balance

            return False, None, 0.0

        except Exception:
            return False, None, 0.0


def load_config_from_env():
    """从环境变量加载配置"""
    accounts_json = os.getenv('ACCOUNTS_JSON')
    webhook_url = os.getenv('NOTIFICATION_WEBHOOK', '')

    if not accounts_json:
        print("错误: 未找到 ACCOUNTS_JSON 环境变量")
        print("请在 GitHub Secrets 中配置 ACCOUNTS_JSON")
        sys.exit(1)

    try:
        accounts = json.loads(accounts_json)
        if not isinstance(accounts, list):
            raise ValueError("ACCOUNTS_JSON 必须是数组格式")

        return {
            "accounts": accounts,
            "notification": {
                "enabled": bool(webhook_url),
                "webhook_url": webhook_url
            }
        }
    except json.JSONDecodeError as e:
        print(f"错误: ACCOUNTS_JSON 格式不正确: {e}")
        sys.exit(1)


def send_notification(webhook_url: str, title: str, content: str):
    """发送企业微信通知"""
    if not webhook_url:
        return

    try:
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"## {title}\n\n{content}"
            }
        }
        requests.post(webhook_url, json=data, timeout=5)
    except Exception as e:
        print(f"通知发送失败: {e}")


def write_log(message: str):
    """写入日志文件"""
    with open('checkin.log', 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {message}\n")


def main():
    """主函数"""
    print("=" * 50)
    print("New API 自动签到脚本 (GitHub Actions)")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    write_log("=" * 50)
    write_log("开始执行签到任务")

    # 从环境变量加载配置
    config = load_config_from_env()
    accounts = config.get('accounts', [])
    notification_config = config.get('notification', {})

    if not accounts:
        print("错误: 配置中没有账号信息")
        write_log("错误: 配置中没有账号信息")
        sys.exit(1)

    results = []

    # 遍历所有账号
    for account in accounts:
        name = account.get('name', 'Unknown')
        base_url = account.get('base_url')
        session_token = account.get('session_token')
        user_id = account.get('user_id')
        b_user_id = account.get('b_user_id')

        print(f"\n处理账号: {name}")
        print("-" * 50)
        write_log(f"处理账号: {name}")

        if not base_url or not session_token:
            msg = f"配置不完整，跳过"
            print(f"  ⚠️  {msg}")
            write_log(f"  {msg}")
            results.append(f"❌ {name}: 配置不完整")
            continue

        try:
            client = NewAPICheckin(base_url, session_token, user_id, b_user_id)

            # 验证登录状态
            login_ok, username, balance = client.get_user_info()
            if not login_ok:
                msg = "登录验证失败，请更新 session token"
                print(f"  ❌ {msg}")
                write_log(f"  {msg}")
                results.append(f"❌ {name}: 登录失败")
                continue

            print(f"  用户: {username}")
            print(f"  余额: ${balance:.2f}")
            write_log(f"  用户: {username}, 余额: ${balance:.2f}")

            # 执行签到
            success, message, reward = client.check_in()

            if success:
                print(f"  ✅ {message}")
                write_log(f"  签到成功: {message}")
                if reward > 0:
                    print(f"  🎁 奖励: ${reward:.2f}")
                    write_log(f"  奖励: ${reward:.2f}")
                    results.append(f"✅ {name}: {message} (+${reward:.2f})")
                else:
                    results.append(f"✅ {name}: {message}")
            else:
                print(f"  ❌ {message}")
                write_log(f"  签到失败: {message}")
                results.append(f"❌ {name}: {message}")

            # 避免请求过快
            time.sleep(2)

        except Exception as e:
            msg = f"异常: {e}"
            print(f"  ❌ {msg}")
            write_log(f"  {msg}")
            results.append(f"❌ {name}: {str(e)}")

    # 发送通知
    if notification_config.get('enabled'):
        summary = "\n".join(results)
        send_notification(
            notification_config.get('webhook_url'),
            "New API 签到结果",
            summary
        )
        print("\n已发送企业微信通知")

    print("\n" + "=" * 50)
    print("签到完成")
    print("=" * 50)
    write_log("签到任务完成")
    write_log("=" * 50)


if __name__ == '__main__':
    main()
