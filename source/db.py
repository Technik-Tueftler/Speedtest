#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from datetime import datetime
from dataclasses import dataclass

Base = declarative_base()
connector = None

if os.getenv("WORKING_DIR") is None:
    sql_db_path = "sqlite:///../files/measurements.sqlite3"
else:
    sql_db_path = "sqlite:///./Speedtest/files/measurements.sqlite3"


class Measurements(Base):
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
        self.session.add(data)
        self.session.commit()


def add_measurement(data: dict) -> None:
    with SQLAlchemyConnectionManager(connector) as conn:
        conn.add(Measurements(timestamp=datetime.now(),
                              max_download_fritzbox=data["max_download_fritzbox"],
                              max_upload_fritzbox=data["max_upload_fritzbox"],
                              avg_download_speedtest=data["avg_download_speedtest"],
                              avg_upload_speedtest=data["avg_upload_speedtest"],
                              ping_speedtest=data["ping_speedtest"]))


def check_and_verify_database_connection() -> None:
    global connector
    connector = os.getenv("DB_CONNECTOR", sql_db_path)
    try:
        engine = create_engine(connector)
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine)
        engine.dispose()

    except sqlalchemy.exc.OperationalError as e:
        connector = sql_db_path
        print(f"ERROR: No connection to the database is possible. Aborted with error: [{e}]. "
              f"Please check DB_CONNECTOR. The measurements will be stored in a SQLite anyway.")
        engine = create_engine(sql_db_path)
        Base.metadata.create_all(engine)
        engine.dispose()

    except sqlalchemy.exc.ProgrammingError as e:
        print(f"ERROR: unexpected error: [{e}].")


def main() -> None:
    with SQLAlchemyConnectionManager(sql_db_path) as session:
        session.add(Measurements(timestamp=datetime.now(),
                                 max_download_fritzbox=676,
                                 max_upload_fritzbox=676,
                                 avg_download_speedtest=676,
                                 avg_upload_speedtest=676,
                                 ping_speedtest=676))


if __name__ == "__main__":
    main()
