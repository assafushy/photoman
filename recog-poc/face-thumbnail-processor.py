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
      opts, args = getopt.getopt(argv[1:],"e:o:m:h:",["amqp-event=","output-dir=","minio-url=","--help="])
   except getopt.GetoptError:
      print('test.py -i <inputfile> -o <outputfile>')
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
   logging.basicConfig(level=logging.INFO)
   logging.info ('Ampq event  is {} '.format(amqpEvent))
   logging.info ('OutPut dir is  {} '.format(outputDir))
   logging.info ('Minio url is  {} '.format(minioUrl))

   #parsing image url for download
   #jsonEvent= json.loads(amqpEvent)
   jsonEvent = {"EventName":"s3:ObjectCreated:Put","Key":"new-files/target.jpg","Records":[{"eventVersion":"2.0","eventSource":"minio:s3","awsRegion":"","eventTime":"2022-02-13T19:30:42.500Z","eventName":"s3:ObjectCreated:Put","userIdentity":{"principalId":"admin"},"requestParameters":{"principalId":"admin","region":"","sourceIPAddress":"10.42.2.39"},"responseElements":{"content-length":"0","x-amz-request-id":"16D36F47A44E4AA4","x-minio-deployment-id":"280668f5-b954-4764-b8ea-242228891bdd","x-minio-origin-endpoint":"http://10.42.2.39:9000"},"s3":{"s3SchemaVersion":"1.0","configurationId":"Config","bucket":{"name":"new-files","ownerIdentity":{"principalId":"admin"},"arn":"arn:aws:s3:::new-files"},"object":{"key":"target.jpg","size":640757,"eTag":"ce723304aa2c464398251be57346d480","contentType":"image/jpeg","userMetadata":{"content-type":"image/jpeg"},"sequencer":"16D36F47A9A8E798"}},"source":{"host":"10.42.2.39","port":"","userAgent":"MinIO (linux; amd64) minio-go/v7.0.21"}}]}
   pathArray = str(jsonEvent["Key"]).split("/")
   bucketName = pathArray[0]
   objectName=pathArray[1]
   #downloading image file
   filePath = downloadImageFile(bucketName,objectName,minioUrl,outputDir)
   #extracting face thumbnails
   extractThumbnails(filePath,"./thumbnails")
   #uploading thumbnails
   
def downloadImageFile(imageBucket,imageFile,minioUrl,destPath="."):
   logging.info('Downloading image {}'.format(imageBucket))   
   client = Minio(minioUrl,None,None,None,False)   # Create client with anonymous access.
   localFilePath = destPath+"/"+imageFile
   try:
      client.fget_object(imageBucket, imageFile,localFilePath)
      return localFilePath
   except:
      logging.error("erron downloading photo : {} from bucket {}".format([imageFile,imageBucket]))

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

def uploadThumbnails(destBucket,minioUrl):
   logging.info("uploading thumbnails")
   client = Minio(minioUrl,None,None,None,False)   # Create client with anonymous access.
  #get files list
   #for each file upload
   try:
      client.fput_object(destBucket)
   except:
      logging.error("erron downloading photo : {} to bucket {}".format(["image",destBucket]))

if __name__ == '__main__':
   main(sys.argv)
