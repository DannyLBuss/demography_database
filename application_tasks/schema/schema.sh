#!/bin/bash

system=`uname`
# Checking operating system to install dependencies
if [[ $system == 'Linux' ]]; then
   echo "Checking for and installing graphviz, wget and java - requires sudo"
   sudo apt-get install graphviz
   sudo apt-get install sun-java6-jdk sun-java6-jre
   sudo apt-get install wget
   echo "Setting home variable for Java"
   export JAVA_HOME="/usr/lib/jvm/java-6-sun-1.6.0.06"
elif [[ $system == 'Darwin' ]]; then
   echo "Mac"
fi



# Detect the presence of the relevant jar files. If they don't exist, download them and create symbolic links to this directory.
if [ -f "schemaSpy.jar" ];
then
   echo "schemaSpy found, continuing with schema..."
   echo 
else
   echo "schemaSpy does not exist - wgetting now"
   wget "http://sourceforge.net/projects/schemaspy/files/schemaspy/SchemaSpy%205.0.0/schemaSpy_5.0.0.jar/download" -O ../../requirements/non_python/schemaSpy.jar
   echo "////////////////"
   echo "Creating symlink to folder"
   ln -s ../../requirements/non_python/schemaSpy.jar schemaSpy.jar >&2
fi

if [ -f "mysql-connector-java-5.1.40-bin.jar" ];
then
   echo "MySQL Java Connector found, continuing with schema..."
else
   echo "MySQL Java Connector does not exist - wgetting now"
   wget "https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.40.zip" -O ../../requirements/non_python/mysql-connector-java-5.1.40.zip
   unzip ../../requirements/non_python/mysql-connector-java-5.1.40.zip -d ../../requirements/non_python/mysql-connector-java-5.1.40
   ln -s ../../requirements/non_python/mysql-connector-java-5.1.40/mysql-connector-java-5.1.40/mysql-connector-java-5.1.40-bin.jar mysql-connector-java-5.1.40-bin.jar >&2
fi

# New outputs will be in 'current', old ones will be archived with the current date and a timestamp
if [ -d "current" ]; then
	echo "Moving current schema to archive $(date +"%m_%d_%Y_%s") - requires sudo"
	sudo mv current $(date +"%m_%d_%Y_%s")
fi

echo "Executing schemaSpy on the database..."


read -p 'Database Name: ' dbname
read -p 'Host (ie Localhost): ' host
read -p 'Username: ' username
read -sp 'Password: ' password

sudo java -jar schemaSpy.jar -t mysql -db $dbname -host $host -u $username -p $password -o current -dp mysql-connector-java-5.1.40-bin.jar

# Clean the files