import datetime as dt

from sqlalchemy import Numeric, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class SensorsBase(DeclarativeBase, MappedAsDataclass, kw_only=True):
    pass


class SensorReading(SensorsBase):
    __tablename__ = "sensor_reading"
    __table_args__ = {"schema": "sensors"}

    timestamp: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), primary_key=True
    )
    sensor_id: Mapped[str] = mapped_column(Text, primary_key=True)
    reading_value: Mapped[float] = mapped_column(Numeric, nullable=False)
