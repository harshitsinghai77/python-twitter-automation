import sqlite3

class Database:

    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        try:
            self.connection = sqlite3.connect('twitter_tweets.db')
            self.cursor = self.connection.cursor()
            return self.cursor

        except sqlite3.Error as e:
            print("Error connecting to database!")

    def __exit__(self, execption_type, execption_value, execption_traceback):
        if execption_value is not None:
            self.connection.rollback()
        else:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()