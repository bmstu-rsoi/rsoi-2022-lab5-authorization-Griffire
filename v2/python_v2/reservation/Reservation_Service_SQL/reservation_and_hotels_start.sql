CREATE TABLE hotels
(
    id        SERIAL PRIMARY KEY,
    hotel_uid uuid         NOT NULL UNIQUE,
    name      VARCHAR(255) NOT NULL,
    country   VARCHAR(80)  NOT NULL,
    city      VARCHAR(80)  NOT NULL,
    address   VARCHAR(255) NOT NULL,
    stars     INT,
    price     INT          NOT NULL
);


CREATE TABLE reservation
(
    id              SERIAL PRIMARY KEY,
    reservation_uid uuid UNIQUE NOT NULL,
    username        VARCHAR(80) NOT NULL,
    payment_uid     uuid        NOT NULL,
    hotel_id        INT REFERENCES hotels (id),
    status          VARCHAR(20) NOT NULL
        CHECK (status IN ('PAID', 'CANCELED')),
    start_date      TIMESTAMP WITH TIME ZONE,
    end_data        TIMESTAMP WITH TIME ZONE
);



insert into hotels (hotel_uid, name, country, city, address, stars, price) values
('049161bb-badd-4fa8-9d90-87c9a82b0668', 'Ararat Park Hyatt Moscow','Россия','Москва', 'Неглинная ул., 4', 5, 10000)

;


--
-- insert into reservation (reservation_uid, username, payment_uid, hotel_id, status, start_date, end_data) values
-- ('c72858b5-ca07-47cc-9ba9-b0c1fd977839', 'Test Max', '049161bb-badd-4fa8-9d90-87c9a82b0669', 1, 'PAID',  '2011-01-01 00:00:00+09', '2012-01-01 00:00:00+09')
