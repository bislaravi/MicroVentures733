import boto, boto3
import zipfile, os
from boto3.s3.transfer import S3Transfer


class S3Manager(object):

    def __init__(self):
        pass

    @staticmethod
    def transafer_file_to_s3(in_file_name, out_file_name):
        transfer = S3Transfer(boto3.client('s3'))
        transfer.upload_file(in_file_name, 'startups-data', out_file_name)
