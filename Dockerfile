FROM docker.io/library/python:3.15.0-trixie AS python-build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

FROM docker.io/library/python:3.15.0-slim-trixie AS final-image
LABEL org.opencontainers.image.source=https://github.com/ppatrzyk/gitbi

WORKDIR /gitbi
COPY --from=python-build /opt/venv /opt/venv
COPY ./app /gitbi/app

ENV PATH="/opt/venv/bin:$PATH"

CMD ["uvicorn", "--app-dir=app", "--host=0.0.0.0", "--port=8000", "main:app"]
