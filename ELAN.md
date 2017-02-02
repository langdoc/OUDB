#ELAN

ELAN stores its data in XML with the extension EAF.

##Tier structure

Here is an [ELAN template file](https://github.com/langdoc/OUDB/edit/master/ELAN-template.etf) (XML with the extension ETF) including the defined tier hierarchy and the maximal set of tiers for a session with one speaker.

Tier name | Description                                       | Note
--------- | ------------------------------------------------- | -----------------------
ref@ABC   | for unique reference, time aligned, no parent     | obligatory
code@ABC  | for transcription, symbolically associated to ref | only Zsófia (coded IPA)
orth@ABC  | for transcription, symbolically associated to ref | obligatory

## Multiple speakers

In sessions with multiple speakers, each speaker gets its own set of tiers marked with "@ABC" in the tier name ("ABC" is the speaker name abbreviation, consistent with the speaker metadata. 

## Language attributes

This is how ELAN stores that kind of language information in EAF:

```
<TIER LANG_REF="kca" LINGUISTIC_TYPE_REF="khanty" TIER_ID="khanty"/>
…
<LANGUAGE LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001" LANG_ID="kca" LANG_LABEL="Khanty (kca)"/>
```
