FROM nginx:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY src/nginx/nginx.conf /etc/nginx/conf.d

WORKDIR /usr/share/nginx/html

COPY src/. .

RUN chmod +x run.sh

EXPOSE 80

CMD ["./run.sh"]