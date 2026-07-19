FROM python:3.12-alpine3.24 AS builder
WORKDIR /build
RUN apk add --no-cache gcc musl-dev python3-dev linux-headers
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt
FROM python:3.12-alpine3.24
ENV LANG=ru_RU.UTF-8
ENV LC_ALL=ru_RU.UTF-8
ENV PYTHONIOENCODING=utf-8
WORKDIR /python-app
COPY --from=builder /build/wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && rm -rf /wheels
COPY . .
CMD [ "python", "main.py" ]