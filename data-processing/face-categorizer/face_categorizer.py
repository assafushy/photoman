import os
import pathlib
import json
import logging
from minio import Minio
import uuid

from PIL import Image
import face_recognition
from datetime import datetime


class face_categorizer:
    def __init__(self,object_name,src_bucket_name,dest_bucket_name,src_download_dir,thumbnails_dir,s3_man,db_manager):
        self.db_manager = db_manager
        self.object_name = object_name
        self.mime_type = ""
        self.src_bucket_name = src_bucket_name
        self.dest_bucket_name = dest_bucket_name
        self.src_download_dir = src_download_dir
        self.thumbnails_dir = thumbnails_dir
        self.s3_man = s3_man
        self.local_file_path=""
        self.photo_meta = {}
        self.start_face_categorizer()

    def start_face_categorizer(self):
        thumbnail = self.db_manager.fetch_thumbnail_by_object_name(self.object_name)
        thumbnail_id = thumbnail["_id"]
        persons =[]
        logging.info("download thumbnail {}".format(self.object_name))
        self.validate_photo_mime_type() #Validate mimie type on thumbnail
        local_src_path = self.s3_man.download_object(self.src_bucket_name,self.object_name,self.thumbnails_dir) #Download thumbnail
        logging.info("laoding thumbnail {} to recognition".format(self.object_name))
        todo_thumbnail = face_recognition.load_image_file(str(local_src_path))
        todo_thumbnail_encoding = face_recognition.face_encodings(todo_thumbnail)[0]
        logging.info("starting face categorizetion")
        persons = self.db_manager.fetch_all_persons()   #Fetch all persons from db
        for person in persons:                          #Iterate persons for compare purposes
            logging.info("checking thumbnail with person: {} ".format(person["_id"]))
            for compare_thumbnail_id in person["thumbnails"]:      #Download persons thumbnails
                logging.info("downloading thumbnail: {} for person: {}".format(compare_thumbnail_id,person["_id"]))
                focused_thumbnail = self.db_manager.fetch_thumbnail_by_id(compare_thumbnail_id)
                compare_thumbnail_path = self.s3_man.download_object("thumbnails",focused_thumbnail["thumbnail_object"],self.thumbnails_dir)
                compared_thumbnail = face_recognition.load_image_file(compare_thumbnail_path) #Encode new thumbnail
                compared_thumbnail_encoding = face_recognition.face_encodings(compared_thumbnail)[0]
                results = face_recognition.compare_faces([todo_thumbnail_encoding], compared_thumbnail_encoding) #compare with original
                if results[0] == True:
                    logging.info("Found a match between - {} - {}".format(thumbnail_id,compared_thumbnail))
                    self.db_manager.link_thumbnail_to_person(thumbnail_id,person["_id"]) #Link thumbnail to person
                    return 1
        self.db_manager.create_person(thumbnail_id) #Create new Person doc
        
        return 0

    def validate_photo_mime_type(self):
        extensions = {".jpg",".jpeg", ".png", ".gif"}
        for ext in extensions:
            if self.object_name.endswith(ext):
                logging.info("image detected, type - {}".format(ext))
                self.mime_type = ext
                return
        logging.warn("no image type detected")

    def extract_thumbnails(self):
        dir_exists = pathlib.Path(self.thumbnails_dir) # Checking and creating thumbnail dir
        if not dir_exists.exists(): 
            os.mkdir(self.thumbnails_dir)
        
        image = face_recognition.load_image_file(self.local_file_path)
        face_locations = face_recognition.face_locations(image)
        logging.info("found {} people in the photo".format(len(face_locations)))
        
        for face_location in face_locations:
            logging.info("Cropping thumbnail #")
            img = Image.open(self.local_file_path)
            area = (face_location[3],face_location[0],face_location[1],face_location[2])
            cropped_img = img.crop(area)
            cropped_img.save(self.thumbnails_dir + "/" +str(uuid.uuid4())+self.mime_type)

    def upload_thumbnails(self):
        client = Minio(self.minio_url,secure=False) # Create client with anonymous access.
        file_list = os.listdir(self.thumbnails_dir) # get files list
        logging.info("Uploading {} thumbnails".format(len(file_list)))
        for file in file_list:
            try:
                file_path = self.thumbnails_dir+"/"+file
                client.fput_object(bucket_name=self.dest_bucket_name,file_path=file_path,object_name=file)
            except Exception as e:
                logging.error(e)
                logging.error("error downloading photo : {} to bucket {}".format(["image",self.dest_bucket_name]))

            thumbnail_id = self.register_thumbnail_to_db(file,self.photo_meta)
            self.db_manager.link_thumbnail_to_photo(thumbnail_id,self.photo_meta["_id"])

    def register_photo_to_db(self):
        logging.info("Registering photo to db")
        photo_object = str(uuid.uuid4())+self.mime_type
        on_boarding_time = str(datetime.utcnow())
        self.photo_meta={"photo_object":photo_object,"objects":[],"on_boarding_time":on_boarding_time}
        logging.info(json.dumps(self.photo_meta))
        photo_id = self.db_manager.register_photo(self.photo_meta)
        self.photo_meta["_id"] = photo_id
    
    def register_thumbnail_to_db(self,object_name,parent_photo_meta):
        logging.info("Registering thumbnail to db")
        on_boarding_time = str(datetime.utcnow())
        thumbnail_meta={"thumbnail_object":object_name,"on_boarding_time":on_boarding_time,"parent_id":parent_photo_meta["_id"]}
        logging.info(json.dumps(thumbnail_meta))
        return self.db_manager.register_thumbnail(thumbnail_meta,self.photo_meta)
    
    def promote_photo_bucket(self):
        logging.info('Promoting photo {}'.format(self.object_name))   
        client = Minio(self.minio_url,None,secure=False)   # Create client with anonymous access.
        try:
            client.fput_object(bucket_name="photos",file_path="./target.jpeg",object_name=str(self.photo_meta["_id"]))
            logging.info("Promotion suceeded --- deleteing photo from new files bucket")
            client.remove_object(self.src_bucket_name, self.object_name)
            logging.info("Deleted photo from new files bucket")
        except Exception as err:
            logging.error(err)
            logging.error("Error in photo Promotion")
        
