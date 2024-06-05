import aiosqlite

class AuthenticationDBManager:
    def __init__(self, db_path='data/Authentication.db'):
        # Initialize the database path
        self.db_path = db_path

    async def connect_to_database(self):
        # Establish a connection to the database
        self.connection = await aiosqlite.connect(self.db_path)
        return self.connection
    
    async def close_connection(self):
        # Close the connection to the database if it is open
            await self.connection.close()

    async def create_users_table(self):
        # Create the users table if it does not exist
        conn = await self.connect_to_database()
        cursor = await conn.cursor()
        await cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        random_state TEXT PRIMARY KEY,
                        access_token TEXT,
                        refresh_token TEXT,
                        expiration_time INTEGER
                     )''')
        await conn.commit()
        await conn.close()

    
            
    async def save_user_data(self, random_state, access_token, refresh_token, expiration_time):
        # Save user data to the users table
        conn = await self.connect_to_database()
        cursor = await conn.cursor()
        await cursor.execute("INSERT INTO users (random_state, access_token, refresh_token, expiration_time) VALUES (?, ?, ?, ?)",
                               (random_state, access_token, refresh_token, expiration_time))
        await conn.commit()
        await conn.close()

    async def get_user_data(self, random_state):
        # Retrieve user data from the users table based on random_state
        conn = await self.connect_to_database()
        cursor = await conn.cursor()
        await cursor.execute("SELECT * FROM users WHERE random_state=?", (random_state,))
        row = await cursor.fetchone()
        await conn.close()
        return row

    async def update_user_tokens(self, random_state, access_token, refresh_token, expiration_time):
        # Update user tokens in the users table
        conn = await self.connect_to_database()
        cursor = await conn.cursor()
        await cursor.execute("UPDATE users SET access_token = ?, refresh_token = ?, expiration_time = ? WHERE random_state = ?", 
                                (access_token, refresh_token, expiration_time, random_state))
        await conn.commit()
        await conn.close()

    async def delete_user_data(self, random_state):
        # Delete user data from the users table based on random_state
        conn = await self.connect_to_database()
        cursor = await conn.cursor()
        await cursor.execute("DELETE FROM users WHERE random_state=?", (random_state,))
        await conn.commit()
        await conn.close()


class StorySTPDBManager:
    def __init__(self, db_path='data/Story_STP.db'):
        # Initialize the database path
        self.db_path = db_path
        self.conn = None
    async def connect_to_database(self):
        # Establish a connection to the database
        self.conn = await aiosqlite.connect(self.db_path)
        
    async def insert_stp(self, user_story, stp):
        # Insert a new story and STP into the Story_STP table
        if not self.conn:
            await self.connect_to_database()
        cursor = await self.conn.execute("INSERT INTO Story_STP (user_story, STP) VALUES (?, ?)", (user_story, stp))
        await self.conn.commit()

    async def get_stp_by_index(self, top_index):
        # Retrieve an STP from the Story_STP table based on the index
        if not self.conn:
            await self.connect_to_database()
        cursor = await self.conn.execute("SELECT STP FROM Story_STP WHERE ROWID = ?", (int(top_index) + 1,))
        stp, = await cursor.fetchone()
        return stp
    
