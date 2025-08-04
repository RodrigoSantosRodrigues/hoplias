from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from ..config import db_connection, db_name

PwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

client = AsyncIOMotorClient(db_connection)
db = client[db_name]
