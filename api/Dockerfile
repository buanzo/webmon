FROM python:3.5
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN chmod +x /code/ronald.py
RUN ls -l /code
CMD ["/code/ronald.py"]
