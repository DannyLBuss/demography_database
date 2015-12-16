#!/bin/bash
clear
echo "Migrating to new version of the database"
echo "Moving current folder to dated, archived folder"
mv schema/ schema_archives/`date +%Y%m%d`/
echo "Moved to schema_archives/"
echo "Running .jar script to create new schema"
java -jar schema.jar -t mysql -db demog_compadre -dp mysql-connector-java-5.1.38-bin.jar -host localhost -port 1433 -u root -p jeh5t -o schema 
echo "Complete!"
