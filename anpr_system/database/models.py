from sqlalchemy import Column, DateTime, Integer, String, func, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class VehicleLog(Base):
    __tablename__ = "vehicle_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_type = Column(String, nullable=False)
    plate_number = Column(String)
    timestamp = Column(DateTime, server_default=func.current_timestamp(), nullable=False)
    video_source = Column(String)
