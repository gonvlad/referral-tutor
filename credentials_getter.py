import os
import psycopg2


DB_URI = os.environ['DB_URI']


class CredentialsGetter:
    def __init__(self):
        self.connection = psycopg2.connect(DB_URI, sslmode="require")
        self.cursor = self.connection.cursor()
        
    def __del__(self):
        self.cursor.close()
        self.connection.close()
        
    def get_credentials(self):
        try:
            status_id = 2
            self.cursor.execute(f"SELECT * FROM okcoin_account WHERE status_id = 2")
            result = self.cursor.fetchone()
            
            if result:
                print(">" * 100)
                for row in result:
                    id = row["id"]
                    login = row["email"]
                    password = row["pswd"]
                credentials = (id, login, password)
            else:
                credentials = ()  
        except Exception as e:
            print(e) 
            credentials = ()
                 
        return credentials
    
    def update_credentials(self, id):
        self.cursor.execute("UPDATE okcoin_account SET status_id = 3 WHERE id = " + id)
        return self.connection.commit()
        