import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
# from dotenv import load_dotenv
from jtools.decorators import retry

class Notifier:
    def __init__(self):
        # 集中管理配置
        self.configs = {
            "telegram": {
                "token": os.getenv("TG_BOT"), # 来自你的 .env
                "chat_id": os.getenv("TG_CHAT")
            },
            "discord": {
                "webhook_url": os.getenv("CONFIG_BOT_DISCORD_INFORMER")
            },
            "feishu": {
                "webhook_url": os.getenv("FEISHU_WEBHOOK_URL")
            },
            "wework": {
                "webhook_url": os.getenv("WECHAT_WEBHOOK_URL")
            },
            "email": {
                "smtp_host": os.getenv("MAIL_SMTP_HOST", "smtp.163.com"),
                "smtp_port": int(os.getenv("MAIL_SMTP_PORT", 465)),
                "user": os.getenv("MAIL_USER"),
                "password": os.getenv("MAIL_PASSWORD"),
                "default_receiver": os.getenv("MAIL_RECEIVER") # 默认发给自己
            }
        }
        
        # 代理设置
        proxy_host = os.getenv("PROXY_HOST", 'localhost')
        proxy_port = os.getenv('PROXY_PORT', '10809') 
        self.proxies = {
            'http': f'http://{proxy_host}:{proxy_port}',
            'https': f'http://{proxy_host}:{proxy_port}',
        }

    def send_message(self, content: str, platform: str = 'feishu', **kwargs):
        """
        统一发送接口
        :param content: 消息内容
        :param platform: 平台名称 ('feishu', 'telegram', 'discord', 'wework', 'email')
        :param kwargs: 额外参数 (如 subject, receiver, mentioned_list 等)
        """
        strategy = {
            'feishu': self._send_feishu_message,
            'telegram': self._send_telegram_message,
            'discord': self._send_discord_message,
            'wework': self._send_wework_message,
            'email': self._send_email_message
        }
        
        handler = strategy.get(platform.lower())
        if not handler:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return handler(content, **kwargs)

    @retry(stop_max_attempt_number=3)
    def _send_telegram_message(self, content: str, **kwargs):
        """Telegram 机器人消息提醒"""
        token = kwargs.get("token", self.configs['telegram']['token'])
        chat_id = kwargs.get("chat_id", self.configs['telegram']['chat_id'])
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": content,
            "parse_mode": kwargs.get("parse_mode", "MarkdownV2"),
        }
        resp = requests.post(url, data=data, proxies=self.proxies, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _send_wework_message(self, content: str, **kwargs) -> bool:
        """企业微信 Webhook 发送逻辑"""
        webhook_url = kwargs.get("webhook_url", self.configs['wework']['webhook_url'])
        if not webhook_url:
            print("Error: WeChat Webhook URL not found.")
            return False

        msgtype = kwargs.get("msgtype", "text")
        headers = {"content-type": "application/json"}
        
        data = {
            "msgtype": msgtype,
            msgtype: {
                "content": content,
            }
        }
        
        # 处理可选的 @ 提醒列表
        if "mentioned_list" in kwargs:
            data[msgtype]['mentioned_list'] = kwargs['mentioned_list']
        if "mentioned_mobile_list" in kwargs:
            data[msgtype]['mentioned_mobile_list'] = kwargs['mentioned_mobile_list']

        try:
            response = requests.post(webhook_url, headers=headers, json=data, timeout=10)
            print(f"WeChat Response: {response.json()}")
            return True
        except Exception as e:
            print(f"WeChat Request Failed: {e}")
            return False

    def _send_feishu_message(self, content: str, **kwargs):
        """飞书 Webhook 发送逻辑"""
        url = self.configs['feishu']['webhook_url']
        if not url:
            print("Error: Feishu Webhook URL not found.")
            return False
        payload = {"msg_type": "text", "content": {"text": content}}
        return requests.post(url, json=payload, timeout=10).json()

    def _send_discord_message(self, content: str, **kwargs):
        """Discord Webhook 发送逻辑"""
        url = self.configs['discord']['webhook_url']
        if not url:
            print("Error: Discord Webhook URL not found.")
            return False
        payload = {"content": content}
        return requests.post(url, json=payload, timeout=10)

    @retry(stop_max_attempt_number=3)
    def _send_email_message(self, content: str, **kwargs):
        """
        邮件发送逻辑 (163 SMTP 示例)
        :param kwargs: mail_subject, mailto_list (str 或 list)
        """
        conf = self.configs['email']
        mail_subject = kwargs.get("subject", "Auto Send Mail")
        
        # 处理收件人列表
        receiver = kwargs.get("receiver", conf['default_receiver'])
        mailto_list = [receiver] if isinstance(receiver, str) else receiver

        msg = MIMEMultipart()
        msg["From"] = conf['user']
        msg["To"] = ";".join(mailto_list)
        msg["Subject"] = mail_subject
        
        # 邮件正文使用 HTML 格式
        txt = MIMEText(content, 'html', 'utf-8')
        msg.attach(txt)

        try:
            # 使用 SSL 端口 465 发送
            with smtplib.SMTP_SSL(conf['smtp_host'], conf['smtp_port']) as smtp:
                smtp.login(conf['user'], conf['password'])
                smtp.sendmail(conf['user'], mailto_list, msg.as_string())
            print("邮件发送成功")
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            raise e
        

if __name__ == "__main__":
    notifier = Notifier()
    # 示例：发送邮件
    # notifier.send_message("<h1>测试</h1><p>这是一封测试邮件</p>", platform='email', subject='测试主题')
