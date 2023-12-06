FROM python:3.11.7-slim
RUN apt-get update \
    && apt-get install -y \
    git \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
COPY . ./gitbi
RUN pip3 install -r gitbi/requirements.txt

RUN useradd -U gitbiuser \
    && chown -R gitbiuser:gitbiuser ./gitbi
USER gitbiuser
WORKDIR /gitbi
EXPOSE 8000
CMD [ "./start_app.sh" ]
