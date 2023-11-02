FROM python:3


RUN mkdir -p /opt/src/application/daemon
WORKDIR /opt/src/application/daemon

COPY applications/daemon/application.py ./application.py
COPY applications/daemon/configuration.py ./configuration.py
COPY applications/daemon/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY decorator.py ./decorator.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/application/daemon"

ENTRYPOINT ["python", "./application.py"]