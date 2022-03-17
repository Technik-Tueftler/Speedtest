FROM arm64v8/python:3.10.2-buster

ENV WORKING_DIR /user/app
WORKDIR $WORKING_DIR

COPY requirements.txt ./Speedtest/

RUN pip install -r ./Speedtest/requirements.txt
RUN pip install mariadb SQLAlchemy
RUN pip install sqlalchemy-utils

COPY files/ ./Speedtest/files/
COPY source/ ./Speedtest/source/

RUN echo "Wir sind die geilsten Hühner im Stall"

CMD ["python", "-u", "./Speedtest/source/main.py"]