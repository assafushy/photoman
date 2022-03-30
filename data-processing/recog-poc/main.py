import sys, getopt
import json
import logging

from dbManager import db_manager
from photo_extraction import photo_extraction

def main(argv):
   amqp_event = ''
   output_dir = ''
   minio_url=''
   mongodb_host=''
   mongodb_port=''
   mongodb_user=''
   mongodb_password=''

   try:
      opts, args = getopt.getopt(argv[1:],"e:o:m:h:d:i:u:p:",["amqp-event=","output-dir=","minio-url=","db-host=","--db-port=","user-name=","password=","--help="])
   except getopt.GetoptError:
      print('face-thumbnail-processor.py -e <amqp-file-event> -o <outputfile> -m <minio-url> -d <mongodb-url> -u <db-username> -p <db-password>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h","--help"):
         print('test.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-e", "--amqp-event"):
         amqp_event = arg
      elif opt in ("-o", "--output-dir"):
         output_dir = arg
      elif opt in ("-m", "--minio-url"):
         minio_url = arg
      elif opt in ("-d", "--db-host"):
         mongodb_host = arg
      elif opt in ("-i", "--db-port"):
         mongodb_port = arg
      elif opt in ("-u", "--user-name"):
         mongodb_user = arg
      elif opt in ("-p", "--password"):
         mongodb_password = arg

   logging.basicConfig(level=logging.INFO)
   
   logging.info ('OutPut dir is  {} '.format(output_dir))
   logging.info ('Minio url is  {} '.format(minio_url))
   json_event= json.loads(amqp_event) # parsing photo path from event
   logging.info ('Ampq event object key is: {} '.format(json_event["Key"]))
   path_array = str(json_event["Key"]).split("/") # parsing bucket name and object name
   bucket_name = path_array[0]
   object_name=path_array[1]
   src_download_dir = "./"
   thumbnails_dir = "./thumbnails"
   dest_bucket_name = "thumbnails-todo"

   db_man = db_manager(mongodb_host,mongodb_port,mongodb_user,mongodb_password)     
   photo_extraction(object_name,bucket_name,dest_bucket_name,src_download_dir,thumbnails_dir,minio_url,db_man)
   
if __name__ == '__main__':
   main(sys.argv)
