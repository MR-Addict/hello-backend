FROM python:3.9.15-slim
WORKDIR /app
EXPOSE 8090
COPY src .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "index.py"]