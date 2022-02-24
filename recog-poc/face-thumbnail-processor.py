import sys, getopt
import uuid
from PIL import Image
import face_recognition
import logging
from minio import Minio
import json
import os

def main(argv):
   amqpEvent = ''
   outputDir = ''
   minioUrl=''
   try:
      opts, args = getopt.getopt(argv[1:],"e:o:m:h:a:s:",["amqp-event=","output-dir=","minio-url=","--access-key=","--secret-key=","--help="])
   except getopt.GetoptError:
      print('face-thumbnail-processor.py -e <amqp-file-event> -o <outputfile> -m<minio-url>')
      sys.exit(2)
   for opt, arg in opts:
      if opt in ("-h","--help"):
         print('test.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-e", "--amqp-event"):
         amqpEvent = arg
      elif opt in ("-o", "--output-dir"):
         outputDir = arg
      elif opt in ("-m", "--minio-url"):
         minioUrl = arg
      elif opt in ("-a", "--access-key"):
         accessKey = arg
      elif opt in ("-s", "--secret-key"):
         secretKey = arg
   logging.basicConfig(level=logging.INFO)
   logging.info ('Ampq event  is {} '.format(amqpEvent))
   logging.info ('OutPut dir is  {} '.format(outputDir))
   logging.info ('Minio url is  {} '.format(minioUrl))

   #parsing image url for download
   jsonEvent= json.loads(amqpEvent)
   pathArray = str(jsonEvent["Key"]).split("/")
   bucketName = pathArray[0]
   objectName=pathArray[1]
   thumbnailsDir = "./thumbnails"
   #downloading image file
   filePath = downloadImageFile(bucketName,objectName,minioUrl,accessKey,secretKey,outputDir)
   #extracting face thumbnails
   extractThumbnails(filePath,thumbnailsDir)
   #uploading thumbnails
   uploadThumbnails(thumbnailsDir,"thumbnails",minioUrl,accessKey,secretKey)
   
def downloadImageFile(imageBucket,imageFile,minioUrl,accessKey,secretKey,destPath="."):
   logging.info('Downloading image {}'.format(imageFile))   
   client = Minio(minioUrl,None,secure=False)   # Create client with anonymous access.
   localFilePath = destPath+"/"+imageFile
   try:
      client.fget_object(imageBucket, imageFile,localFilePath)
      return localFilePath
   except Exception as err:
      logging.error(err)
      logging.error("error downloading photo :" +imageFile +  " from bucket "+imageBucket)

def extractThumbnails(srcPhoto,thumbnailDestFolder):
   image = face_recognition.load_image_file(srcPhoto)
   face_locations = face_recognition.face_locations(image)
   os.mkdir(thumbnailDestFolder)
   # crop thumbnails
   for face_location in face_locations:
      img = Image.open(srcPhoto)
      area = (face_location[3],face_location[0],face_location[1],face_location[2])
      cropped_img = img.crop(area)
      cropped_img.save(thumbnailDestFolder + "/" +str(uuid.uuid4())+".jpg")

def uploadThumbnails(thumbnailsDir,destBucket,minioUrl,accessKey,secretKey):
   logging.info("uploading thumbnails")
   client = Minio(minioUrl,secure=False)   # Create client with anonymous access.
   #get files list
   fileList = os.listdir(thumbnailsDir)
   #for each file upload
   for file in fileList:
      try:
         filePath = thumbnailsDir+"/"+file
         client.fput_object(bucket_name=destBucket,file_path=filePath,object_name=file)
      except Exception as e:
         logging.error(e)
         logging.error("erron downloading photo : {} to bucket {}".format(["image",destBucket]))

if __name__ == '__main__':
   main(sys.argv)
