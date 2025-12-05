# Use an official Python runtime as the base image
FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["fastapi", "dev", "api.py", "--host=0.0.0.0", "--port=8500"]