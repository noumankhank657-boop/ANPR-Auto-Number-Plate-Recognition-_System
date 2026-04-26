import os
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from config import DB_PATH
from database.models import Base, VehicleLog

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def insert_log(vehicle_type, plate_number, timestamp, video_source):
    session = SessionLocal()
    try:
        if timestamp is None:
            new_log = VehicleLog(
                vehicle_type=vehicle_type,
                plate_number=plate_number,
                video_source=video_source,
            )
        else:
            new_log = VehicleLog(
                vehicle_type=vehicle_type,
                plate_number=plate_number,
                timestamp=timestamp,
                video_source=video_source,
            )
        session.add(new_log)
        session.commit()
        session.refresh(new_log)
        return new_log.id
    finally:
        session.close()


def get_all_logs():
    session = SessionLocal()
    try:
        logs = session.query(VehicleLog).order_by(VehicleLog.timestamp.desc()).all()
        return [
            {
                "id": log.id,
                "vehicle_type": log.vehicle_type,
                "plate_number": log.plate_number,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "video_source": log.video_source,
            }
            for log in logs
        ]
    finally:
        session.close()


def get_logs_by_type(vehicle_type):
    session = SessionLocal()
    try:
        logs = session.query(VehicleLog).filter(VehicleLog.vehicle_type == vehicle_type).order_by(VehicleLog.timestamp.desc()).all()
        return [
            {
                "id": log.id,
                "vehicle_type": log.vehicle_type,
                "plate_number": log.plate_number,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "video_source": log.video_source,
            }
            for log in logs
        ]
    finally:
        session.close()


def get_logs_by_video(video_source):
    session = SessionLocal()
    try:
        logs = session.query(VehicleLog).filter(VehicleLog.video_source == video_source).order_by(VehicleLog.timestamp.desc()).all()
        return [
            {
                "id": log.id,
                "vehicle_type": log.vehicle_type,
                "plate_number": log.plate_number,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "video_source": log.video_source,
            }
            for log in logs
        ]
    finally:
        session.close()


def get_analytics():
    session = SessionLocal()
    try:
        vehicle_counts = session.query(VehicleLog.vehicle_type, func.count(VehicleLog.id)).group_by(VehicleLog.vehicle_type).all()
        hourly_counts = session.query(
            func.strftime("%Y-%m-%d %H:00:00", VehicleLog.timestamp),
            func.count(VehicleLog.id),
        ).group_by(func.strftime("%Y-%m-%d %H:00:00", VehicleLog.timestamp)).order_by(func.strftime("%Y-%m-%d %H:00:00", VehicleLog.timestamp)).all()

        return {
            "vehicle_type_counts": [{"vehicle_type": vehicle_type, "count": count} for vehicle_type, count in vehicle_counts],
            "hourly_counts": [{"hour": hour, "count": count} for hour, count in hourly_counts],
        }
    finally:
        session.close()
