FROM python:3.5
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN chmod +x /code/executor.py
RUN ls
RUN pwd
ENTRYPOINT ["/code/executor.py"]
