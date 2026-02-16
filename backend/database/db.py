import motor.motor_asyncio
from config import DATABASE_URI, DATABASE_NAME

# Fix SSL issues on VPS with older OpenSSL
try:
    import certifi
    ssl_cert = certifi.where()
except ImportError:
    ssl_cert = True


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            uri,
            tls=True,
            tlsCAFile=ssl_cert if isinstance(ssl_cert, str) else None,
            tlsAllowInvalidCertificates=not isinstance(ssl_cert, str),
        )
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
