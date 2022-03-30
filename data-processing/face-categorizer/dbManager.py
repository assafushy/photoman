import pymongo
import logging

class db_manager:
    def __init__(self,db_hostname,db_port,db_user,db_password):
        connection_str = 'mongodb://'+db_user+':'+db_password+'@'+db_hostname+':'+str(db_port)+'/'
        self.client = pymongo.MongoClient(connection_str,authSource="admin")
        self.photos_db = self.client.get_database("photos")
    
    def fetch_all_persons(self):
        logging.info("Fetching all persons documnets from db")
        persons = self.photos_db.get_collection("persons").find()
        return persons

    # -----OLD------
    # def register_photo(self,photo_meta):
    #     photos_collection = self.photos_db.get_collection("photos")
    #     res = photos_collection.insert_one(photo_meta)
    #     return res.inserted_id
    
    # def register_thumbnail(self,thumbnail_meta,photo_meta):
    #     photos_collection = self.photos_db.get_collection("thumbnails")
    #     res = photos_collection.insert_one(thumbnail_meta)
    #     return res.inserted_id
    
    # def link_thumbnail_to_photo(self,thumbnail_id,photo_id):
    #     photos_collection = self.photos_db.get_collection("photos")
    #     record_filter = { '_id': photo_id }
    #     newvalues = { "$push": { 'thumbnails': thumbnail_id } }
    #     photos_collection.update_one(record_filter, newvalues)      