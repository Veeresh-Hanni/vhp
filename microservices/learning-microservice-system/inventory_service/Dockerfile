FROM python:3.13-slim

WORKDIR /app
COPY inventory_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY inventory_service/ .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
