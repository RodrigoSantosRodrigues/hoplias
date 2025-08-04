from nameko.extensions import DependencyProvider
from pymongo import MongoClient


class MongoDB(DependencyProvider):
    def __init__(self):
        self.client = None

    def setup(self):
        config = self.container.config
        self.uri = config['MONGO_URI']
        self.db_name = config['MONGO_DB_NAME']
        self.client = MongoClient(self.uri)

    def stop(self):
        if self.client:
            self.client.close()

    def get_dependency(self, worker_ctx):
        return self.client[self.db_name]
