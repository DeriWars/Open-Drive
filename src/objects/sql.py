from sqlite3 import *

class UserDatabase():
    """
    The users database.
    Store the name, email and password of the user.
    """
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        """
        Create the users' table.
        """
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                            name TEXT,
                            email TEXT,
                            password TEXT)""")
        self.conn.commit()
        print("User table created!")
    
    def add_user(self, username: str, email: str, password: str):
        """
        Add a user to the database.

        Args:
            username (str): the user's name
            email (str): the user's email
            password (str): the user's encrypted password
        """
        
        self.cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (username, email, password))
        self.conn.commit()
    
    def get_user(self, username: str, email: str=None) -> dict:
        """
        Search for a user in the database by name or by email.

        Args:
            username (str): the user's name
            email (str, optional): the user's email. Defaults to None.

        Returns:
            dict: the user's information or None if not found.
        """
        
        if email is None: self.cursor.execute("SELECT * FROM users WHERE name=? OR email=?", (username,username,))
        else: self.cursor.execute("SELECT * FROM users WHERE name=? OR email=?", (username,email,))
        return self.cursor.fetchone()
    
    def is_valid_user(self, username: str, password: str) -> bool:
        """
        Check if the user is valid.
        
        Params:
            username (str): the user's name
            password (str): the user's encrypted password
        
        Returns:
            bool: True if the user is valid, False otherwise.
        """
        
        self.cursor.execute("SELECT * FROM users WHERE (name=? OR email=?) AND password=?", (username,username,password,))
        return self.cursor.fetchone() is not None


class FolderDatabase():
    """
    The folders database.
    Store the name, path and the user's id of the folder.
    """
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        """
        Create the folders' table.
        """
        
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS folders(
                            name TEXT,
                            id TEXT,
                            owners TEXT,
                            path TEXT,
                            parent TEXT)""")
        self.conn.commit()
    
    def generate_id(self):
        """
        Generate an id for the folder.
        """
        
        from random import choices
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(choices(characters, k=64))
    
    def add_folder(self, name: str, owners: str, base_path: str) -> str:
        """
        Add a folder to the database.

        Args:
            name (str): the folder's name
            owners (str): the folder's owner
        """
        
        identity = self.generate_id()
        
        while self.get_folder(identity) is not None:
            identity = self.generate_id()
        
        print(identity)
        
        self.cursor.execute("INSERT INTO folders VALUES (?, ?, ?, ?, ?)", (name, identity, owners, base_path + identity + "/", base_path))
        self.conn.commit()
        return identity
    
    def get_folder_by_name(self, name: str, asker: str) -> dict:
        """
        Search for a folder in the database by id.

        Args:
            id (str): the folder's id

        Returns:
            dict: the folder's information or None if not found.
        """
        
        self.cursor.execute("SELECT * FROM folders WHERE name=?", (name,))
        results = self.cursor.fetchall()
        
        for r in results:
            if asker in r[2]:
                return r
        
        return None
    
    def get_folder_by_id(self, identity: str, asker: str) -> dict:
        """
        Search for a folder in the database by id.

        Args:
            identity (str): the folder's id

        Returns:
            dict: the folder's information or None if not found.
        """
        
        self.cursor.execute("SELECT * FROM folders WHERE id=?", (identity,))
        results = self.cursor.fetchall()
        
        for r in results:
            if asker in r[2]:
                return r
        
        return None

    def get_folder(self, identity: str) -> dict:
        """
        Search for a folder in the database by id.

        Args:
            identity (str): the folder's id

        Returns:
            dict: the folder's information or None if not found.
        """

        self.cursor.execute("SELECT * FROM folders WHERE id=?", (identity,))
        return self.cursor.fetchone()

    def get_folders(self, user: str) -> list:
        """
        Search for a folder in the database by user's name.

        Args:
            user (str): the user's name

        Returns:
            list: the folder's information or None if not found.
        """
        
        self.cursor.execute("SELECT * FROM folders WHERE ? IN owners", (user,))
        results = self.cursor.fetchall()

        return results

    def get_owners(self, identity: str) -> list:
        self.cursor.execute("SELECT * FROM folders WHERE id=?", (identity,))
        return self.cursor.fetchone()['owners'].split(", ")
    
    def delete_folder(self, folder_id: str):
        """
        Delete a folder from the database.

        Args:
            folder_id (str): the folder's id
        """
        
        self.cursor.execute("DELETE FROM folders WHERE id=? OR parent LIKE ?", (folder_id,folder_id,))
