#Declinazione di responsabilità. 
#I file rilasciati in formato testo sono provvisti anche dei programmi di importazione per STATA, SAS e R. 
#L'Istat non garantisce che le funzioni contenute nei suddetti programmi siano esenti da errore e non si assume alcuna responsabilità sull’output ottenuto dal loro utilizzo.  
setwd(choose.dir(default = "", caption = "WHERE ARE MICRODATA?"))
direttorio = getwd()
fileInput = paste (direttorio, "/ISTAT_MFR_EHIS_Microdati_2019_ESEMPIO_STRUTTURA_FILE.txt", sep="")
DF_EHIS_A2019<- read.delim2 (fileInput,  header=T, sep="	",  quote="",  na.strings = ".")
attr(DF_EHIS_A2019, "label") <- c(
"null")
save.image (file="DF_EHIS_A2019.RData")
