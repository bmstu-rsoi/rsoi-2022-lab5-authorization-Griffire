import os

import uvicorn
import psycopg2
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI, status, Body, Header
from fastapi.requests import Request
from dataclasses import dataclass


app = FastAPI()

port = 8050
conn = psycopg2.connect(dbname="postgres", user="program", password="test", host="postgres-service", port="5432")
# conn = psycopg2.connect(dbname="postgres", user="program", password="test", host="postgres", port="5432")


sql_path = os.path.dirname(__file__)



def start_DB():
    print('starting')
    f_loyalty_start = open(sql_path + '/Loyalty_Service_SQL/loyalty_start.sql', 'r')
    sqlFile_loyalty_start = f_loyalty_start.read()
    f_loyalty_start.close()

    print('_')
    f_loyalty_stop = open(sql_path + '/Loyalty_Service_SQL/loyalty_stop.sql', 'r')
    sqlFile_loyalty_stop = f_loyalty_stop.read()
    f_loyalty_stop.close()

    with conn.cursor() as cur:
        cur.execute(sqlFile_loyalty_stop)
        cur.execute(sqlFile_loyalty_start)
        conn.commit()


@app.get("/manage/health")
def get_hotels_page():
    headers = {'Content-Type': 'application/json'}
    return JSONResponse(content="Host localhost:8050 is active", headers=headers, status_code=status.HTTP_200_OK)


@app.get("/api/v1/check")
def get_hotels_page():
    with conn.cursor() as cur:
        print("8050 is alive")
        data = {'all': 'ok_8050'}
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=data, headers=headers, status_code=status.HTTP_200_OK)



@dataclass
class Loyalty:
    id: int
    username: str
    reservationCount: int
    status: str
    discount: int


@app.get("/api/v1/loyalty/")
def get_loyalty(request: Request):
    with conn.cursor() as cur:
        user_name = request.headers.get('user_name')
        print(user_name)
        cur.execute(
            f'Select * from loyalty where username= \'{user_name}\''
        )
        loyalty_row = cur.fetchall()
        if len(loyalty_row) > 0:
            print(loyalty_row)
            r = [Loyalty(*loyalty_row[i]) for i in range(len(loyalty_row))] if loyalty_row else None
            r_arr = []
            for i in r:
                loyalty = {}
                print("________")
                for j in i.__dict__.items():
                    loyalty[j[0]] = j[1]
                r_arr.append(loyalty)
            # data = {'page': 1, 'pageSize': 3, 'totalElements': 1, 'items': hotels}
            headers = {'Content-Type': 'application/json'}
            return JSONResponse(content=r_arr, headers=headers, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content=[], status_code=status.HTTP_404_NOT_FOUND)


@app.patch("/api/v1/loyalty/")
def patch_loyalty(request: Request):
    with conn.cursor() as cur:
        user_name = request.headers.get('user_name')
        reservation_count = int(request.headers.get('reservation_count'))
        s_status = request.headers.get('status')
        discount = int(request.headers.get('discount'))

        print('update', user_name, reservation_count)
        cur.execute(
            f'UPDATE loyalty SET '
            f' reservation_count = \'{reservation_count}\', status = \'{s_status}\', discount = \'{discount}\' '
            f'where username= \'{user_name}\''
        )

        return JSONResponse(content=[], status_code=status.HTTP_202_ACCEPTED)


if __name__ == "__main__":

    print(sql_path)
    start_DB()
    uvicorn.run(app, host="0.0.0.0", port=port)

    # uvicorn.run(app, host="localhost", port=port)
