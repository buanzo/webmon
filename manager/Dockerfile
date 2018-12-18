FROM python:3.5
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN chmod +x /code/manager.py
RUN ls -l /code
CMD ["/code/manager.py"]
