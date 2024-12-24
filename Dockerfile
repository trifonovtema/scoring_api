FROM python:3.12-slim
WORKDIR /src
COPY pyproject.toml poetry.lock ./
RUN pip install poetry==1.8.3 && poetry install --no-dev
COPY src /src
ENV PYTHONPATH=/src
WORKDIR /
CMD ["poetry","--directory", "/src", "run", "python", "-m","src.api"]