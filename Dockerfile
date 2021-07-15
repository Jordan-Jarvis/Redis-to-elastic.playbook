FROM python:3

LABEL maintainer="Jordan Jarvis"

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY pylogstash /usr/share/pylogstash/.

CMD ["python", "/usr/share/pylogstash/main.py"]

