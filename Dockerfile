FROM python:3.12-alpine

COPY ./requirements.txt /app/
RUN pip install -U --no-cache-dir -r /app/requirements.txt
COPY ./wifi_logger.py /app/

WORKDIR /app

CMD ["python", "-u", "wifi_logger.py"]