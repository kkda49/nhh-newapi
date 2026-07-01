#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试脚本 - 验证 session token 是否有效
"""

import requests

# 你的配置
BASE_URL = "https://api.123nhh.com"
SESSION_TOKEN = "MTc4Mjg3NzA5MHxEWDhFQVFMX2dBQUJFQUVRQUFEX3ZQLUFBQVlHYzNSeWFXNW5EQVFBQW1sa0EybHVkQVFFQVA0TXpBWnpkSEpwYm1jTUNnQUlkWE5sY201aGJXVUdjM1J5YVc1bkRBWUFCR1JoTkRrR2MzUnlhVzVuREFZQUJISnZiR1VEYVc1MEJBSUFBZ1p6ZEhKcGJtY01DQUFHYzNSaGRIVnpBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBY0FCV2R5YjNWd0JuTjBjbWx1Wnd3SkFBZGtaV1poZFd4MEJuTjBjbWx1Wnd3TkFBdHZZWFYwYUY5emRHRjBaUVp6ZEhKcGJtY01EZ0FNT1VObGIyVjZjV2hwUWpnenyxvLS2pMWrZNBaf5og2wL3F7CGVGXo3gxypB7DMdQIWw=="

output = []
output.append("=" * 60)
output.append("测试 Session Token 有效性")
output.append("=" * 60)

# 创建 session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cache-Control': 'no-store',
    'Referer': 'https://api.123nhh.com/console/token',
    'New-Api-User': '1638',  # 关键：用户ID
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
})

# 设置 Cookie - 需要同时设置 b-user-id 和 session
session.cookies.set('b-user-id', 'ca59aa82-4fdd-a741-5284-073acedaa2b9', domain='api.123nhh.com')
session.cookies.set('session', SESSION_TOKEN, domain='api.123nhh.com')

output.append(f"\n1. 测试 Cookie:")
output.append(f"   b-user-id=ca59aa82-4fdd-a741-5284-073acedaa2b9")
output.append(f"   session={SESSION_TOKEN[:50]}...")

# 测试获取用户信息
try:
    output.append(f"\n2. 请求用户信息: {BASE_URL}/api/user/self")
    resp = session.get(f'{BASE_URL}/api/user/self', timeout=10)

    output.append(f"   状态码: {resp.status_code}")

    if resp.status_code == 401:
        output.append("\n[失败] Token 已失效或格式不正确")
        output.append("   原因: 服务器返回 401 未授权")
        output.append("   解决: 需要重新从浏览器获取最新的 session token")
        output.append("\n获取方法:")
        output.append("1. 打开浏览器，登录 https://api.123nhh.com")
        output.append("2. F12 -> Application -> Cookies -> api.123nhh.com")
        output.append("3. 找到 session，复制完整的 Value")
        output.append("4. 或者在 Network 标签，找请求头里的 Cookie: session=xxx")
    elif resp.status_code == 200:
        data = resp.json()
        output.append(f"\n[成功] Token 有效！")
        output.append(f"   响应数据: {data}")

        if data.get('success') or data.get('data'):
            user_data = data.get('data', {})
            output.append(f"\n用户信息:")
            output.append(f"   用户名: {user_data.get('username', 'Unknown')}")
            output.append(f"   余额: ${user_data.get('quota', 0) / 500000:.2f}")
    else:
        output.append(f"\n[警告] 意外状态码: {resp.status_code}")
        output.append(f"   响应内容: {resp.text[:500]}")

except Exception as e:
    output.append(f"\n[错误] 请求失败: {e}")

output.append("\n" + "=" * 60)

# 写入文件
result = "\n".join(output)
with open('test_result.txt', 'w', encoding='utf-8') as f:
    f.write(result)

print("Test completed. Check test_result.txt")
