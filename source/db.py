#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main functions for checking env variables, creating database tables and inserting new measurements
Check if a database connection is available with the passed env variables and checks if they are
valid. In case no connection information are available or they are invalid, a sqlite database
will be created and used as a endpoint.
"""
import os
from datetime import datetime
from dataclasses import dataclass

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()

if os.getenv("WORKING_DIR") is None:
    SQL_DB_PATH = "sqlite:///../files/measurements.sqlite3"
else:
    SQL_DB_PATH = "sqlite:///./Speedtest/files/measurements.sqlite3"

CONNECTOR = os.getenv("DB_CONNECTOR", SQL_DB_PATH)
try:
    engine = create_engine(CONNECTOR)
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(engine)
    engine.dispose()

except sqlalchemy.exc.OperationalError as err:
    CONNECTOR = SQL_DB_PATH
    print(f"ERROR: No connection to the database is possible. Aborted with error: [{err}]. "
          f"Please check DB_CONNECTOR. The measurements will be stored in a SQLite anyway.")
    engine = create_engine(SQL_DB_PATH)
    Base.metadata.create_all(engine)
    engine.dispose()

except sqlalchemy.exc.ProgrammingError as err:
    print(f"ERROR: unexpected error: [{err}].")


class Measurements(Base):  # pylint: disable=too-few-public-methods
    """Table structure for measurements for easy work with an ORM"""
    __tablename__ = 'measurements'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    max_download_fritzbox = sqlalchemy.Column(sqlalchemy.Integer)
    max_upload_fritzbox = sqlalchemy.Column(sqlalchemy.Integer)
    avg_download_speedtest = sqlalchemy.Column(sqlalchemy.Integer)
    avg_upload_speedtest = sqlalchemy.Column(sqlalchemy.Integer)
    ping_speedtest = sqlalchemy.Column(sqlalchemy.Integer)


@dataclass
class SQLAlchemyConnectionManager:
    """
    Timer class to create the times for the measurements and repetitions
    :param connector: Connection string for access to the database
    """
    connector: str
    engine: sqlalchemy.engine.Engine = None
    session_make: sqlalchemy.orm.session.sessionmaker = None
    session: sqlalchemy.orm.session.Session = None

    def __enter__(self):
        self.engine = create_engine(self.connector)
        Base.metadata.bind = self.engine
        self.session_make = sessionmaker(bind=self.engine)
        self.session = self.session_make()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.session.close()
        self.engine.dispose()

    def add(self, data: Measurements):
        """Add measurement data to the session and commit it."""
        self.session.add(data)
        self.session.commit()


def add_measurement(data: dict) -> None:
    """General function to add results of the speed test to the database."""
    with SQLAlchemyConnectionManager(CONNECTOR) as conn:
        conn.add(Measurements(timestamp=datetime.now(),
                              max_download_fritzbox=data["max_download_fritzbox"],
                              max_upload_fritzbox=data["max_upload_fritzbox"],
                              avg_download_speedtest=data["avg_download_speedtest"],
                              avg_upload_speedtest=data["avg_upload_speedtest"],
                              ping_speedtest=data["ping_speedtest"]))


def main() -> None:
    """Main function for db and test locally."""
    with SQLAlchemyConnectionManager(SQL_DB_PATH) as session:
        session.add(Measurements(timestamp=datetime.now(),
                                 max_download_fritzbox=676,
                                 max_upload_fritzbox=676,
                                 avg_download_speedtest=676,
                                 avg_upload_speedtest=676,
                                 ping_speedtest=676))


if __name__ == "__main__":
    main()
