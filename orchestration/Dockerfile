FROM python:3.11-slim
WORKDIR /opt/dagster/app
COPY orchestration/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY orchestration/ ./orchestration/
COPY dbt/ ./dbt/
COPY dbt/profiles.yml .
EXPOSE 3000
CMD ["dagster", "dev", "-f", "definitions.py", "-h", "0.0.0.0", "-p", "3000"]