from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import uuid
from datetime import date
from contextlib import closing
import time

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
        self.session.set_keyspace(self.keyspace)
        self.create_tables()
        print(f"Keyspace {self.keyspace} created or already exists")

    def create_tables(self):
        session = self.get_session()
        
        # Create users table
        user_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id text PRIMARY KEY,
            username text,
            email text,
            hashed_password text,
            is_active boolean
        );
        """
        session.execute(user_table_query)

        # Create index on username for faster lookups
        username_index_query = """
        CREATE INDEX IF NOT EXISTS users_username_idx ON users (username);
        """
        session.execute(username_index_query)

        # Create index on email
        email_index_query = """
        CREATE INDEX IF NOT EXISTS users_email_idx ON users (email);
        """
        session.execute(email_index_query)
        
        # Create projects table
        project_table_query = """
        CREATE TABLE IF NOT EXISTS projects (
            p_id text PRIMARY KEY,
            p_name text,
            p_head text
        );
        """
        session.execute(project_table_query)

        # Create index on project name for faster lookups
        project_name_index_query = """
        CREATE INDEX IF NOT EXISTS projects_p_name_idx ON projects (p_name);
        """
        session.execute(project_name_index_query)

        print("Tables created")

    def get_session(self):
        if self.session is None:
            print("WARNING: Session is None, attempting to reconnect...")
            max_retries = 5
            retry_delay = 10
            
            for attempt in range(max_retries):
                try:
                    print(f"Reconnection attempt {attempt + 1}/{max_retries}")
                    self.connect()
                    if self.session is not None:
                        print("Successfully reconnected to Cassandra")
                        return self.session
                except Exception as e:
                    print(f"Reconnection attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        print(f"Waiting {retry_delay} seconds before next attempt...")
                        time.sleep(retry_delay)
                    else:
                        print("All reconnection attempts failed")
                        raise RuntimeError(f"Failed to reconnect to Cassandra after {max_retries} attempts")
            
            raise RuntimeError(f"Failed to obtain Cassandra session after {max_retries} attempts")
        
        return self.session