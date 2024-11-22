from sqlalchemy import String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True,nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    refer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)

    refer_count: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

class Chanel(Base):
    __tablename__ = "channels"
    id: Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    title:Mapped[str]=mapped_column(String,nullable=False)
    url:Mapped[str]=mapped_column(String,nullable=False)


