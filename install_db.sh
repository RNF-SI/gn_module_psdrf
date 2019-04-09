#!/bin/bash

. ./config/settings.ini


if [ ! -d 'var' ]
then
  mkdir var
fi

if [ ! -d 'var/log' ]
then
  mkdir var/log
fi


echo "Creating CMR schema..." &> var/log/install_db.log
echo "--------------------" &> var/log/install_db.log
cp data/psdrf.sql /tmp/psdrf.sql
sudo sed -i "s/MYLOCALSRID/$srid_local/g" /tmp/psdrf.sql


export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f /tmp/psdrf.sql  &>> var/log/install_db.log
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f data/psdrf_data.sql  &>> var/log/install_db.log


sudo rm /tmp/psdrf.sql

echo "... Installation terminée"