# Use the official Python image
FROM python:3.11-slim-bookworm

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose port
EXPOSE 8000

# Start the app
CMD ["uvicorn", "monorail_main:app", "--host", "0.0.0.0", "--port", "8000"]