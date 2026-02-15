import motor.motor_asyncio
from config import DATABASE_URI, DATABASE_NAME


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.files = self.db.files

    async def get_file(self, message_id):
        """Get file metadata by message ID."""
        return await self.files.find_one({'message_id': int(message_id)})

    async def get_file_by_hash(self, file_hash, message_id):
        """Get file by hash and message_id for verification."""
        return await self.files.find_one({
            'hash': file_hash,
            'message_id': int(message_id)
        })


db = Database(DATABASE_URI, DATABASE_NAME)
