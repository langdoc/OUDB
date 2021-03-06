#Notes

This file is for preliminary notes, as well as links to available tools or other types of relevant documentations.

## FLEx-to-ELAN interaction
* a paper on the topic: http://www.academia.edu/24857244/Elan_Flex_Fieldworks_language_explorer_workflow
* webpage on the topic: http://www.philol.msu.ru/~languedoc/eng/help/flex2eaf.php
* relevant page from the ELAN manual: http://www.mpi.nl/corpus/html/elan/ch01s04s02.html#Sec_Importing_a_document_from_Fieldworks_Language_Explorer_FLEx
* EAF-Schema:
  http://www.mpi.nl/tools/elan/EAF_Annotation_Format_3.0_and_ELAN.pdf
* how to upload CMDI via Lamus (& especially what kind of CMDI template you need --> lat-session):
https://tla.mpi.nl/wp-content/uploads/2012/09/Migration-CMDI_archiving-workflow.pdf
* CMDI templates: lat-corpus & lat-session:
https://catalog.clarin.eu/ds/ComponentRegistry/#/?itemId=clarin.eu:cr1:p_1407745712064&_k=rgocqj
* FAQ CMDI
https://www.clarin.eu/content/faq-metadata
* how to CMDI
https://infra.clarin.eu/cmd/doc/howto.html
* Md-Schema (you need this for a Lamus friendly CMDI):
https://infra.clarin.eu/cmd/example/example-md-schema.xsd

We will create two different types of ELAN files:

1. ELAN files without linked audio
  * a) they come from FLEx
  * b) they come from the transcription files without annotations
2. ELAN files with linked audio
  * a) they come from Zsófia's transcribed recordings and have also related FLEx annotations
  * b) they come from a few other, old recordings and have also related FLEx annotations

### 1a)
FLEx-to-ELAN script needed, time alignment in ELAN not needed

### 1b)
1. restructure the text file
2. import into ELAN, time alignment not needed

### 2a)
FLEx-to-ELAN script needed, merging with original time alignment in existing ELAN files needed

### 2b)
FLEx-to-ELAN script needed, new time alignment in ELAN needed
