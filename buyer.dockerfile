FROM python:3


RUN mkdir -p /opt/src/application/buyer
WORKDIR /opt/src/application/buyer

COPY applications/buyer/application.py ./application.py
COPY applications/buyer/configuration.py ./configuration.py
COPY applications/buyer/models.py ./models.py
COPY applications/requirements.txt ./requirements.txt
COPY decorator.py ./decorator.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/application/buyer"

ENTRYPOINT ["python", "./application.py"]