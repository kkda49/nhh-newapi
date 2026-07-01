#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试脚本 - 直接测试浏览器签到（跳过登录验证）
"""

import os
from playwright.sync_api import sync_playwright

# 配置
BASE_URL = "https://api.123nhh.com"
SESSION_TOKEN = "MTc4Mjg3NzA5MHxEWDhFQVFMX2dBQUJFQUVRQUFEX3ZQLUFBQVlHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0TXpBWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRBWUFCR1JoTkRrR2MzUnlhVzVuREFZQUJISnZiR1VEYVc1NEJBSUFBZ1p6ZEhKcGJtY01DQUFHYzNSaGRIVnpBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBY0FCV2R5YjNWd0JuTjBjbWx1Wnd3SkFBZGtaV1poZFd4MEJuTjBjbWx1Wnd3TkFBdHZZWFYwYUY5emRHRjBaUVp6ZEhKcGJtY01EZ0FNT1VObGIyVjZjV2hwUWpnenyxvLS2pMWrZNBaf5og2wL3F7CGVGXo3gxypB7DMdQIWw=="
B_USER_ID = "ca59aa82-4fdd-a741-5284-073acedaa2b9"

print("=" * 60)
print("浏览器自动化签到测试")
print("=" * 60)

with sync_playwright() as p:
    print("\n1. 启动浏览器...")
    browser = p.chromium.launch(headless=False)  # 非无头模式，可以看到操作过程

    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        viewport={'width': 1920, 'height': 1080}
    )

    # 设置 Cookies
    print("2. 设置 Cookies...")
    cookies = [
        {
            'name': 'session',
            'value': SESSION_TOKEN,
            'domain': 'api.123nhh.com',
            'path': '/',
        },
        {
            'name': 'b-user-id',
            'value': B_USER_ID,
            'domain': 'api.123nhh.com',
            'path': '/',
        }
    ]
    context.add_cookies(cookies)

    page = context.new_page()

    try:
        # 访问个人设置页面
        settings_url = f'{BASE_URL}/console/profile'
        print(f"3. 访问个人设置页面: {settings_url}")
        page.goto(settings_url, wait_until='domcontentloaded', timeout=60000)

        # 等待页面加载
        print("4. 等待页面加载...")
        page.wait_for_timeout(5000)

        # 保存截图
        screenshot_path = 'page_loaded.png'
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"   已截图保存到: {screenshot_path}")

        # 打印页面 HTML（部分）
        page_html = page.content()
        with open('page_content.html', 'w', encoding='utf-8') as f:
            f.write(page_html)
        print(f"   已保存页面 HTML 到: page_content.html")

        # 查找包含"每日签到"的元素
        print("\n5. 查找签到相关元素...")

        # 尝试找到所有包含"签到"的文本
        checkin_texts = page.locator('text=/签到/').all()
        print(f"   找到 {len(checkin_texts)} 个包含'签到'的元素")

        # 查找按钮
        buttons = page.locator('button').all()
        print(f"   页面共有 {len(buttons)} 个按钮")

        # 尝试各种选择器
        selectors = [
            'button:has-text("签到")',
            'button:has-text("加载")',
            '[role="button"]:has-text("签到")',
            'div:has-text("每日签到")',
        ]

        for selector in selectors:
            try:
                elements = page.locator(selector).all()
                if elements:
                    print(f"   ✓ 选择器 '{selector}' 找到 {len(elements)} 个元素")
            except Exception as e:
                print(f"   ✗ 选择器 '{selector}' 失败: {e}")

        print("\n6. 等待30秒让你手动查看页面...")
        print("   （你可以在浏览器中手动操作）")
        page.wait_for_timeout(30000)

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        page.screenshot(path='error.png', full_page=True)
        print("   已保存错误截图到: error.png")

    finally:
        print("\n7. 关闭浏览器...")
        page.close()
        context.close()
        browser.close()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
