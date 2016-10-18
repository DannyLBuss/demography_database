#!/bin/bash
if [ -f "demography_database.sql" ];
then
	echo "Archiving old SQL dump to archives/$(date +"%m_%d_%Y_%s").sql"
	mv demography_database.sql archives/$(date +"%m_%d_%Y_%s").sql
	echo
fi

read -p 'Username: ' usern
read -sp 'Password: ' passwd

echo "Creating SQL dump of entire database, including structure"
mysqldump demog_compadre > demography_database.sql -u $usern -p$passwd