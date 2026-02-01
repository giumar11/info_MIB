/* Declinazione di responsabilità. 
I file rilasciati in formato testo sono provvisti anche dei programmi di importazione per STATA, SAS e R. 
L'Istat non garantisce che le funzioni contenute nei suddetti programmi siano esenti da errore e non si assume alcuna responsabilità sull’output ottenuto dal loro utilizzo.                 */
%macro grabpath;
%qsubstr(%sysget(SAS_EXECFILEPATH),1,%length(%sysget(SAS_EXECFILEPATH))-%length(%sysget(SAS_EXECFILEname)))
%mend grabpath;
%let path = %grabpath;
%let nomeFile =ISTAT_MFR_EHIS_Microdati_2019_ESEMPIO_STRUTTURA_FILE.txt;
LIBNAME ISTAT "&path";
DATA ISTAT.EHIS_A2019;

INFILE "&path&nomeFile" DLM='09'x  LRECL=32767 TRUNCOVER FIRSTOBS=2 IGNOREDOSEOF;
INPUT 
;
LABEL 
;
RUN;
PROC FORMAT;
RUN;
