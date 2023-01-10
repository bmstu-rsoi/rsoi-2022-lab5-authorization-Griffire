FROM python:3.9

RUN pip install \
    datetime \
    uuid \
    dataclasses \ 
 	uvicorn \
fastapi \
psycopg2 \
requests \
 pyjwt[crypto]






COPY / /app/

WORKDIR /app


CMD ["python3", "GateWay_Service.py" ]