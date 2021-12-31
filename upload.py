import boto3
import sys
from boto.s3.key import Key

AWS_ACCESS_KEY_ID = 'AKIAQM3DCGJZF6LD2REG'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET = 'webms-mp4convertedllmao'

class Uploader:
    def __init__(self):
        pass
    def upload(self, path, filename):
        session = boto3.Session(
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )
        s3 = session.resource('s3')
        x = s3.meta.client.upload_file(Filename="{}/{}".format(path, filename), Bucket=BUCKET, Key=filename)
        location = s3.meta.client.get_bucket_location(Bucket=BUCKET)['LocationConstraint']
        url = "https://s3-%s.amazonaws.com/%s/%s" % (location, BUCKET, filename)
        print("uploaded", url)
        return url
