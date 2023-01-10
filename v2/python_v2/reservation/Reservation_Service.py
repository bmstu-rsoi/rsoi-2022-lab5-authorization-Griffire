import datetime
import os
from dataclasses import dataclass

import uvicorn
import psycopg2
from fastapi import FastAPI
from fastapi.responses import JSONResponse, Response
from fastapi import FastAPI, status, Body, Header
from fastapi.requests import Request


app = FastAPI()

port = 8070
conn = psycopg2.connect(dbname="postgres", user="program", password="test", host="postgres-service", port="5432")
# conn = psycopg2.connect(dbname="postgres", user="program", password="test", host="postgres", port="5432")


sql_path = os.path.dirname(__file__)


def start_DB():
    print('starting')

    print('____')
    f_reservation_and_hotels_start = open(sql_path + '/Reservation_Service_SQL/reservation_and_hotels_start.sql', 'r')
    sqlFile_reservation_and_hotels_start = f_reservation_and_hotels_start.read()
    f_reservation_and_hotels_start.close()

    print('_____')
    f_reservation_and_hotels_stop = open(sql_path + '/Reservation_Service_SQL/reservation_and_hotels_stop.sql', 'r')
    sqlFile_reservation_and_hotels_stop = f_reservation_and_hotels_stop.read()
    f_reservation_and_hotels_stop.close()

    with conn.cursor() as cur:
        cur.execute(sqlFile_reservation_and_hotels_stop)
        cur.execute(sqlFile_reservation_and_hotels_start)
        conn.commit()

@app.get("/manage/health")
def get_hotels_page():
    headers = {'Content-Type': 'application/json'}
    return JSONResponse(content="Host localhost:8070 is active", headers=headers, status_code=status.HTTP_200_OK)


@app.get("/api/v1/check")
def get_hotels_page():
    with conn.cursor() as cur:
        print("8070 is alive")
        data = {'all': 'ok_8070'}
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=data, headers=headers, status_code=status.HTTP_200_OK)


@dataclass
class Hotel:
    id: int
    hotelUid: str
    name: str
    country: str
    city: int
    address: str
    stars: int
    price: int

@dataclass
class Reservation:
    id: int
    reservationUid: str
    username: str
    payment_uid: str
    hotel_id: int
    status: str
    startDate: str
    endDate: str





@app.get("/api/v1/hotels/")
def get_hotels(request: Request):
    with conn.cursor() as cur:
        hotel_id_s = request.headers.get('hotel_id')
        hotelUid = request.headers.get('hotelUid')
        # print(hotel_id)
        if hotelUid is not None:
            print('uid is on')
            cur.execute(
                f'Select * from hotels where hotel_uid=\'{hotelUid}\' '
            )
        elif hotel_id_s is not None:
            hotel_id = int(hotel_id_s)
            print('id is in')
            cur.execute(
                f'Select * from hotels where id=\'{hotel_id}\' '
            )
        else:
            print('id is off')
            cur.execute(
                f'Select * from hotels'
            )
        hotels_row = cur.fetchall()
        if len(hotels_row) > 0:
            print(hotels_row)
            r = [Hotel(*hotels_row[i]) for i in range(len(hotels_row))] if hotels_row else None
            r_arr = []
            for i in r:
                hotel = {}
                print("________")
                for j in i.__dict__.items():
                    hotel[j[0]] = j[1]
                r_arr.append(hotel)
            headers = {'Content-Type': 'application/json'}
            return JSONResponse(content=r_arr, headers=headers, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content=[], status_code=status.HTTP_404_NOT_FOUND)


@app.get("/api/v1/reservations/")
def get_reservations(request: Request):
    with conn.cursor() as cur:
        print('op1')
        user_name = request.headers.get('user_name')
        reservationUid = request.headers.get('reservationUid')

        print(user_name,reservationUid )
        if reservationUid is not None:
            cur.execute(
                f'Select * from reservation where reservation_uid= \'{reservationUid}\''
            )
        else:
            cur.execute(
                f'Select * from reservation where username= \'{user_name}\''
            )
        reservations_row = cur.fetchall()
        print('row::::', reservations_row)
        if len(reservations_row) > 0:
            print(reservations_row)
            r = [Reservation(*reservations_row[i]) for i in range(len(reservations_row))] if reservations_row else None
            r_arr = []
            for i in r:
                reservation = {}
                print("________")
                for j in i.__dict__.items():
                    if type(j[1]) is not int:
                        if type(j[1]) is datetime.datetime:
                            reservation[j[0]] = str(j[1].date())
                        else:
                            reservation[j[0]] = str(j[1])
                    else:
                        reservation[j[0]] = j[1]

                r_arr.append(reservation)
            headers = {'Content-Type': 'application/json'}
            print(r_arr)
            return JSONResponse(content=r_arr, headers=headers, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content=[], status_code=status.HTTP_404_NOT_FOUND)


@app.post("/api/v1/reservations/")
def post_reservations(request: Request):
    with conn.cursor() as cur:
        reservation_uid = request.headers.get('reservation_uid')
        username = request.headers.get('username')
        payment_uid = request.headers.get('payment_uid')
        hotel_id = int(request.headers.get('hotel_id'))
        s_status = request.headers.get('status')
        start_date = request.headers.get('start_date')
        end_data = request.headers.get('end_data')

        cur.execute(
            f'INSERT INTO  reservation(reservation_uid, username, payment_uid, hotel_id, status, start_date, end_data) '
            f' values(\'{reservation_uid}\', \'{username}\' , \'{payment_uid}\' , \'{hotel_id}\', '
            f' \'{s_status}\', \'{start_date}\' , \'{end_data}\' )'
        )
        return JSONResponse(content=[], status_code=status.HTTP_201_CREATED)


@app.delete("/api/v1/reservations/")
def post_reservations(request: Request):
    with conn.cursor() as cur:
        reservation_uid = request.headers.get('reservationUid')

        cur.execute(
            f'UPDATE reservation SET '
            f' status = \'CANCELED\' '
            f' where reservation_uid = \'{reservation_uid}\' '
        )
        return JSONResponse(content=[], status_code=status.HTTP_201_CREATED)



if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=port)

    print(sql_path)
    start_DB()
    uvicorn.run(app, host="0.0.0.0", port=port)

    # uvicorn.run(app, host="localhost", port=port)
