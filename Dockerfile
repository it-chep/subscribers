FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN apt-get -y update
RUN apt-get -y install vim nano
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "main.py"]