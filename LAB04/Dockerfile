FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY __init__.py app.py common.py /app/LAB04/
COPY registry.json /app/LAB04/registry.json
COPY artifacts/ /app/LAB04/artifacts/
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "LAB04.app:app", "--host", "0.0.0.0", "--port", "8000"]
