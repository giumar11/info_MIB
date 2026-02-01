/* #Declinazione di responsabilità. 
#I file rilasciati in formato testo sono provvisti anche dei programmi di importazione per STATA, SAS e R. 
#L'Istat non garantisce che le funzioni contenute nei suddetti programmi siano esenti da errore e non si assume alcuna responsabilità sull’output ottenuto dal loro utilizzo.       */
/*  I valori delle label nelle variabili categoriche sono commentati a causa della presenza di codici non esclusivamente numerici. Comunque sono completamente documentati.  */
clear all
infile  using  PGM_2019_IT_DELIMITED.dct, clear
/*
*/
save  EHIS_A2019.dta, replace
