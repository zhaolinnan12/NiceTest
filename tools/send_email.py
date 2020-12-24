import yagmail
from loguru import logger


def send_email(setting):
    """
    :user: 发件人邮箱
    :password: 邮箱授权码
    :host: 发件人使用的邮箱服务 例如：smtp.163.com
    :contents: 内容
    :addressees: 收件人列表
    :title: 邮件标题
    :enclosures: 附件列表
    :return:
    """
    yag = yagmail.SMTP(setting['user'], setting['password'], setting['host'])
    # 发送邮件
    yag.send(setting['addressees'], setting['title'], setting['contents'], setting['enclosures'])
    # 关闭服务
    yag.close()
    logger.info("邮件发送成功！")