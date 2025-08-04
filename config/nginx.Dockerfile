FROM nginx:1.21.1-alpine

COPY /config/nginx.conf /etc/nginx/conf.d
