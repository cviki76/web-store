FROM python:3


RUN mkdir -p /opt/src/application/warehouseman
WORKDIR /opt/src/application/warehouseman

COPY applications/warehouseman/application.py ./application.py
COPY applications/warehouseman/configuration.py ./configuration.py
COPY applications/warehouseman/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY decorator.py ./decorator.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/application/warehouseman"

ENTRYPOINT ["python", "./application.py"]