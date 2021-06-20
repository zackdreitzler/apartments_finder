FROM python:3.9.5-buster

RUN mkdir apartments_finder_app

WORKDIR ./apartments_finder_app

RUN python3 -m venv venv

COPY ./apartments_finder .

COPY requirements.txt .

RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python3", "apartments_finder.py"]
