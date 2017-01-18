df<-read.csv("comadre_migration_2017.csv", header=T)
names(df)
names(df)[82]<-"species_gisd_status"
install.packages("originr")
library(originr)

###Scraping gisd status for each species 

##1. create species list from COMADRE 
sp_list<-unique(df$species_accepted)
sp_list<-gsub("_", " ", sp_list)
#test<-sp_list[1:25]

##2. scrape GISD data
df_inv<-gisd(sp_list, simplify=TRUE)
# df_inv[[1]]$status - how to get the status out of the list
df_invas<- data.frame(species_accepted = rep(NA,length(df_inv)), status = NA)
for(i in 1:length(df_inv)) {
    df_invas$species_accepted[i]<-(df_inv[[i]]$species)
    df_invas$status[i]<-(df_inv[[i]]$status)
  }

##3. convert to TRUE FALSE "Not in GISD"<-FALSE  "Invasive"<-TRUE
df_invas$status<-gsub("Not in GISD", "FALSE", df_invas$status)
df_invas$status<-gsub("Invasive", "TRUE", df_invas$status)
df_invas$species_accepted<-gsub(" ", "_", df_invas$species_accepted)

##4. merge data by species
new<-merge(df, df_invas, by="species_accepted", all.x=T)
new$species_gisd_status<-new$status
new<-new[,-115]
write.csv(new, "comadre_migration_2017.csv")
