from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .constants import UUID_LENGTH

__all__ = ["DocumentTypeTable"]


class DocumentTypeTable(Base):
    __tablename__ = "document_type"
    id: Mapped[str] = mapped_column(String(UUID_LENGTH), primary_key=True)
