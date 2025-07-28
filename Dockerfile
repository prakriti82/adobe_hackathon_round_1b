FROM --platform=linux/amd64 python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# This command copies all your .py scripts into the container
COPY . .

# This sets your main script as the one to run when the container starts
CMD ["python", "extractor_1b.py"]