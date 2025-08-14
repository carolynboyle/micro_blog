import squlite3 as sq
import blog_utililties as ul

def create_database(database_name:str):
    '''This function creates a database to support the blog application. 
    parms:
        database_name: represents the database to use or create.
        
        returns:
        table structure
        2025-AUG-06'''
    
    conn=None #if connection exists, close it   
    try:
        with sq.connect(database=database_name) as conn:
            print(f"Connected to database {database_name}")
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blog_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("Table 'blog_posts' created successfully.")

            #users table
            sql_qry = ''' 
                CREATE TABLE IF NOT EXISTS users (
                    userId INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );'''
            
            cursor.execute(sql_qry)
            print("Table 'users' created successfully.")    
            print(f"{sql_qry} executed successfully.")
            print(f"************")
            # Commit the changes
            conn.commit()
             #create blog_post table
        sql_qry =''' CREATE TABLE IF NOT EXISTS blog_posts (
             postId INTEGER PRIMARY KEY AUTOINCREMENT,
             post_message TEXT NOT NULL,
             postDate TEXT DEFAULT CURRENT_TIMESTAMP,
             userId INTEGER,
             FOREIGN KEY (userID) REFERENCES users(userId);'''
        cursor.execute(sql_qry)
        conn.commit()
        print("Table 'blog_posts' created successfully.")
        print(f"{sql_qry} executed successfully.")
        print(f"************")
    

        
    except sq.Error as e:
        print(f"An error occurred while creating the database: {e}")
    finally:
        if conn:
            conn.close()
            print(f"Connection to database {database_name} closed.")    

    if __name__ == "__main__":
        database_name = ul.get_env('.env', 'database_name')
        if database_name:
            create_database(database_name)
        else:
            print("Database name not found in environment variables.")
  
#instead of a stored procedure, since sqlite doesn't have those
def add_user(database_name:str, username:str):
    '''This function adds a user to the users table.
    parms:
        database_name: represents the database to use or create.
        username: represents the username to add.
        
        returns:
        user who was added  
        2025-AUG-06'''
    
    

    try:
        conn = None
        with sq.connect(database=database_name) as conn:
            cursor = conn.cursor()
            sql_qry='INSERT INTO users (username) VALUES (?)', (username,)
            username=(userName,)
            cursor.execute((username, sql_qry))

            

            # Commit the changes
            conn.commit()
            print(f"User '{username}' added successfully.")
    except sq.Error as e:
        print(f"An error occurred while adding the user: {e}")
    finally:
        if conn:
            conn.close()
            print(f"Connection to database {database_name} closed.")

def add_blog_post(database_name:str, 
                  post_message:str,
                  userID:int):
    
    '''This function adds a blog post to the blog_posts table.
    parms:
        database_name: represents the database to use or create.
        post_message: represents the content of the blog post.
        userID: represents the user ID of the author of the blog post.
        returns:
        
        '''