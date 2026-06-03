FROM python:3.11-slim

RUN pip install --no-cache-dir \
    dbt-core \
    dbt-databricks

WORKDIR /dbt

CMD ["tail", "-f", "/dev/null"]
