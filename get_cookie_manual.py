#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试：直接在浏览器手动登录后获取 Cookie
"""

from playwright.sync_api import sync_playwright
import json

print("=" * 60)
print("手动登录获取 Cookie")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print("\n1. 打开登录页面...")
    page.goto("https://api.123nhh.com/login")

    print("\n2. 请在浏览器中手动登录...")
    print("   登录成功后，会自动跳转到控制台")
    print("   等待跳转完成后按 Enter 继续...")
    input()

    print("\n3. 获取 Cookies...")
    cookies = context.cookies()

    session_cookie = None
    b_user_id_cookie = None

    for cookie in cookies:
        if cookie['name'] == 'session':
            session_cookie = cookie['value']
        if cookie['name'] == 'b-user-id':
            b_user_id_cookie = cookie['value']

    if session_cookie:
        print(f"\n✓ Session Token: {session_cookie}")
    else:
        print("\n✗ 未找到 session cookie")

    if b_user_id_cookie:
        print(f"✓ B-User-ID: {b_user_id_cookie}")
    else:
        print("✗ 未找到 b-user-id cookie")

    # 尝试访问个人设置页面
    if session_cookie:
        print("\n4. 访问个人设置页面...")
        page.goto("https://api.123nhh.com/console/profile")
        page.wait_for_timeout(3000)

        page.screenshot(path='logged_in_profile.png', full_page=True)
        print("   已截图保存到: logged_in_profile.png")

        # 查找签到相关元素
        print("\n5. 查找签到元素...")
        page_text = page.content()

        if '签到' in page_text:
            print("   ✓ 页面包含'签到'文本")
        else:
            print("   ✗ 页面不包含'签到'文本")

    print("\n按 Enter 关闭浏览器...")
    input()

    browser.close()

print("\n" + "=" * 60)
print("完成")
print("=" * 60)
