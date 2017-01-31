compadre<-read.csv("compadre_migration_2017.csv", header=T)
names(compadre)
head(compadre$database_date_created)
compadre$database_date_created<-as.Date(compadre$database_date_created, "%m/%d/%Y")
compadre$database_date_created<-as.POSIXct(compadre$database_date_created)
compadre$database_date_created<-format(as.Date(compadre$database_date_created), "%d/%m/%Y")
head(compadre$database_date_created)

head(compadre$database_date_check)
compadre$database_date_check<-as.Date(compadre$database_date_check, "%m/%d/%Y")
compadre$database_date_check<-as.POSIXct(compadre$database_date_check)
compadre$database_date_check<-format(as.Date(compadre$database_date_check), "%d/%m/%Y")
head(compadre$database_date_check)

head(compadre$date_author_contacted)
compadre$date_author_contacted<-as.Date(compadre$date_author_contacted, "%m/%d/%Y")
compadre$date_author_contacted<-as.POSIXct(compadre$date_author_contacted)
compadre$date_author_contacted<-format(as.Date(compadre$date_author_contacted), "%d/%m/%Y")
head(compadre$date_author_contacted)

head(compadre$date_author_contacted_again)
compadre$date_author_contacted_again<-as.Date(compadre$date_author_contacted_again, "%m/%d/%Y")
compadre$date_author_contacted_again<-as.POSIXct(compadre$date_author_contacted_again)
compadre$date_author_contacted_again<-format(as.Date(compadre$date_author_contacted_again), "%d/%m/%Y")
head(compadre$date_author_contacted_again)

publication_date_digitization
head(compadre$publication_date_digitization)
compadre$publication_date_digitization<-as.Date(compadre$publication_date_digitization, "%m/%d/%Y")
compadre$publication_date_digitization<-as.POSIXct(compadre$publication_date_digitization)
compadre$publication_date_digitization<-format(as.Date(compadre$publication_date_digitization), "%d/%m/%Y")
head(compadre$publication_date_digitization)

write.csv(compadre, "compadre_migration_2017.csv")
