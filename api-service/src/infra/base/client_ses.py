import logging
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from fastapi.templating import Jinja2Templates
from ...helpers.mappers import FileManagerMappers, StatusCode

templates = Jinja2Templates(directory="src")

class ClientSes():
  def __init__(self, config):
    self.__host_platform = config.APP_PLATFORM_HOST
    self.__source_mail = config.MAIL_FROM
    self.__ses_client = boto3.client(
      'ses',
      aws_access_key_id=config.AWS_ACCESS_KEY_ID,
      aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
      region_name=config.AWS_REGION
    )

  async def send_template_email(self, request, to_email, subject, template_name, code= None, path: str = ''):
    try:
      html_content = templates.TemplateResponse(
        f"{FileManagerMappers.TEMPLATE_EMAIL_FOLDER}/{template_name}.html",
        { "request": request, 'host_platform': self.__host_platform, "code": code, "path": path }
      ).body.decode("utf-8")

      response = self.__ses_client.send_email(
        Source=self.__source_mail,
        Destination={
          'ToAddresses': [to_email],
        },
        Message={
          'Subject': {'Data': subject},
          'Body': {'Html': {'Data': html_content}},
        },
      )

      metadata = response.get('ResponseMetadata')
      if metadata.get('HTTPStatusCode') != StatusCode.HTTP_OK:
        logging.error(response)
        return None

      return {
        'message_id': response.get('MessageId'),
        'meta_data': metadata,
        'retry_attemps': response.get('RetryAttempts')
      }

    except NoCredentialsError as e:
      logging.error(e)
      return None
    except BotoCoreError as e:
      logging.error(e)
      return None
    except Exception as e:
      logging.error(e)
      return None
