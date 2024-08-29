FROM nginx:mainline-alpine

RUN apk update && apk add --no-cache openssl

RUN rm /etc/nginx/conf.d/default.conf
COPY conf/nginx.conf /etc/nginx/nginx.conf
COPY tools ./tools

RUN chmod +x tools/setup.sh

RUN mkdir -p /usr/share/nginx/html/profile_photos

ENTRYPOINT ["./tools/setup.sh"]