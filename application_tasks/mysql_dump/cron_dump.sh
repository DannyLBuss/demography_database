#!/bin/bash
PATH_TO_CURRENT_DB="/Users/daniellebuss/Sites/demography_database/application_tasks/mysql_dump/"
CURRENT_SQL_DB_NAME="demography_database.sql"
DIRECTORY="/Users/daniellebuss/Sites/demography_database/alchemydumps/"

# Because this will be chroned, it cant promt the user for a 
# username and password as there isnt one.
# I suppose, you need a admin style account who can perform the sql dump, and dump
# everything. 
#ADMIN_USERNAME=read -p 'Username: ' usern
#ADMIN_PASSWORD=read -sp 'Password: ' passwd

# check that a new database is present, if so move it to archive
if [ -f $PATH_TO_CURRENT_DB$CURRENT_SQL_DB_NAME ]; then
  cp $PATH_TO_CURRENT_DB$CURRENT_SQL_DB_NAME  $DIRECTORY$(date +"%m_%d_%Y_%s").sql
fi

# reset the new current sql data base
# mysqldump demog_compadre > $CURRENT_SQL_DB_NAME $ADMIN_USERNAME -p $ADMIN_PASSWORD


#chrontab -e chrontab.txt

