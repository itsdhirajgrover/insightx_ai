from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from datetime import datetime
import enum
from src.database.database import Base

class TransactionStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"

class DeviceType(str, enum.Enum):
    IOS = "iOS"
    ANDROID = "Android"
    WEB = "Web"

class NetworkType(str, enum.Enum):
    WIFI = "WiFi"
    MOBILE_4G = "4G"
    MOBILE_5G = "5G"

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    device_type = Column(String(20), nullable=False)
    network_type = Column(String(20), nullable=False)
    state = Column(String(50), nullable=False, index=True)
    age_group = Column(String(20), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="success")
    fraud_flag = Column(Boolean, default=False, index=True)
    merchant_id = Column(Integer, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    
    class Config:
        from_attributes = True
