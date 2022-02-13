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
      opts, args = getopt.getopt(argv,"ae:o:m:h:",["amqp-event=","output-dir=","minio-url=","--help="])
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
         minioUrl = args
   logging.basicConfig(level=logging.INFO)
   logging.info ('Ampq event  is {} '.format(amqpEvent))
   logging.info ('OutPut dir is  {} '.format(outputDir))
   logging.info ('Minio url is  {} '.format(minioUrl))

   #parsing image url for download
   imageUrl = ""
   #downloading image file
   filePath = downloadImageFile("new-files","team.png","./srcPhoto")
   #extracting face thumbnails
   extractThumbnails(filePath,"./thumbnails")
   #uploading thumbnails
   
def downloadImageFile(imageBucket,imageFile,destPath="."):
   logging.info('Downloading image {}'.format(imageBucket))   
   client = Minio("localhost:30010",None,None,None,False)   # Create client with anonymous access.
   localFilePath = destPath+"/"+imageFile
   try:
      client.fget_object(imageBucket, imageFile,localFilePath)
      return localFilePath
   except:
      logging.error("erron downloading photo : {} from bucket {}".format([imageFile,imageBucket]))

def extractThumbnails(srcPhoto,thumbnailDestFolder):
   image = face_recognition.load_image_file(srcPhoto)
   face_locations = face_recognition.face_locations(image)

   # crop thumbnails
   for face_location in face_locations:
      img = Image.open(srcPhoto)
      area = (face_location[3],face_location[0],face_location[1],face_location[2])
      cropped_img = img.crop(area)
      cropped_img.save(thumbnailDestFolder + "/" +str(uuid.uuid4())+".png")

if __name__ == '__main__':
   main(sys.argv)
