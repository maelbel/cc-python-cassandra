from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import uuid
from datetime import date
from contextlib import closing

class Database:
    def __init__(self, contact_points, keyspace):
        self.contact_points = contact_points
        self.keyspace = keyspace
        self.cluster = None
        self.session = None
        self.connect()
    
    def connect(self):
        self.cluster = Cluster(self.contact_points)
        self.session = self.cluster.connect()
        self.create_keyspace()
        self.session.set_keyspace(self.keyspace)
        print("Connected to Cassandra")
    
    def close(self):
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
        print("Connection closed")

    def create_keyspace(self):
        query = f"""
        CREATE KEYSPACE IF NOT EXISTS {self.keyspace}
        WITH REPLICATION = {{ 'class' : 'SimpleStrategy', 'replication_factor' : 1 }};
        """
        if self.cluster is None:
            self.cluster = Cluster(self.contact_points)
        if self.session is None:
            self.session = self.cluster.connect()
        self.session.execute(query)
        print(f"Keyspace {self.keyspace} created or already exists")