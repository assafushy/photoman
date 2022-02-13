import sys, getopt
import uuid
from PIL import Image
import face_recognition
import logging
from minio import Minio

def main(argv):
   amqpEvent = ''
   outputDir = ''
   minioUrl=''
   try:
      opts, args = getopt.getopt(argv,"ae:o:m:",["amqp-event=","output-dir=","minio-url="])
   except getopt.GetoptError:
      print('test.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('test.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-ae", "--amqp-event"):
         amqpEvent = arg
      elif opt in ("-o", "--output-dir"):
         outputDir = arg
      elif opt in ("-m", "--minio-url"):
         minioUrl = arg
   logging.info ('Ampq event  is {} '.format(amqpEvent))
   logging.info ('OutPut dir is  {} '.format(outputDir))
   logging.info ('Minio url is  {} '.format(minioUrl))

   #parsing image url for download
   imageUrl = ""
   #extracting face thumbnails
   downloadImageFile(imageUrl)
   #uploading thumbnails
   
def downloadImageFile(imageBucket,imageFile,destPath="./"):
   logging.info('Downloading image {}'.format(imageBucket))   
   client = Minio("play.min.io")   # Create client with anonymous access.
   try:
      response = client.get_object("my-bucket", "my-object")
      # Read data from response.
   finally:
      response.close()
      response.release_conn()


def createThumbnails():
   image = face_recognition.load_image_file("target.jpg")
   face_locations = face_recognition.face_locations(image)

   # crop thumbnails
   for face_location in face_locations:
      img = Image.open("target.jpg")
      area = (face_location[3],face_location[0],face_location[1],face_location[2])
      cropped_img = img.crop(area)
      cropped_img.save(str(uuid.uuid4())+".jpg")

   def downloadImageFile(imageFile,MinioUrl):
      logging.info('Downloading image {}'.format(imageFile))