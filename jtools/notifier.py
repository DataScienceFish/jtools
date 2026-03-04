import os
import requests
# from dotenv import load_dotenv

from jtools.decorators import retry

# 加载配置（项目文件中运行）
# load_dotenv()


class Notifier:
    def __init__(self):
        # 集中管理配置
        self.configs = {
            "telegram": {
                "token": os.getenv("TG_BOT"),
                "chat_id": os.getenv("TG_CHAT")
            },
            "discord": {
                "webhook_url": os.getenv("CONFIG_BOT_DISCORD_INFORMER")
            },
            "feishu": {
                "webhook_url": os.getenv("FEISHU_WEBHOOK_URL")
            },
            "wework": {
                "webhook_url": os.getenv("WECHAT_WEBHOOK_URL") # 建议在 .env 中添加此项
            }
        }
        proxy_host, proxy_port = os.getenv("PROXY_HOST", 'localhost'), os.getenv('PROXY_PORT', 10809) 
        self.proxies = {
            'http': f'http://{proxy_host}:{proxy_port}',
            'https': f'http://{proxy_host}:{proxy_port}',
        }

    def send_message(self, content: str, platform: str = 'feishu', **kwargs):
        """
        统一发送接口
        :param content: 消息内容
        :param platform: 平台名称 ('feishu', 'telegram', 'discord', 'wework')
        :param kwargs: 额外参数 (如 mentioned_list, token, chat_id 等)
        """
        strategy = {
            'feishu': self._send_feishu_message,
            'telegram': self._send_telegram_message,
            'discord': self._send_discord_message,
            'wework': self._send_wework_message
        }
        
        handler = strategy.get(platform.lower())
        if not handler:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return handler(content, **kwargs)

    @retry(stop_max_attempt_number=3)
    def _send_telegram_message(self, content, **kwargs):
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

    def _send_feishu_message(self, content, **kwargs):
        """飞书 Webhook 发送逻辑"""
        url = self.configs['feishu']['webhook_url']
        payload = {"msg_type": "text", "content": {"text": content}}
        return requests.post(url, json=payload).json()

    def _send_discord_message(self, content, **kwargs):
        """Discord Webhook 发送逻辑"""
        url = self.configs['discord']['webhook_url']
        payload = {"content": content}
        return requests.post(url, json=payload)
    

if __name__ == "__main__":
    # 实例化
    notifier = Notifier()
