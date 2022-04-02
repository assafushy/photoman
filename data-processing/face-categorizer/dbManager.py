import pymongo
import logging

class db_manager:
    def __init__(self,db_hostname,db_port,db_user,db_password):
        connection_str = 'mongodb://'+db_user+':'+db_password+'@'+db_hostname+':'+str(db_port)+'/'
        self.client = pymongo.MongoClient(connection_str,authSource="admin")
        self.photos_db = self.client.get_database("photos")
    
    def fetch_thumbnail_by_object_name(self,object_name):
        logging.info("Fetching thumbnail by object name : {}".format(object_name))
        thumbnail = self.photos_db.get_collection("thumbnails").find_one({"thumbnail_object" : object_name})
        return thumbnail

    def fetch_thumbnail_by_id(self,id):
        logging.info("Fetching thumbnail by id : {}".format(id))
        thumbnail = self.photos_db.get_collection("thumbnails").find_one({"_id" : id})
        return thumbnail

    def fetch_all_persons(self):
        logging.info("Fetching all persons documnets from db")
        persons = self.photos_db.get_collection("persons").find()
        return persons

    def create_person(self,thumbnail_id):
        persons_collection = self.photos_db.get_collection("persons")
        new_person_doc = {"name":"unknown","groups":[],"thumbnails":[thumbnail_id]}
        res = persons_collection.insert_one(new_person_doc)
        return res.inserted_id
    
    def link_thumbnail_to_person(self,thumbnail_id,person_id):
        logging.info("Linking thumbnail: {} , to person id: {}".format(thumbnail_id,person_id))
        record_filter = { '_id': person_id, "thumbnails":{ "$ne" : thumbnail_id}}
        newvalues = { "$push": { 'thumbnails': thumbnail_id } }
        self.photos_db.get_collection("persons").update_one(record_filter, newvalues)
