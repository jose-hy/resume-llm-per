FROM --platform=linux/amd64 python:3.11


WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

EXPOSE 80

COPY . /code

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]