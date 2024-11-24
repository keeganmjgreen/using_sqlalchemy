import pytest
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema

import pandas as pd

from db_model import SensorReading, SensorsBase


@pytest.fixture
def url(postgresql) -> URL:
    url = URL.create(
        drivername="postgresql",
        username=postgresql.info.user,
        password=postgresql.info.password,
        host=postgresql.info.host,
        port=postgresql.info.port,
        database=postgresql.info.dbname,
    )
    engine = create_engine(url)
    with Session(engine) as session:
        session.execute(CreateSchema("sensors"))
        session.commit()
    SensorsBase.metadata.create_all(engine)
    with Session(engine) as session:
        for i in range(3):
            sensor_reading = SensorReading(
                timestamp=pd.Timestamp("2000-01-01 00:00+00:00").to_pydatetime(),
                sensor_id=f"sensor-{i}",
                reading_value=i,
            )
            session.add(sensor_reading)
            session.commit()
    return url


def test_raw_sql_mode(url):
    from sqlalchemy import create_engine, text

    engine = create_engine(url)

    with engine.connect() as connection:
        query = text(
            """
            SELECT DISTINCT ON (sensor_id)
                sr.sensor_id, sr.reading_value AS value
            FROM sensors.sensor_reading AS sr
            WHERE sr.sensor_id = ANY(:sensor_ids)
            ORDER BY sr.sensor_id, sr.timestamp DESC
            """
        )
        latest_sensor_readings = connection.execute(
            query,
            parameters={
                "sensor_ids": ["sensor-1", "sensor-2"],
            },
        )


def test_sql_expression_language(url):
    from sqlalchemy import create_engine, select

    from db_model import SensorReading

    engine = create_engine(url)

    with engine.connect() as connection:
        sr = SensorReading
        sensor_ids = ["sensor-1", "sensor-2"]
        query = (
            select(sr.sensor_id, sr.reading_value.label("value"))
            .distinct(sr.sensor_id)
            .where(sr.sensor_id.in_(sensor_ids))
            .order_by(sr.sensor_id, sr.timestamp.desc())
        )
        latest_sensor_readings = connection.execute(query)
