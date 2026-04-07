# 1. Base Image
FROM python:3.9-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# 3. Set Working Directory
WORKDIR /app

# 4. Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the project code
COPY . /app/

# 6. Default port for Flask
EXPOSE 5000

# 7. Run Flask app binding to 0.0.0.0 to allow external access
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
