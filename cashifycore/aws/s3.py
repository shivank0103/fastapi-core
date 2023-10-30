import boto3
from app.config import settings


class CashifyS3:
    """
    Cashify S3 class to handle all S3 functionalities.
    """

    @staticmethod
    def save(path: str, body, bucket_name: str, is_private: bool = False, extra_args: dict = {}):
        """
        method to save the data to s3 bucket using
        provided path and bucket name
        """
        try:
            s3 = boto3.resource('s3')
            if is_private:
                if extra_args:
                    return s3.Bucket(bucket_name).put_object(Key=path, Body=body, ExtraArgs=extra_args)
                return s3.Bucket(bucket_name).put_object(Key=path, Body=body)
            else:
                if extra_args:
                    return s3.Bucket(bucket_name).put_object(Key=path, Body=body, ACL="public-read",
                                                             ExtraArgs=extra_args)
                return s3.Bucket(bucket_name).put_object(Key=path, Body=body, ACL="public-read")
        except Exception as e:
            boto3_session = boto3.session.Session(
                aws_access_key_id=settings.STAGE_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.STAGE_AWS_SECRET_ACCESS_KEY
            )
            s3 = boto3_session.resource('s3')
            if is_private:
                if extra_args:
                    return s3.Bucket(bucket_name).put_object(Key=path, Body=body, ExtraArgs=extra_args)
                return s3.Bucket(bucket_name).put_object(Key=path, Body=body)
            else:
                if extra_args:
                    return s3.Bucket(bucket_name).put_object(Key=path, Body=body, ACL="public-read",
                                                             ExtraArgs=extra_args)
                return s3.Bucket(bucket_name).put_object(Key=path, Body=body, ACL="public-read")

    @staticmethod
    def get_presigned_url(bucket_name: str, key: str, expires_in: int = 60):
        try:
            s3 = boto3.resource('s3')
            return s3.meta.client.generate_presigned_url(
                'get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=expires_in
            )
        except Exception as e:
            boto3_session = boto3.session.Session(
                aws_access_key_id=settings.STAGE_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.STAGE_AWS_SECRET_ACCESS_KEY
            )
            s3 = boto3_session.resource('s3')
            return s3.meta.client.generate_presigned_url(
                'get_object', Params={'Bucket': bucket_name, 'Key': key}, ExpiresIn=expires_in
            )
