import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

def send_main(mail_text, mail_subject="Auto Send Mail", mailto_list='m18621127127@163.com'):
    mailto_list = [mailto_list]
    mail_host = os.getenv('MAIL_HOST')
    mail_user = os.getenv('MAIL_USER')
    # 这里首先在邮箱-设置里开启 SMTP 服务，其次获得授权码，以授权码作为密码输入
    mail_pass = os.getenv('MAIL_PASSWORD')

    # 后续写入consts.py中
    msg = MIMEMultipart()
    msg["From"] = mail_user   # 发件人
    msg["To"] = ";".join(mailto_list)  # 收件人
    msg["Subject"] = mail_subject   # 邮件标题
    # 邮件正文
    txt = MIMEText(mail_text, 'html', 'utf-8')
    msg.attach(txt)

    # 附件名称非中文时的写法
    # att["Content-Disposition"] = 'attachment; filename="test.html")'

    smtp = smtplib.SMTP()
    smtp.connect(mail_host)
    smtp.login(mail_user, mail_pass)
    smtp.sendmail(mail_user, mailto_list, msg.as_string())
    smtp.quit()
    print("邮件发送成功")


if __name__ == '__main__':
    send_main('python auto test', 'm18621127127@163.com')
