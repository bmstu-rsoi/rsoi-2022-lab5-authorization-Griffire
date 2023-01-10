CREATE TABLE payment
(
    id          SERIAL PRIMARY KEY,
    payment_uid uuid        NOT NULL,
    status      VARCHAR(20) NOT NULL
        CHECK (status IN ('PAID', 'CANCELED')),
    price       INT         NOT NULL
);


-- INSERT INTO payment(payment_uid, status, price)
--  VALUES('049161bb-badd-4fa8-9d90-87c9a82b0669', 'PAID', 10000)