import motor.motor_asyncio
from datetime import datetime
from config import DATABASE_URI, DATABASE_NAME


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.users
        self.files = self.db.files

    # ─── User Methods ───

    def new_user(self, id, name):
        return dict(id=id, name=name)

    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.users.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.users.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.users.count_documents({})
        return count

    async def get_all_users(self):
        return self.users.find({})

    async def delete_user(self, user_id):
        await self.users.delete_many({'id': int(user_id)})

    # ─── File Methods ───

    async def save_file(self, message_id, file_name, file_size, mime_type,
                        file_unique_id, file_id, user_id):
        """Save file metadata when user uploads a file."""
        file_hash = file_unique_id[:6]
        doc = {
            'message_id': message_id,
            'file_name': file_name,
            'file_size': file_size,
            'mime_type': mime_type,
            'file_unique_id': file_unique_id,
            'file_id': file_id,
            'hash': file_hash,
            'user_id': user_id,
            'created_at': datetime.utcnow(),
        }
        await self.files.insert_one(doc)
        return file_hash

    async def get_file(self, message_id):
        """Get file metadata by message ID."""
        return await self.files.find_one({'message_id': int(message_id)})

    async def get_file_by_hash(self, file_hash, message_id):
        """Get file by hash and message_id for verification."""
        return await self.files.find_one({
            'hash': file_hash,
            'message_id': int(message_id)
        })

    async def get_user_files(self, user_id, skip=0, limit=10):
        """Get all files uploaded by a specific user (paginated)."""
        cursor = self.files.find(
            {'user_id': int(user_id)}
        ).sort('created_at', -1).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_user_files_count(self, user_id):
        """Get total files count for a specific user."""
        return await self.files.count_documents({'user_id': int(user_id)})

    async def total_files_count(self):
        return await self.files.count_documents({})


db = Database(DATABASE_URI, DATABASE_NAME)
