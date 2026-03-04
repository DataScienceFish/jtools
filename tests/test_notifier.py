import sys
sys.path.append('F:/projects/jtools')

import os
from dotenv import load_dotenv
from jtools.notifier import Notifier

load_dotenv()

def test_send_message():
    print(os.getenv("TG_BOT"))
    if os.getenv("TG_BOT") is None:
        raise ValueError("No token")
    notifier = Notifier()
    notifier.send_message("项目部署成功", platform='telegram')
