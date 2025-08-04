import logging
import boto3
from botocore.session import get_session
from botocore.exceptions import ClientError
import base64
from dotenv import load_dotenv
import os

load_dotenv()

class ClientS3:
    def __init__(self):
        self.__s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION")
        )

    def upload_image(self, image_data, bucket, file_name):
        """Upload an image to an S3 bucket."""
        try:
            # Decode the base64 image data
            image_bytes = base64.b64decode(image_data)
            # Upload the image to S3
            self.__s3_client.put_object(Bucket=bucket, Key=file_name, Body=image_bytes, ContentType='image/png')
        except ClientError as e:
            logging.error(f"Error uploading image {file_name}: {e}.")
            return False
        return True

    def remove_file(self, bucket, file_name):
        """Remove a file from an S3 bucket."""
        try:
            self.__s3_client.delete_object(Bucket=bucket, Key=file_name)
        except ClientError as e:
            logging.error(f"Error removing file {file_name}: {e}.")
            return False
        return True

    def load_image(self, file_name, bucket):
        """Load an image from an S3 bucket and return it in base64."""
        try:
            response = self.__s3_client.get_object(Bucket=bucket, Key=file_name)
            image_data = response['Body'].read()
            
            # Detect MIME type dynamically
            content_type = response.get('ContentType', 'image/png')  # Default to PNG
            
            # Encode the image data to base64
            binary = base64.b64encode(image_data).decode('utf-8')

            if "dataimage/jpegbase64" in binary:
                binary = binary.replace("dataimage/jpegbase64", "")
            
            # Return with correct MIME type
            return f"data:{content_type};base64,{binary}"
        except ClientError as e:
            logging.error(f"Error loading image {file_name}: {e}.")
            return None
