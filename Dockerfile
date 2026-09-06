FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py test_workflow.py ./
USER 10001:10001
CMD ["python", "-u", "app.py"]
