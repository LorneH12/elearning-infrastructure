#!/bin/sh
set -eu
if [ ! -f /var/www/html/config.php ]; then
  php /var/www/html/admin/cli/install.php --non-interactive --agree-license \
    --wwwroot=http://localhost:8080 --dataroot=/var/moodledata \
    --dbtype=pgsql --dbhost=moodle-db --dbname=moodle --dbuser=moodle --dbpass="$MOODLE_DB_PASSWORD" \
    --fullname='Portfolio Learning Lab' --shortname='Learning Lab' \
    --adminuser=labadmin --adminpass="$MOODLE_ADMIN_PASSWORD" --adminemail=labadmin@example.org
  chown www-data:www-data /var/www/html/config.php
  chmod 640 /var/www/html/config.php
fi
exec apache2-foreground
