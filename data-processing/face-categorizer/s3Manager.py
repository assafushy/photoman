
import logging
from minio import Minio

class s3_manager:

    def __init__(self,s3_url,s3_user,s3_password):
        self.s3_url = s3_url
        self.client = Minio(self.s3_url,None,secure=False)   # Create client using anonymous access.

    def download_object(self,bucket_name,object_name,dest_path):
        local_file_path = dest_path+"/"+ object_name
        try:
            self.client.fget_object(bucket_name, object_name,local_file_path)
            return local_file_path
        except Exception as err:
            logging.error(err)
            logging.error("error downloading photo :" +object_name +  " from bucket "+ bucket_name)
            return None