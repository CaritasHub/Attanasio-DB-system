FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app
COPY DockerConfig/DBScript.sql /app/DBScript.sql
RUN chmod +x /app/entrypoint.sh
# Run the entrypoint script through /bin/sh to avoid exec format issues
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
