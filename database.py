from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./ticket_system.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    category = Column(String)  # 'standard' ወይም 'lottery'
    price = Column(Float)
    total_tickets = Column(Integer)
    date = Column(String)

class BankAccount(Base):
    __tablename__ = "bank_accounts"
    id = Column(Integer, primary_key=True, index=True)
    bank_name = Column(String)
    account_number = Column(String)
    account_holder = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String, unique=True, index=True)
    event_id = Column(Integer)
    buyer_name = Column(String)
    buyer_phone = Column(String)
    quantity = Column(Integer)
    total_amount = Column(Float)
    selected_bank = Column(String)
    status = Column(String, default="pending")  # pending, approved, rejected, expired
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    receipt_image = Column(String, nullable=True)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True)
    order_code = Column(String)
    event_id = Column(Integer)
    is_used = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)