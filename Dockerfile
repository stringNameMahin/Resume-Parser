# Use official Python image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Use the PORT environment variable provided by Cloud Run
CMD ["python", "main.py", "sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
