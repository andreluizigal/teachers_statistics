FROM andreluizigal/grafana_teachers_statistics:TCC

USER root

RUN apk update && \
    apk add --no-cache python3 py3-pip

COPY ./ /app

WORKDIR /app

RUN pip install beautifulsoup4 requests psycopg2-binary unicode unidecode

CMD ["bash"]