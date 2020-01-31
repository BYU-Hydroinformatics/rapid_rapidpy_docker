from boto3.session import Session
import boto3
import os

ACCESS_KEY =  # OBTAIN FROM AWS
SECRET_KEY =  # OBTAIN FROM AWS
BUCKET_NAME = 'byu-rapid-input-files'
remoteDirectoryName = os.environ['REGION']

session = Session(aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

s3 = session.resource('s3')

s3_resource = boto3.resource('s3')
your_bucket = s3.Bucket(BUCKET_NAME)


output_location = os.path.join('/home/rapid-io/input', remoteDirectoryName)
if os.path.exists(output_location):
    print("Input files already exist. No need to redownload. You may delete the dir and force a refresh")
else:
    for object in your_bucket.objects.filter(Prefix=remoteDirectoryName):
        if(object.key == remoteDirectoryName + '/'):
            continue

        path = os.path.join('/home/rapid-io/input', os.path.dirname(object.key))
        if not os.path.exists(path):
            os.makedirs(path)

        your_bucket.download_file(object.key, os.path.join('/home/rapid-io/input', object.key))
