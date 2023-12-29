FROM python:3.11

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* ./

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY main.py .

CMD python -u main.py

