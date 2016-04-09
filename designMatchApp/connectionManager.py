import os

import boto
from boto.dynamodb.table import Table


class ConnectionManager:

    def __init__(self):
        self.db = None
        self.proyectosTable = None

        self.db = boto.dynamodb.connect_to_region(
            os.environ.get('REGION'),
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

    def setupProyectosTable(self):
        try:
            self.proyectosTable = Table("Proyectos", connection=self.db)
        except Exception as e:
            raise e("Hubo un problema con la tabla Proyectos.")

    def getProyectosTable(self):
        if self.proyectosTable == None:
            self.setupProyectosTable()
        return self.proyectosTable