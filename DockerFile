# Base image with Python 3.9
FROM python:3.9-slim

# Install system deps if needed (none for gspread)
WORKDIR /app

# Copy and install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script and service‑account file
COPY upload_to_sheets.py .
# If you commit your JSON key, also COPY it:
# COPY service-account.json .

# Make the script executable
RUN chmod +x upload_to_sheets.py

# Default command
CMD ["./upload_to_sheets.py"]
