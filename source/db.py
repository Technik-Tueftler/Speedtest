#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os
from datetime import datetime

# engine = sqlalchemy.create_engine("postgresql+psycopg2://app_user:Password123!@127.0.0.1:3306/company")

Base = declarative_base()
session = None

if os.getenv("WORKING_DIR") is None:
    sql_db_path = "sqlite:///../files/measurements.sqlite3"
else:
    sql_db_path = "sqlite:///./Speedtest/files/measurements.sqlite3"


class Measurements(Base):
    __tablename__ = 'measurements'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    # timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False, server_default=text("NOW()"))
    timestamp = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=False), nullable=False)
    max_download_fritzbox = sqlalchemy.Column(sqlalchemy.Integer)
    max_upload_fritzbox = sqlalchemy.Column(sqlalchemy.Integer)
    avg_download_speedtest = sqlalchemy.Column(sqlalchemy.Integer)
    avg_upload_speedtest = sqlalchemy.Column(sqlalchemy.Integer)
    ping_speedtest = sqlalchemy.Column(sqlalchemy.Integer)


def commit(function):
    def wrapper(*args, **kwargs):
        return_function = function(*args, **kwargs)
        session.commit()
        return return_function
    return wrapper


@commit
def add_measurement(data: dict) -> None:
    session.add(Measurements(timestamp=datetime.now(),
                             max_download_fritzbox=data["max_download_fritzbox"],
                             max_upload_fritzbox=data["max_upload_fritzbox"],
                             avg_download_speedtest=data["avg_download_speedtest"],
                             avg_upload_speedtest=data["avg_upload_speedtest"],
                             ping_speedtest=data["ping_speedtest"]))


def check_and_verify_database_connection() -> None:
    global Base
    global session
    connector = os.getenv("DB_CONNECTOR", sql_db_path)
    try:
        engine = create_engine(connector)
        if not database_exists(engine.url):
            create_database(engine.url)
        Base.metadata.create_all(engine)
        session_make = sessionmaker(bind=engine)
        session = session_make()

    except sqlalchemy.exc.OperationalError as _:
        print("Keine Verbindung zur Datenbank möglich. Es wird eine sqlite angelegt. Siehe Doku.")
        engine = create_engine(sql_db_path)
        Base.metadata.create_all(engine)
        sessionmake = sessionmaker(bind=engine)
        session = sessionmake()
    except sqlalchemy.exc.ProgrammingError as _:
        print("es ist schon wieder passiert")


def main() -> None:
    # check_and_verify_database_connection()

    pass


if __name__ == "__main__":
    main()
