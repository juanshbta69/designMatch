import os

from pymongo import MongoClient

class Connection():

    client = MongoClient('mongodb://' + os.environ.get('MONGO_USERNAME') + ':' + os.environ.get('MONGO_PASSWORD') + '@' + os.environ.get('MONGO_HOST') + ':' + os.environ.get('MONGO_PORT') + '/' + os.environ.get('MONGO_DBNAME'))

    db = client.designmatch

    def set_client(self, host, port):
        self.client = MongoClient(host, port)

    def set_database(self, database):
        self.db = self.client[database]