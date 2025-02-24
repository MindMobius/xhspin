import datetime
import json
from time import sleep
import os

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

from xhs import DataFetchError, XhsClient, help
from parser import XHSParser
from monitor import XHSMonitor

load_dotenv()


def sign(uri, data=None, a1="", web_session=""):
    for _ in range(10):
        try:
            with sync_playwright() as playwright:
                stealth_js_path = "stealth.min.js"
                chromium = playwright.chromium

                # 如果一直失败可尝试设置成 False 让其打开浏览器，适当添加 sleep 可查看浏览器状态
                browser = chromium.launch(headless=True)

                browser_context = browser.new_context()
                browser_context.add_init_script(path=stealth_js_path)
                context_page = browser_context.new_page()
                context_page.goto("https://www.xiaohongshu.com")
                browser_context.add_cookies([
                    {'name': 'a1', 'value': a1, 'domain': ".xiaohongshu.com", 'path': "/"}]
                )
                context_page.reload()
                # 这个地方设置完浏览器 cookie 之后，如果这儿不 sleep 一下签名获取就失败了，如果经常失败请设置长一点试试
                sleep(1)
                encrypt_params = context_page.evaluate("([url, data]) => window._webmsxyw(url, data)", [uri, data])
                return {
                    "x-s": encrypt_params["X-s"],
                    "x-t": str(encrypt_params["X-t"])
                }
        except Exception:
            # 这儿有时会出现 window._webmsxyw is not a function 或未知跳转错误，因此加一个失败重试趴
            pass
    raise Exception("重试了这么多次还是无法签名成功，寄寄寄")


if __name__ == '__main__':
    cookie = os.getenv("XHS_COOKIE")
    user_ids = os.getenv("XHS_USER_IDS", "").split(",")
    if not cookie:
        raise ValueError("请在.env文件中设置XHS_COOKIE")
    if not user_ids:
        raise ValueError("请在.env文件中设置XHS_USER_IDS")

    xhs_client = XhsClient(cookie, sign=sign)
    monitor = XHSMonitor(xhs_client, user_ids)
    
    # 开始监控，每5分钟检查一次
    monitor.monitor(interval=300)