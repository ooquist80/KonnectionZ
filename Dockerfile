FROM python:3.10-slim
LABEL authors="olle"
WORKDIR /app
COPY requirements.txt .
# Install dependencies
RUN pip install -r requirements.txt
# Copy the application code
COPY . .
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]