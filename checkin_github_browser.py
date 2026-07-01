#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
New API 自动签到脚本 (浏览器自动化版本 - GitHub Actions)
使用 Playwright 模拟浏览器操作进行签到
"""

import os
import sys
import json
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class NewAPICheckinBrowser:
    def __init__(self, base_url: str, session_token: str, user_id: str = None, b_user_id: str = None):
        """
        初始化签到客户端
        :param base_url: 网站基础URL
        :param session_token: session Cookie
        :param user_id: 用户ID
        :param b_user_id: b-user-id Cookie
        """
        self.base_url = base_url.rstrip('/')
        self.session_token = session_token
        self.user_id = user_id
        self.b_user_id = b_user_id
        self.domain = self._get_domain()

    def _get_domain(self):
        """从 base_url 提取域名"""
        from urllib.parse import urlparse
        return urlparse(self.base_url).netloc

    def check_in(self):
        """
        执行签到操作（使用浏览器自动化）
        :return: (success: bool, message: str, reward: float)
        """
        with sync_playwright() as p:
            # 启动浏览器（无头模式）
            browser = p.chromium.launch(headless=True)

            # 创建浏览器上下文
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )

            # 设置 Cookies
            cookies = [
                {
                    'name': 'session',
                    'value': self.session_token,
                    'domain': self.domain,
                    'path': '/',
                }
            ]

            if self.b_user_id:
                cookies.append({
                    'name': 'b-user-id',
                    'value': self.b_user_id,
                    'domain': self.domain,
                    'path': '/',
                })

            context.add_cookies(cookies)

            # 创建页面
            page = context.new_page()

            try:
                # 访问个人设置页面
                settings_url = f'{self.base_url}/console/profile'
                print(f"  访问个人设置页面: {settings_url}")
                page.goto(settings_url, wait_until='networkidle', timeout=30000)

                # 等待页面加载
                page.wait_for_timeout(2000)

                # 查找"每日签到"模块
                # 可能的选择器：包含"每日签到"文本的元素
                checkin_section = None
                try:
                    # 尝试找到"每日签到"文本
                    checkin_section = page.locator('text=每日签到').first
                    if checkin_section.is_visible(timeout=5000):
                        print("  ✓ 找到每日签到模块")
                except:
                    pass

                if not checkin_section:
                    return False, "未找到每日签到模块", 0.0

                # 查找签到按钮或状态
                # 可能的情况：
                # 1. "加载中..." 按钮 - 需要点击
                # 2. "已签到" 状态 - 今天已签到

                # 先检查是否已签到
                try:
                    already_checked = page.locator('text=已签到').first
                    if already_checked.is_visible(timeout=2000):
                        print("  ℹ 今天已经签到过了")
                        return True, "今日已签到", 0.0
                except:
                    pass

                # 等待页面完全加载，按钮状态可能会从"加载中"变为"签到"
                print("  → 等待页面完全加载...")
                page.wait_for_timeout(5000)

                # 查找签到按钮 - 尝试多种可能的选择器
                button_selectors = [
                    'button:has-text("签到")',
                    'button:has-text("加载中")',
                    'div[role="button"]:has-text("签到")',
                    'div[role="button"]:has-text("加载中")',
                    '.checkin-button',
                    '[class*="check"] button',
                    'button',  # 作为最后的fallback
                ]

                button = None
                for selector in button_selectors:
                    try:
                        btn = page.locator(selector).first
                        if btn.is_visible(timeout=2000):
                            button = btn
                            button_text = btn.inner_text()
                            print(f"  ✓ 找到按钮: {selector}, 文本: {button_text}")
                            break
                    except:
                        continue

                if not button:
                    # 截图调试
                    screenshot_path = 'checkin_page.png'
                    page.screenshot(path=screenshot_path)
                    print(f"  ⚠ 未找到签到按钮，已截图保存到 {screenshot_path}")
                    return False, "未找到签到按钮", 0.0

                # 点击签到按钮
                print("  → 点击按钮...")
                button.click()

                # 等待签到结果
                page.wait_for_timeout(3000)

                # 检查签到结果
                # 可能的成功标志：
                # 1. 出现"已签到"文本
                # 2. 按钮状态变化
                # 3. 出现成功提示

                success_indicators = [
                    'text=已签到',
                    'text=签到成功',
                    'text=奖励',
                ]

                for indicator in success_indicators:
                    try:
                        element = page.locator(indicator).first
                        if element.is_visible(timeout=2000):
                            print("  ✓ 签到成功")

                            # 尝试提取奖励信息
                            reward = 0.0
                            try:
                                # 查找余额变化或奖励提示
                                page_text = page.content()
                                # 这里可以根据实际页面结构解析奖励金额
                            except:
                                pass

                            return True, "签到成功", reward
                    except:
                        continue

                # 如果没有明确的成功标志，截图并返回
                screenshot_path = 'checkin_result.png'
                page.screenshot(path=screenshot_path)
                print(f"  ⚠ 无法确认签到结果，已截图保存到 {screenshot_path}")
                return False, "无法确认签到结果", 0.0

            except PlaywrightTimeout as e:
                return False, f"页面加载超时: {str(e)}", 0.0
            except Exception as e:
                return False, f"签到异常: {str(e)}", 0.0
            finally:
                # 关闭浏览器
                page.close()
                context.close()
                browser.close()

    def get_user_info(self):
        """
        获取用户信息（验证登录状态）
        :return: (success: bool, username: str, balance: float)
        """
        import requests

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

        if self.user_id:
            session.headers['New-Api-User'] = str(self.user_id)

        if self.b_user_id:
            session.cookies.set('b-user-id', self.b_user_id, domain=self.domain)
        session.cookies.set('session', self.session_token, domain=self.domain)

        try:
            url = f'{self.base_url}/api/user/self'
            resp = session.get(url, timeout=10)

            if resp.status_code == 401:
                return False, None, 0.0

            data = resp.json()
            if data.get('success') or data.get('code') == 0:
                user_data = data.get('data', {})
                username = user_data.get('username', 'Unknown')
                balance = user_data.get('quota', 0) / 500000
                return True, username, balance

            return False, None, 0.0

        except Exception:
            return False, None, 0.0


def send_notification(webhook_url: str, title: str, content: str):
    """发送企业微信通知"""
    if not webhook_url:
        return

    import requests
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
    # 设置标准输出编码为 UTF-8
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    print("=" * 50)
    print("New API 自动签到脚本 (GitHub Actions)")
    print(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    write_log("=" * 50)
    write_log("开始执行签到任务 (浏览器自动化)")

    # 从环境变量加载配置
    accounts_json = os.getenv('ACCOUNTS_JSON', '[]')
    webhook_url = os.getenv('NOTIFICATION_WEBHOOK', '')

    try:
        accounts = json.loads(accounts_json)
    except json.JSONDecodeError as e:
        print(f"配置解析失败: {e}")
        write_log(f"配置解析失败: {e}")
        sys.exit(1)

    if not accounts:
        print("未配置任何账号")
        write_log("未配置任何账号")
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
            client = NewAPICheckinBrowser(base_url, session_token, user_id, b_user_id)

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

            # 执行签到（浏览器自动化）
            success, message, reward = client.check_in()

            if success:
                print(f"  ✅ {message}")
                write_log(f"  签到成功: {message}")
                results.append(f"✅ {name}: {message}")
            else:
                print(f"  ❌ {message}")
                write_log(f"  签到失败: {message}")
                results.append(f"❌ {name}: {message}")

        except Exception as e:
            msg = f"处理异常: {str(e)}"
            print(f"  ❌ {msg}")
            write_log(f"  {msg}")
            results.append(f"❌ {name}: 异常")

    # 汇总结果
    print("\n" + "=" * 50)
    print("签到完成")
    print("=" * 50)
    write_log("=" * 50)
    write_log("签到完成")

    summary = "\n".join(results)
    print(summary)

    # 发送通知
    if webhook_url:
        notification_content = f"**运行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        notification_content += "\n\n".join(results)
        send_notification(webhook_url, "New API 签到结果", notification_content)
        print("\n通知已发送")

    write_log("任务结束")


if __name__ == "__main__":
    main()
