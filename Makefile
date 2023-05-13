APP_NAME:=trellinho-api

all: build run

build:
	docker build . -t $(APP_NAME)

run:
	docker run -it --rm -p 8080:8080 $(APP_NAME)
