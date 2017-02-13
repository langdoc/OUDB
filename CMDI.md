This is the start of a file documenting our Metadata (CMDI) structure.

#CMDI

##Validator
Link to a [CMDI validator tool](https://nexus.clarin.eu/service/local/repositories/Clarin/content/eu/clarin/cmdi/cmdi-validator-tool/1.0.0/cmdi-validator-tool-1.0.0.jar)

##Other
how to create cmdi using arbil: (https://www.clarin.eu/faq/how-do-i-create-new-cmdi-metadata-file) - using imdi-session-profile


##OUDB-Metadata


###MD
CMDI key | DB value | example value
------------ | ------------- | -------------
Name | dialect-KUERZEL.'_'.id_text | YK_1523
Title | title_vernacular | iːttən əntə nɛripti (AJM)
Date | rec_date / 'Unspecified' | 2015
Genre | genre_content | Tales (tal)
Continent | 'Asia' | 
Continent | 'Russian Federation' | 
Project | 'OUDB' | 


###Content_Language
CMDI key | DB value | example value
------------ | ------------- | -------------
Id | dialect-GROUP-ISO | ISO639-3:kca
Name | dialect-GROUP-NAME | Khanty

###Content_Language>descriptions
CMDI key | DB value | example value
------------ | ------------- | -------------
Description | dialect | yugan khanty (YK)

###Actor:Collector
CMDI key | DB value | example value
------------ | ------------- | -------------
Name | collector | Kayukova & Schön (AZ)
Age | 'Unspecified' | 
BirthDate | 'Unspecified' | 
Sex | 'Unspecified' | 
Anonymized | 'Unspecified' | 


###Actor:Speaker/Signer (optional, repeated)
CMDI key | DB value | example value
------------ | ------------- | -------------
Name | informant-ABKUERZUNG (LISTE ZSÓFI + generiert von Ira) | OAL
Age | 'Unspecified' | 
BirthDate | 'Unspecified' | 
Sex | 'Unspecified' | 
Anonymized | 'Unspecified' | 
