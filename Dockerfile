FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
EXPOSE 8080
COPY . .
# CMD ["gunicorn","app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8080"]


