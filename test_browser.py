#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试脚本 - 测试浏览器自动化签到
"""

import os
import sys

# 设置测试配置
os.environ['ACCOUNTS_JSON'] = '[{"name":"Da49","base_url":"https://api.123nhh.com","session_token":"MTc4Mjg5MDAwMHxEWDhFQVFMX2dBQUJFQUVRQUFEX3ZQLUFBQVlHYzNSeWFXNW5EQWNBQldkeWIzVndCbk4wY21sdVp3d0pBQWRrWldaaGRXeDBCbk4wY21sdVp3d05BQXR2WVhWMGFGOXpkR0YwWlFaemRISnBibWNNRGdBTWNrbElRa1JIVDNFMWEzUkVCbk4wY21sdVp3d0VBQUpwWkFOcGJuUUVCQUQtRE13R2MzUnlhVzVuREFvQUNIVnpaWEp1WVcxbEJuTjBjbWx1Wnd3R0FBUmtZVFE1Qm5OMGNtbHVad3dHQUFSeWIyeGxBMmx1ZEFRQ0FBSUdjM1J5YVc1bkRBZ0FCbk4wWVhSMWN3TnBiblFFQWdBQ3z36hd18TNIW_hYy2-kydnkITFNBfHm_xxS86bQ7TZL2g==","user_id":"1638","b_user_id":"ca59aa82-4fdd-a741-5284-073acedaa2b9"}]'

# 导入主程序
sys.path.insert(0, os.path.dirname(__file__))
from checkin_github_browser import main

if __name__ == "__main__":
    print("开始本地测试...")
    main()
