
FROM python:3.11-slim AS compile-image

RUN apt-get update \
    && apt-get install -y \
    gcc \
    build-essential \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip3 install -r requirements.txt

FROM python:3.11-slim AS build-image
RUN apt-get update \
    && apt-get install -y \
    git \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY --from=compile-image /opt/venv /opt/venv
COPY . ./app

RUN useradd -U appuser \
    && chown -R appuser:appuser ./app
USER appuser
WORKDIR /app
ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000
CMD [ "./start_app.sh" ]
