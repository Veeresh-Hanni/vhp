FROM python:3.13-slim

WORKDIR /app
COPY order_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY order_service/ .
EXPOSE 8000
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=8000"]
