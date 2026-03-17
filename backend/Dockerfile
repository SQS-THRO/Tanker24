# We use Python 3.13
FROM python:3.13-slim

# Copy backend dir to the Container
COPY . /app
WORKDIR /app

# Copy the requirements file into the image
COPY requirements.txt .

# Install Python dependencies as specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose the Port we will run uvicorn on
EXPOSE 80

# Start app with uvicorn
CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "80"]

