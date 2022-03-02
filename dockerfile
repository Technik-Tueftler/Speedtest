FROM arm64v8/python:3.10.2-alpine3.15
WORKDIR /user/app

COPY requirements.txt ./Speedtest/
RUN pip install -r ./Speedtest/requirements.txt

COPY files/ ./Speedtest/files/
COPY source/ ./Speedtest/source/
# COPY requirements.txt .

RUN echo "Wir sind die geilsten Hühner im Stall"

CMD ["python", "-u", "./Speedtest/source/main.py"]