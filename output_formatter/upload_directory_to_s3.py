import mimetypes
import os

try:
    import boto3
    from botocore.exceptions import NoCredentialsError
except ImportError:
    boto3 = None
    NoCredentialsError = None

def upload_directory_to_s3(config_aws_s3_bucket_details, config_publishing_details_local_publish_path):
    bucket_name = config_aws_s3_bucket_details["bucket_name"]
    s3_directory = config_aws_s3_bucket_details["s3_directory"]
    aws_access_key_id = config_aws_s3_bucket_details["aws_access_key_id"]
    aws_secret_access_key = config_aws_s3_bucket_details["aws_secret_access_key"]
    region_name = config_aws_s3_bucket_details["region_name"]
    local_directory = config_publishing_details_local_publish_path

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    s3 = session.resource('s3')

    num_files = 0

    for root, dirs, files in os.walk(local_directory):
        for filename in files:
            local_path = os.path.join(root, filename)
            relative_path = os.path.relpath(local_path, local_directory)
            s3_path = os.path.join(s3_directory, relative_path).replace(os.sep, '/')

            content_type, _ = mimetypes.guess_type(local_path)
            if not content_type:
                content_type = 'binary/octet-stream'

            print(f"Uploading {local_path} to {bucket_name}/{s3_path} with Content-Type {content_type}")
            try:
                num_files += 1
                s3.Bucket(bucket_name).upload_file(
                    local_path,
                    s3_path,
                    ExtraArgs={'ContentType': content_type}
                )

            except NoCredentialsError:
                print("Credentials not available")
                return "    Failed on file: " + local_path
    return f"    {num_files} files uploaded successfully."
