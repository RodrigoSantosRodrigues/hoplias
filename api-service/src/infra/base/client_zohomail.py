import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from ...helpers.mappers import FileManagerMappers, StatusCode

env = Environment(loader=FileSystemLoader("src"))

class ClientZoho():
    def __init__(self, config):
        self.__host_platform = config.APP_PLATFORM_HOST
        self.__source_mail = config.MAIL_FROM
        self.__smtp_server = "smtp.zoho.com"
        self.__smtp_port = 465
        self.__smtp_user = config.MAIL_USERNAME
        self.__smtp_password = config.MAIL_PASSWORD

    async def send_template_email(self, to_email, subject, template_name, code=None, path: str = ''):
        try:
            template = env.get_template(f"{FileManagerMappers.TEMPLATE_EMAIL_FOLDER}/{template_name}.html")
            html_content = template.render(
                host_platform=self.__host_platform,
                code=code,
                path=path
            )

            message = MIMEMultipart()
            message["From"] = self.__source_mail
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(html_content, "html"))

            # Enviar e-mail via Zoho SMTP
            smtp = aiosmtplib.SMTP(hostname=self.__smtp_server, port=self.__smtp_port, use_tls=True)
            await smtp.connect()
            await smtp.login(self.__smtp_user, self.__smtp_password)
            await smtp.send_message(message)
            await smtp.quit()

            return {
                'message_id': subject,
                'meta_data': {"status": "sent"},
                'retry_attempts': 0
            }

        except Exception as e:
            logging.error(f"Error in send mail: {e}")
            return None