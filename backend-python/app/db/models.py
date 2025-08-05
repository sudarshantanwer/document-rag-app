from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
import uuid

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=True)
    embedding: Mapped[list] = mapped_column(JSON, nullable=True)
    num_chunks: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    vector_ids: Mapped[list] = mapped_column(JSON, nullable=False)
