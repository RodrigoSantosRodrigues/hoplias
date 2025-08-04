import logging
import boto3
import base64
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
import os


class ClientS3:
    def __init__(self, config):
        """
        S3.

        :param aws_access_key: AWS access key.
        :param aws_secret_key: AWS secret key.
        :param region_name: AWS region (default: us-east-1).
        """
        self.__s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION
        )

    async def upload_image(self, image_data, bucket, file_name):
        """Upload an image to an S3 bucket."""
        try:
            # Decode the base64 image data
            image_bytes = base64.b64decode(image_data)
            # Upload the image to S3
            self.__s3_client.put_object(Bucket=bucket, Key=file_name, Body=image_bytes, ContentType='image/png')
        except ClientError as e:
            logging.error(f"Error uploading image {file_name}: {e}.")
            raise e
        return True

    async def remove_file(self, bucket, file_name):
        """Remove a file from an S3 bucket."""
        try:
            self.__s3_client.delete_object(Bucket=bucket, Key=file_name)
        except ClientError as e:
            logging.error(f"Error removing file {file_name}: {e}.")
            return False
        return True

    async def load_image(self, file_name, bucket):
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
       
            return f"data:{content_type};base64,{binary}"
        except ClientError as e:
            logging.error(f"Error loading image {file_name}: {e}.")
            return None

    def load_images_bacth(self, bucket_name, s3_folder):
        """
        Downloads all images from a folder in S3 and returns a list of base64 strings.
        
        :param bucket_name: Name of the S3 bucket.
        :param s3_folder: Path to the folder in S3.
        :return: List of base64 strings representing the loaded images.
        """

        base64_list = []
        
        try:
            response = self.__s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder)
        
            if 'Contents' not in response:
                logging.error(f"Error loading image not information image.")
                return base64_list
            
            for obj in response['Contents']:
                file_key = obj['Key']
          
                if file_key.endswith('/'):
                    continue
                
                try:
                    file_object = self.__s3_client.get_object(Bucket=bucket_name, Key=file_key)
                    file_content = file_object['Body'].read()
              
                    base64_data = base64.b64encode(file_content).decode('utf-8')
                    base64_list.append(base64_data)

                except Exception as e:
                    logging.error(f"Error loading image {e}.")
                    continue
        
        except (NoCredentialsError, PartialCredentialsError) as cred_error:
            logging.error(f"Error loading image {cred_error}.")
        except Exception as e:
            logging.error(f"Error loading image  {e}.")
        
        return base64_list
