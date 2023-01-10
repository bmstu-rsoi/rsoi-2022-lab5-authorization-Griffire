import os

import uvicorn
import psycopg2
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI, status, Body, Header
from fastapi.requests import Request
from dataclasses import dataclass


app = FastAPI()

port = 8060
conn = psycopg2.connect(dbname="postgres", user="program", password="test", host="postgres-service", port="5432")
# conn = psycopg2.connect(dbname="postgres", user="program", password="test", host="postgres", port="5432")


sql_path = os.path.dirname(__file__)


def start_DB():
    print('starting')

    print('__')
    f_payment_start = open(sql_path + '/Payment_Service_SQL/payment_start.sql', 'r')
    sqlFile_payment_start = f_payment_start.read()
    f_payment_start.close()

    print('___')
    f_payment_stop = open(sql_path + '/Payment_Service_SQL/payment_stop.sql', 'r')
    sqlFile_payment_stop = f_payment_stop.read()
    f_payment_stop.close()

    with conn.cursor() as cur:
        cur.execute(sqlFile_payment_stop)
        cur.execute(sqlFile_payment_start)
        conn.commit()


@app.get("/manage/health")
def get_hotels_page():
    headers = {'Content-Type': 'application/json'}
    return JSONResponse(content="Host localhost:8060 is active", headers=headers, status_code=status.HTTP_200_OK)


@app.get("/api/v1/check")
def get_hotels_page():
    with conn.cursor() as cur:
        print("8060 is alive")
        data = {'all': 'ok_8060'}
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=data, headers=headers, status_code=status.HTTP_200_OK)


@dataclass
class Payment:
    id: int
    payment_uid: str
    status: str
    price: int


@app.get("/api/v1/payments/")
def get_loyalty(request: Request):
    with conn.cursor() as cur:
        payment_uid = request.headers.get('payment_uid')
        print(payment_uid)
        if payment_uid is not None:
            print('id is in')
            cur.execute(
                f'Select * from payment where payment_uid=\'{payment_uid}\' '
            )
        else:
            print('id is off')
            cur.execute(
                f'Select * from payment'
            )
        payment_row = cur.fetchall()
        if len(payment_row) > 0:
            print(payment_row)
            r = [Payment(*payment_row[i]) for i in range(len(payment_row))] if payment_row else None
            r_arr = []
            for i in r:
                payment = {}
                print("________")
                for j in i.__dict__.items():
                    payment[j[0]] = j[1]
                r_arr.append(payment)
            headers = {'Content-Type': 'application/json'}
            return JSONResponse(content=r_arr, headers=headers, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content=[], status_code=status.HTTP_404_NOT_FOUND)




@app.post("/api/v1/payments/")
def get_loyalty(request: Request):
    with conn.cursor() as cur:
        paymentUid = request.headers.get('paymentUid')
        payment_status = request.headers.get('status')
        payment_price = int(request.headers.get('price'))

        cur.execute(
            f'INSERT INTO  payment(payment_uid , status, price) values(\'{paymentUid}\' ,\'{payment_status}\', {payment_price}   ) '
        )
        return JSONResponse(content=[], status_code=status.HTTP_201_CREATED)

@app.delete("/api/v1/payments/delete")
def delete_payment(request: Request):
    print('DELETE')
    with conn.cursor() as cur:
        paymentUid = request.headers.get('paymentUid')

        print('del', paymentUid )
        cur.execute(
            f'UPDATE payment SET '
            f' status = \'CANCELED\''
            f'where payment_uid= \'{paymentUid}\''
        )

        return JSONResponse(content=[], status_code=status.HTTP_301_MOVED_PERMANENTLY)



if __name__ == "__main__":

    print(sql_path)
    start_DB()
    uvicorn.run(app, host="0.0.0.0", port=port)

    # uvicorn.run(app, host="localhost", port=port)
