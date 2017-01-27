compadre2<-read.csv("compadre_migration_2017.csv", header=T)
#1. Add images from EOL
species_accepted<-unique(compadre2$species_accepted)
species<-species_accepted[1:300]
species2<-species_accepted[301:600]
species3<-species_accepted[601:931]
MyEOLs<- DownloadSearchedTaxa(species3, to.file=FALSE)
MyEOLs <- MyEOLs[(names(MyEOLs) != "eolNA")]
df4<-data.frame(species_accepted = rep(NA,length(MyEOLs)), image1 = NA, image2 = NA)
for (i in 1:length(MyEOLs)){
  object <- GatherDataObjectInformation(MyEOLs[i])
  media <- object$mediaURL
  if (is.null(media) == F){
    media <- media[!is.na(media)]
    df4$species[i] <- object$Taxon[1]
    df4$image1[i] <- media[1]
    df4$image2[i] <- media[2]
  }
  cat(paste(" ",i))
}

##rbind the 3 together after, removed code for this
names(df6)[1]<-"image_path"
names(df6)[3]<-"species_accepted"
names(df6)[2]<-"image_path2"
df6$species_accepted<-gsub(" ", "_", df6$species_accepted)
compadre2$species_accepted<-gsub(" ", "_", compadre2$species_accepted)
compadre2$imagecheck<-"noimage"
df6<-df6[!duplicated(df6),]
df<-merge(compadre2, df6, by="species_accepted", all.x =TRUE)

#2. Add IUCN statuses


#6. adjusting date columns so they all match
compadre<-df
head(df$database_date_check)
head(compadre$datbase_date_created)
x<-as.character(df$database_date_created)
levels(x)
compadre$database_date_digitization<-as.Date(df$datbase_date_digitization, "%m.%d.%Y")
compadre$datbase_date_check<-as.Date(df$datbase_date_check, "%m.%d.%Y")
compadre$database_date_created<-as.Date(compadre$database_date_created, "%d.%m.%Y")
compadre$database_date_created<-as.Date(compadre$database_date_created, "%m.%d.%Y")
FINAL$publication_date_author_contacted<-as.Date(FINAL$Contacted, "%d/%m/%Y")
FINAL$publication_date_author_contacted_again<-as.Date(FINAL$Contacted.again, "%d/%m/%Y")

