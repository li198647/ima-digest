# -*- coding: utf-8 -*-
"""通过木木自己的 QQ 邮箱 SMTP 发送 HTML 邮件（复用 mail.py 的连接逻辑）。
用法: python send_html.py <收件人> <主题> <html文件路径>
"""
import sys
import os
from email.mime.text import MIMEText

sys.path.insert(0, r"E:\workbuddywork\2026-10-23-14-33-47\交接给113")
import mail


def main():
    to, subject, html_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    cfg = mail.load_conf()
    s = mail.smtp_login(cfg)
    msg = MIMEText(html, "html", "utf-8")
    msg["From"] = cfg["account"]
    msg["To"] = to
    msg["Subject"] = subject
    try:
        s.sendmail(cfg["account"], [to], msg.as_string())
        print("已发送 -> %s（主题：%s，HTML %d 字符）" % (to, subject, len(html)))
    finally:
        try:
            s.quit()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
