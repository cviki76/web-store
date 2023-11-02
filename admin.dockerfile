FROM python:3


RUN mkdir -p /opt/src/application/admin
WORKDIR /opt/src/application/admin

COPY applications/admin/application.py ./application.py
COPY applications/admin/configuration.py ./configuration.py
COPY applications/admin/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY decorator.py ./decorator.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/application/admin"

ENTRYPOINT ["python", "./application.py"]