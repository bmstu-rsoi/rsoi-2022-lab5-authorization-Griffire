# syntax=docker/dockerfile:1
FROM golang:1.16.9
COPY src/ /app/

WORKDIR /app
Run go env -w GO111MODULE=off
Run go get github.com/go-chi/chi github.com/go-chi/render github.com/lib/pq
Run go get gitlab.com/idoko/bucketeer/db
Run go get gitlab.com/idoko/bucketeer/models
Run go get github.com/go-chi/chi


CMD ["go", "run" , "/app/main.go", "/app/test.go",  "/app/models.go", "/app/persons.go", "/app/handlerALL.go",  "/app/errors.go" , "/app/db.go" ]