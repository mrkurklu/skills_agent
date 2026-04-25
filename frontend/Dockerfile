FROM nginx:alpine

# Nginx'in varsayılan 80 portunu 3000'e çeviriyoruz
RUN sed -i 's/listen  *80;/listen 3000;/g' /etc/nginx/conf.d/default.conf

COPY index.html /usr/share/nginx/html/index.html

EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]