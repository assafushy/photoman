import uuid
from PIL import Image
import face_recognition

image = face_recognition.load_image_file("target.jpg")
face_locations = face_recognition.face_locations(image)

# crop thumbnails
for face_location in face_locations:
  img = Image.open("target.jpg")
  area = (face_location[3],face_location[0],face_location[1],face_location[2])
  cropped_img = img.crop(area)
  cropped_img.save(str(uuid.uuid4())+".jpg")