# Use an official Python runtime as base image
FROM python:3.13-slim
EXPOSE 5000
# Set working directory
WORKDIR /app
# Copy your current directory contents into the container
COPY requirements.txt .
COPY . .
RUN pip install -r requirements.txt 
# Run the Flask app
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0"]
