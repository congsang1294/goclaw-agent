#!/usr/bin/env python3
"""
auto_config.py — Cấu hình Facebook Page 1 lần.
Chạy tuần tự:
  1. Nhập short-lived token → đổi sang long-lived token (60 ngày)
  2. Gọi /me/accounts → list Fanpage
  3. User chọn page → ghi đè file .env
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, ".env")

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

def print_step(msg):
    print(f"\n{CYAN}▶ {msg}{RESET}")

def print_ok(msg):
    print(f"  {GREEN}✓ {msg}{RESET}")

def print_warn(msg):
    print(f"  {YELLOW}⚠ {msg}{RESET}")

def print_err(msg):
    print(f"  {RED}✗ {msg}{RESET}")

def api_get(url):
    """GET request với retry."""
    for attempt in range(2):
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            if attempt == 0:
                print_warn(f"Lỗi: {e}. Thử lại sau 3 giây...")
                import time
                time.sleep(3)
            else:
                raise
    return None

def read_env():
    """Đọc .env hiện tại thành dict."""
    env = {}
    if not os.path.isfile(ENV_PATH):
        return env
    with open(ENV_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def write_env(env):
    """Ghi dict vào .env."""
    with open(ENV_PATH, "w") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")

def exchange_long_lived_token(short_token, app_id, app_secret):
    """Đổi short-lived → long-lived token (60 ngày)."""
    url = (
        f"https://graph.facebook.com/v21.0/oauth/access_token"
        f"?grant_type=fb_exchange_token"
        f"&client_id={app_id}"
        f"&client_secret={app_secret}"
        f"&fb_exchange_token={short_token}"
    )
    data = api_get(url)
    if data and "access_token" in data:
        return data["access_token"]
    return None

def get_pages(token):
    """Lấy danh sách Fanpage từ /me/accounts."""
    url = f"https://graph.facebook.com/v21.0/me/accounts?access_token={token}&limit=50"
    data = api_get(url)
    if data and "data" in data:
        return data["data"]
    return []

def main():
    print(f"\n{GREEN}══════════════════════════════════════{RESET}")
    print(f"{GREEN}  CẤU HÌNH FACEBOOK PAGE{RESET}")
    print(f"{GREEN}══════════════════════════════════════{RESET}")

    env = read_env()

    # Bước 1: Nhập short-lived token
    print_step("Bước 1: Lấy Long-Lived Token")
    print("  Lấy short-lived token ở: https://developers.facebook.com/tools/access_token/")
    short_token = input("  Dán short-lived access token vào đây: ").strip()
    if not short_token:
        print_err("Không có token. Thoát.")
        sys.exit(1)

    # Thử exchange trực tiếp (không có app_secret thì dùng thẳng short_token)
    print("  Đang đổi sang long-lived token (60 ngày)...")
    app_id = input("  Nhập App ID (Facebook App): ").strip() or ""
    app_secret = input("  Nhập App Secret: ").strip() or ""

    long_token = short_token
    if app_id and app_secret:
        try:
            result = exchange_long_lived_token(short_token, app_id, app_secret)
            if result:
                long_token = result
                print_ok("Đã đổi sang long-lived token thành công!")
            else:
                print_warn("Không exchange được, dùng token gốc (có thể hết hạn sau 2h).")
        except Exception as e:
            print_warn(f"Exchange lỗi: {e}. Dùng token gốc.")
    else:
        print_warn("Không có App ID/Secret, dùng short-lived token (có thể hết hạn nhanh).")

    access_token = long_token
    env["FB_ACCESS_TOKEN"] = access_token
    write_env(env)

    # Bước 2: Lấy danh sách Fanpage
    print_step("Bước 2: Lấy danh sách Fanpage")
    print("  Đang gọi API Facebook...")

    try:
        pages = get_pages(access_token)
    except Exception as e:
        print_err(f"Lỗi khi gọi API: {e}")
        print("  Thử lại với token hợp lệ.")
        sys.exit(1)

    if not pages:
        print_err("Không tìm thấy Fanpage nào trong tài khoản này.")
        print("  Kiểm tra: token có quyền 'pages_manage_posts', 'pages_read_engagement' không.")
        sys.exit(1)

    print(f"\n  {GREEN}Tìm thấy {len(pages)} Fanpage:{RESET}")
    for i, page in enumerate(pages):
        print(f"    {i+1}. {page.get('name', 'N/A')} (ID: {page.get('id', 'N/A')})")

    # Bước 3: Chọn page
    print_step("Bước 3: Chọn Fanpage")
    while True:
        try:
            choice = int(input("  Chọn số thứ tự Fanpage: ").strip())
            if 1 <= choice <= len(pages):
                break
            else:
                print_warn(f"Chọn số từ 1 đến {len(pages)}.")
        except ValueError:
            print_warn("Nhập số hợp lệ.")

    selected = pages[choice - 1]
    page_id = selected["id"]
    page_name = selected.get("name", "")
    page_token = selected.get("access_token", access_token)

    print_ok(f"Đã chọn: {page_name} (ID: {page_id})")

    # Bước 4: Ghi đè .env
    print_step("Bước 4: Ghi cấu hình vào .env")
    env["FB_PAGE_ID"] = page_id
    env["FB_PAGE_NAME"] = page_name
    env["FB_ACCESS_TOKEN"] = page_token
    env["DRY_RUN"] = "true"  # mặc định an toàn
    write_env(env)

    print_ok(f"Đã ghi vào: {ENV_PATH}")
    print(f"\n{GREEN}══════════════════════════════════════{RESET}")
    print(f"{GREEN}  CẤU HÌNH HOÀN TẤT!{RESET}")
    print(f"{GREEN}  Fanpage: {page_name}{RESET}")
    print(f"{GREEN}  Đặt DRY_RUN=false trong .env để đăng bài thật.{RESET}")
    print(f"{GREEN}══════════════════════════════════════{RESET}")

if __name__ == "__main__":
    main()
