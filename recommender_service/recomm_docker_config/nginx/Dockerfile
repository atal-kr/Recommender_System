FROM nginx
RUN chmod +x /etc/nginx
COPY nginx_recommender_service.conf /etc/nginx/conf.d
RUN apt-get update
RUN apt install nano
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log
RUN rm -f /etc/nginx/conf.d/default.conf
EXPOSE "80"
CMD ["nginx", "-g", "daemon off;"]