FROM --platform=linux/arm64 arm64v8/alpine:3.17

WORKDIR /app

COPY --chmod=755 server . 
EXPOSE 8080

ENTRYPOINT [ "./server" ]
