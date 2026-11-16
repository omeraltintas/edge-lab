from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from edge_lab.db import Base


class Link(Base):
    __tablename__ = "links"

    code: Mapped[str] = mapped_column(String(16), primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    owner_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
