# Using SQLAlchemy

SQLAlchemy is a library that provides functionality for interacting and working with databases in Python.

Queries (and other database operations) can be written in three ways using SQLAlchemy, and each has their advantages and disadvantages.

The first way, which I call 'raw SQL' mode, consists of writing queries in plain old SQL. The third way — object-relational mapping, or ORM — involves using SQLAlchemy to create a mapping between Python objects and database records, such that they can be interacted with in a natural way without needing to write any SQL. And the second way — SQLAlchemy's SQL Expression Language — is like a middle-ground (perhaps even a best-of-both-worlds) between the two.

A project should either stick to raw SQL mode or, preferably, stick to SQL Expression Language and/or ORM.

## 'Raw SQL' mode

SQLAlchemy allows queries to be written in plain old SQL. This will be most familiar to users of `psycopg2`.

```python
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
```

Being able to write raw SQL queries means that your code for interacting with databases is language-independent — your queries are written the same regardless of whether they are executed by a Python program or a program written in another language. The only practical advantage of this, however, is being able to copy the query elsewhere, such as into a database client (DataGrip, DBeaver, etc.). One might argue that doing this is necessary when debugging your deployed software, by recreating your query's execution or output. But such an inefficient process does not help when debugging parts of your code other than its database interactions, and can be largely avoided in the first place using thorough unit tests (more on this later).

## SQL Expression Language

Writing raw SQL queries as a big string within a `.py` file has numerous disadvantages. There is no autocomplete of SQL syntax, nor docstrings, nor syntax highlighting to quickly differentiate between SQL syntax, identifiers, and comments. Raw SQL queries cannot be auto-formatted by your Python code formatter, creating a breeding ground for inconsistent indentation, spacing, and cases.

SQLAlchemy's SQL Expression Language solves these issues by allowing you to write queries in Python syntax that resembles SQL as closely as possible. This makes for a smooth transition from writing in raw SQL. Because your query becomes no different than the rest of your `.py` file, you automatically get autocomplete, docstrings, syntax highlighting, and auto-formatting along with the rest of your Python code. Query comments become Python comments — no longer second-class citizens in a sea of plaintext. And SQL Expression Language allows parameters to be naturally inserted into your queries, which helps discourage hard-coding of values.

```python
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
```

What is `SensorReading` in the above example? I don't know — what was the `sensors.sensor_reading` table in the previous raw-SQL example? In the raw-SQL example, this table's columns and data types had to be inferred by their usage, else manually looked-up in the database. Whether a table, DataFrame, or dict, inferring the attributes (and their data types) of a data model by how those attributes are used is bad practice because it can often lead to a pieced-together, incomplete, and inaccurate picture of the data model. SQL Expression Language forces you to adhere to best practices and define a data model for each table you want to work with, most importantly including the table columns (and their data types). This also enables autocomplete and docstrings for column names.

```python
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
```

<!-- Can use tables or ORM objects. -->

<!-- making some sql syntax clearer, eg desc -->
<!-- learning 1 lang -->

## ORM

<!-- abstracts away -->
