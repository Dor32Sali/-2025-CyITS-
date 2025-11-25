FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Default port inside the container
EXPOSE 8000

CMD ["python", "app.py"]
