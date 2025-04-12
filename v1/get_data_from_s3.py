import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# AWS credentials from environment variables
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_KEY = os.getenv('AWS_SECRET_KEY')
BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

def list_and_download_files(bucket_name, download_dir='downloads'):
    try:
        # Create download directory if it doesn't exist
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        # Create a session using the provided credentials
        s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

        # List objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            print(f"\nFiles in bucket {bucket_name}:")
            for obj in response['Contents']:
                file_key = obj['Key']
                file_size = obj['Size']
                print(f"- {file_key} (Size: {file_size} bytes)")
                
                # Download each file
                local_file_path = os.path.join(download_dir, file_key)
                print(f"Downloading {file_key}...")
                s3.download_file(bucket_name, file_key, local_file_path)
                print(f"Downloaded to {local_file_path}")
        else:
            print(f"No files found in bucket {bucket_name}")

    except NoCredentialsError:
        print("Credentials not available")
    except ClientError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

# Execute if this file is run directly
if __name__ == "__main__":
    if not all([ACCESS_KEY, SECRET_KEY, BUCKET_NAME]):
        print("Error: Missing required environment variables. Check your .env file.")
    else:
        list_and_download_files(BUCKET_NAME)