from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src import base
from src.auth import models_user
from src.image import models_image


# Модель книги
class Book(base.Base):
    __tablename__: str = "book"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, onupdate=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False, onupdate=True)
    genre: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    image = relationship(
        "Image",
        back_populates="book",
        cascade="save-update, merge, delete, delete-orphan",
        uselist=False
        )
    registered_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped["models_user.User"] = relationship("User",
                                                     back_populates="books",
                                                     uselist=False
                                                     )
