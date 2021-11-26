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
