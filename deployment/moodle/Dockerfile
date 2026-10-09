FROM php:8.3-apache
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev libicu-dev libzip-dev libpng-dev libjpeg62-turbo-dev libfreetype6-dev libxml2-dev libonig-dev libcurl4-openssl-dev \
 && docker-php-ext-configure gd --with-freetype --with-jpeg \
 && docker-php-ext-install pgsql intl zip gd soap opcache mbstring curl exif \
 && rm -rf /var/lib/apt/lists/*
RUN printf 'max_input_vars=5000\nupload_max_filesize=100M\npost_max_size=100M\n' > /usr/local/etc/php/conf.d/moodle.ini
COPY vendor/moodle/ /var/www/html/
COPY deployment/moodle/start.sh /usr/local/bin/start-moodle
RUN chmod +x /usr/local/bin/start-moodle && mkdir -p /var/moodledata && chown -R www-data:www-data /var/moodledata /var/www/html
ENTRYPOINT ["start-moodle"]
