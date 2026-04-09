FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make the run script executable
RUN chmod +x run.sh

# Default port locally (Render overrides this with the $PORT env var)
ENV PORT=10000
EXPOSE $PORT

# Start both services
ENTRYPOINT ["./run.sh"]
