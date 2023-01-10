import datetime
import os
import sys
import uuid
from dataclasses import dataclass
from json import JSONEncoder

import jwt
import requests as http_req
import uvicorn
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

app = FastAPI()

sql_path = os.path.dirname(__file__)

port = 8080



@dataclass
class PostHotelReserve:
    hotelUid: str
    startDate: datetime.date
    endDate: datetime.date


class MyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


JWT_WELLKNOWN = 'https://dev-c0acsqpvgx5g1phe.us.auth0.com/.well-known/jwks.json'

jwks_client = jwt.PyJWKClient(JWT_WELLKNOWN)


def token_parse(token: str):
    jwks_client = jwt.PyJWKClient(JWT_WELLKNOWN)
    # print(jwks_client)
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    print("key")
    # print(signing_key.key)
    data = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience="https://lab5griffv1api",
        options={"verify_signature": False}
    )
    print(data)
    print(data, file=sys.stderr)
    return data
    # return None


def get_token(request: Request):
    headers = request.headers
    print(headers)
    bearer = headers.get('authorization')
    print('bearer')
    print(bearer)
    # _token_parse(bearer.split()[1])
    data = None
    try:
        data = token_parse(bearer.split()[1])
    except:
        data = None
    print('data')
    print(data)
    return data



def auth_name(request: Request):
    data = get_token(request)
    print("___NAME___")
    # print(data.get('https://example.com/name'))
    if data is None:
        return None
    return data.get('https://example.com/name')


@app.get("/manage/health")
def get_hotels_page():
    headers = {'Content-Type': 'application/json'}
    return JSONResponse(content="Host localhost:8080 is active", headers=headers, status_code=status.HTTP_200_OK)


@app.get("/api/v1/hotels")
def get_hotels_page(page: int, size: int, req: Request):
    data = get_token(req)
    if data is None:
        msg = 'Get authorized please'
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=msg, headers=headers, status_code=status.HTTP_401_UNAUTHORIZED)

    inp_post_response = http_req.get('http://reservation:8070/api/v1/hotels/')
    hotel_row = inp_post_response.json()
    headers = {'Content-Type': 'application/json'}
    hotel_res = {'page': 1, 'pageSize': 1, 'totalElements': len(hotel_row), 'items': hotel_row}
    return JSONResponse(content=hotel_res, headers=headers, status_code=status.HTTP_200_OK)


@app.post("/api/v1/reservations")
def post_reservations(request: Request, item: PostHotelReserve):
    # username_from_header = request.headers.get('X-User-Name')
    username_from_header = auth_name(request)
    if username_from_header is None:
        msg = 'Get authorized please'
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=msg, headers=headers, status_code=status.HTTP_401_UNAUTHORIZED)

    if username_from_header is not None:
        inp_post_response = http_req.get('http://reservation:8070/api/v1/hotels/', headers={"hotelUid": item.hotelUid})
        if inp_post_response.status_code != 404:
            hotel_row = inp_post_response.json()
            if len(hotel_row) > 0:
                hotel = hotel_row[0]
                nights = (item.endDate - item.startDate).days
                price = nights * hotel['price']
                inp_post_response = http_req.get('http://loyalty:8050/api/v1/loyalty/',
                                                 headers={"user_name": username_from_header})
                if inp_post_response.status_code != 404:
                    loyalty_row = inp_post_response.json()
                    if len(loyalty_row) > 0:
                        loyalty = loyalty_row[0]
                        discount = loyalty['discount']
                        price = int(price * (1 - discount * 0.01))
                    else:
                        discount = ''

                    paymentUid = str(uuid.uuid4())
                    http_req.post('http://payment:8060/api/v1/payments/',
                                  headers={'paymentUid': paymentUid, "price": str(price), 'status': 'PAID'})
                    inp_post_response = http_req.get('http://payment:8060/api/v1/payments/',
                                                     headers={"payment_uid": paymentUid})
                    if inp_post_response.status_code != 404:
                        payment_elem = inp_post_response.json()
                        hotel['payment'] = payment_elem[0]
                        hotel['discount'] = discount
                        hotel['status'] = 'PAID'

                    reservationUid = str(uuid.uuid4())
                    req = http_req.post('http://reservation:8070/api/v1/reservations/',
                                        headers={'reservation_uid': reservationUid, "username": username_from_header,
                                                 'payment_uid': paymentUid, 'hotel_id': str(hotel['id']),
                                                 'status': 'PAID',
                                                 'start_date': str(item.startDate), 'end_data': str(item.endDate)})

                    if req.status_code == 201:
                        # print("ny i che tut???????")
                        hotel['reservationUid'] = reservationUid
                        hotel['startDate'] = str(item.startDate)
                        hotel['endDate'] = str(item.endDate)

                        loyalty['reservationCount'] = loyalty['reservationCount'] + 1
                        print(loyalty['reservationCount'])
                        if loyalty['reservationCount'] >= 10:
                            loyalty['status'] = 'SILVER'
                            loyalty['discount'] = 7
                            if loyalty['reservationCount'] >= 20:
                                loyalty['status'] = 'GOLD'
                                loyalty['discount'] = 10

                        req = http_req.patch('http://loyalty:8050/api/v1/loyalty/', headers={
                            'user_name': username_from_header, 'reservation_count': str(loyalty['reservationCount']),
                            'status': loyalty['status'], 'discount': str(loyalty['discount']),
                        })
                        print(req.status_code)


                    print(nights, price)
                    headers = {'Content-Type': 'application/json'}
                    return JSONResponse(content=hotel, headers=headers, status_code=status.HTTP_200_OK)


@app.get("/api/v1/me")
def get_me(request: Request):
    # username_from_header = request.headers.get('X-User-Name')

    username_from_header = auth_name(request)
    print(get_token(request))
    if username_from_header is None:
        msg = 'Get authorized please'
        headers = {'Content-Type': 'application/json'}
        return  JSONResponse(content=msg, headers=headers, status_code=status.HTTP_401_UNAUTHORIZED)

    if username_from_header is not None:
        info = {}
        print(username_from_header)
        inp_post_response = http_req.get('http://loyalty:8050/api/v1/loyalty/',
                                         headers={"user_name": username_from_header})
        if inp_post_response.status_code != 404:
            loyalty = inp_post_response.json()[0]
            info['loyalty'] = loyalty

        inp_post_response = http_req.get('http://reservation:8070/api/v1/reservations/',
                                         headers={"user_name": username_from_header})
        if inp_post_response.status_code != 404:
            reservations = inp_post_response.json()
            for r in reservations:
                inp_post_response = http_req.get('http://reservation:8070/api/v1/hotels/',
                                                 headers={"hotel_id": str(r['hotel_id'])})
                hotel = inp_post_response.json()
                hotel[0]['fullAddress'] = hotel[0]['country'] + ', ' + hotel[0]['city'] + ', ' + hotel[0]['address']

                r['hotel'] = hotel[0]

                print('pay', r['payment_uid'])
                inp_post_response = http_req.get('http://payment:8060/api/v1/payments/',
                                                 headers={"payment_uid": r['payment_uid']})
                payment = inp_post_response.json()
                r['payment'] = payment[0]
            info['reservations'] = reservations

        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=info, headers=headers, status_code=status.HTTP_200_OK)


@app.get("/api/v1/reservations")
def get_reservations(request: Request):
    print('nachali')
    # username_from_header = request.headers.get('X-User-Name')
    username_from_header = auth_name(request)
    if username_from_header is None:
        msg = 'Get authorized please'
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=msg, headers=headers, status_code=status.HTTP_401_UNAUTHORIZED)


    if username_from_header is not None:
        print('nachali2')
        print(username_from_header)
        inp_post_response = http_req.get('http://reservation:8070/api/v1/reservations/',
                                         headers={'user_name': username_from_header})
        print('nachali3')
        if inp_post_response.status_code != 404:
            print(inp_post_response)
            reservations_row = inp_post_response.json()
            print(reservations_row)
            for i in reservations_row:
                inp_post_response = http_req.get('http://reservation:8070/api/v1/hotels/',
                                                 headers={"hotel_id": str(i['hotel_id'])})
                hotel_row = inp_post_response.json()
                hotel_row[0]['fullAddress'] = hotel_row[0]['country'] + ', ' + hotel_row[0]['city'] + ', ' + \
                                              hotel_row[0]['address']
                print(i['hotel_id'])

                payment_uid = i['payment_uid']
                inp_post_response = http_req.get('http://payment:8060/api/v1/payments/',
                                                 headers={"paymentUid": payment_uid})
                payment_row = inp_post_response.json()
                print(payment_row)
                i['hotel'] = hotel_row[0]
                i['payment'] = payment_row[0]

            print(reservations_row)
            headers = {'Content-Type': 'application/json'}
            #

            return JSONResponse(content=reservations_row, headers=headers, status_code=status.HTTP_200_OK)

            # print(inp_post_response.json())



        else:
            print('4040404040404040404')


@app.get("/api/v1/loyalty")
def get_loyalty(request: Request):
    # username_from_header = request.headers.get('X-User-Name')
    username_from_header = auth_name(request)
    if username_from_header is None:
        msg = 'Get authorized please'
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=msg, headers=headers, status_code=status.HTTP_401_UNAUTHORIZED)

    if username_from_header is not None:
        inp_post_response = http_req.get('http://loyalty:8050/api/v1/loyalty/',
                                         headers={"user_name": username_from_header})
        if inp_post_response.status_code != 404:
            loyalty_row = inp_post_response.json()
            headers = {'Content-Type': 'application/json'}
            return JSONResponse(content=loyalty_row[0], headers=headers, status_code=status.HTTP_200_OK)


@app.get("/api/v1/reservations/{reservationUid}")
def get_reservation(request: Request, reservationUid: str):
    print('nachali')
    # username_from_header = request.headers.get('X-User-Name')
    username_from_header = auth_name(request)
    if username_from_header is None:
        msg = 'Get authorized please'
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=msg, headers=headers, status_code=status.HTTP_401_UNAUTHORIZED)

    if username_from_header is not None:
        print('nachali2')
        print(username_from_header)
        inp_post_response = http_req.get('http://reservation:8070/api/v1/reservations/',
                                         headers={'reservationUid': reservationUid})
        print('nachali3')
        if inp_post_response.status_code != 404:
            print(inp_post_response)
            reservations_row = inp_post_response.json()
            print(reservations_row)
            for i in reservations_row:
                inp_post_response = http_req.get('http://reservation:8070/api/v1/hotels/',
                                                 headers={"hotel_id": str(i['hotel_id'])})
                hotel_row = inp_post_response.json()
                hotel_row[0]['fullAddress'] = hotel_row[0]['country'] + ', ' + hotel_row[0]['city'] + ', ' + \
                                              hotel_row[0]['address']
                print(i['hotel_id'])

                payment_uid = i['payment_uid']
                inp_post_response = http_req.get('http://payment:8060/api/v1/payments/',
                                                 headers={"payment_uid": payment_uid})
                payment_row = inp_post_response.json()
                print(payment_row)
                i['hotel'] = hotel_row[0]
                i['payment'] = payment_row[0]

            print(reservations_row)
            headers = {'Content-Type': 'application/json'}

            return JSONResponse(content=reservations_row[0], headers=headers, status_code=status.HTTP_200_OK)


@app.delete("/api/v1/reservations/{reservationUid}")
def get_reservation(request: Request, reservationUid: str):
    print('nachali delete')
    # username_from_header = request.headers.get('X-User-Name')
    username_from_header = auth_name(request)
    if username_from_header is None:
        msg = 'Get authorized please'
        headers = {'Content-Type': 'application/json'}
        return JSONResponse(content=msg, headers=headers, status_code=status.HTTP_401_UNAUTHORIZED)

    if username_from_header is not None:
        print('nachali2')
        print(username_from_header)
        inp_post_response = http_req.get('http://reservation:8070/api/v1/reservations/',
                                         headers={'reservationUid': reservationUid})
        print('nachali3')
        if inp_post_response.status_code != 404:
            print(inp_post_response)
            reservations_row = inp_post_response.json()
            reservation = reservations_row[0]
            payment_uid = reservation['payment_uid']
            http_req.delete('http://payment:8060/api/v1/payments/delete', headers={"paymentUid": payment_uid})
            http_req.delete('http://reservation:8070/api/v1/reservations/', headers={"reservationUid": reservationUid})

            reservation['status'] = 'CANCELED'

            inp_post_response = http_req.get('http://loyalty:8050/api/v1/loyalty/',
                                             headers={"user_name": username_from_header})
            loyalty = inp_post_response.json()[0]
            print(loyalty)

            #
            loyalty['reservationCount'] = loyalty['reservationCount'] - 1
            print(loyalty['reservationCount'])
            loyalty['status'] = 'BRONZE'
            loyalty['discount'] = 5
            if loyalty['reservationCount'] >= 10:
                loyalty['status'] = 'SILVER'
                loyalty['discount'] = 7
                if loyalty['reservationCount'] >= 20:
                    loyalty['status'] = 'GOLD'
                    loyalty['discount'] = 10
            #
            req = http_req.patch('http://loyalty:8050/api/v1/loyalty/', headers={
                'user_name': username_from_header, 'reservation_count': str(loyalty['reservationCount']),
                'status': loyalty['status'], 'discount': str(loyalty['discount']),
            })

            headers = {'Content-Type': 'application/json'}
            return JSONResponse(content=reservation, headers=headers, status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=port)

