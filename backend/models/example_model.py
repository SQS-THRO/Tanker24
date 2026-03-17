from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base
from pydantic import BaseModel

class example(Base):
    __tablename__ = "example_table"
    id = Column(UUID(as_uuid=True), default=uuid.uuid4 , primary_key=True, index=True)
    text = Column(String(64), index=True)

class exampleReturnModel(BaseModel):
    text: str

class exampleCreateModel(BaseModel):
    text: str

