from sqlalchemy import create_engine, Column, Boolean, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import secrets

SQLALCHEMY_DATABASE_URL = "sqlite:///./rsvp_returns.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()


class Guest(Base):
    __tablename__ = "guest_list"

    id = Column(String, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    display_name = Column(String, nullable=True, default=None)
    accomodation = Column(Boolean)
    attending = Column(Boolean, default=False)
    requirements = Column(String, nullable=True, default=None)
    linked_to = Column(String, nullable=True, default=None)
    responded_at = Column(DateTime, nullable=True, default=None)

    def __init__(self, first_name, last_name, display_name, linked_to) -> None:
        self.id = secrets.token_urlsafe(6)
        self.first_name = first_name
        self.last_name = last_name
        self.display_name = display_name
        self.linked_to = linked_to

    @property
    def name(self):
        if self.display_name is not None:
            return self.display_name

        return f"{self.first_name} {self.last_name}"
