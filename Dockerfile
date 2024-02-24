FROM python:3.12-alpine

COPY ./wifi_logger.py /app/
COPY ./requirements.txt /app/
RUN pip install -U --no-cache-dir -r /app/requirements.txt

WORKDIR /app

CMD ["python", "wifi_logger.py"]