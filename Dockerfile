FROM python:slim-buster
WORKDIR /usr/src/app
EXPOSE 8090
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "index.py"]