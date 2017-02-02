#ELAN

ELAN stores its data in XML with the extension EAF.

##Tier structure

Here is an [ELAN template file](https://github.com/langdoc/OUDB/edit/master/ELAN-template.etf) (XML with the extension ETF) including the defined tier hierarchy and the maximal set of tiers for a session with one speaker.

Tier name     | Description                                           | Note
------------- | ------------------------------------------------------| -----------------------
ref@ABC       | for unique reference, time aligned, no parent         | obligatory
code@ABC      | for transcription, symbolically associated to ref     | facultative (only Zsófia, i.e. her coded IPA)
orth@ABC      | for transcription, symbolically associated to ref     | obligatory
word@ABC      | for tokens, symbolically subdivided orth              | ??  
morph@ABC     | for morphemes, symbolically subdivided word           | only for FLEx (and there obligatory)
morph-var@ABC | for allomorphs, symbolically associated to morph      | only for FLEx (and there facultative)
lemma@ABC     | for lemma, symbolically subdivided morph              | only for FLEx (and there obligatory)
gloss@ABC     | for gloss, symbolically associated to morph           | only for FLEx (and there obligatory)
pos@ABC       | for pos, symbolically associated to morph             | only for FLEx (and there obligatory)
ft-rus@ABC    | for free translation, symbolically associated to orth | ??     
ft-hun@ABC    | for free translation, symbolically associated to orth | ?? 
ft-eng@ABC    | for free translation, symbolically associated to orth | ?? 
ft-fin@ABC    | for free translation, symbolically associated to orth | ?? 

### Glossary

* gloss = either English translation of *true* lemma or morphological category labels included in FLEx (for bound morphemes)
* lemma = refers here to the FLEx dictionary entry for both free morphemes (i.e. a true lemma) and bound morphemes (i.e. afixes, clitica, etc.)
* morpheme = referes here to *linear* morphemes listed in the FLEx dictionary
* pos = here "part of morpheme"
* token = word tokens and punctuation marks
* transcription = here in IPA (or Zsófia's pre-coded IPA)

## Multiple speakers

In sessions with multiple speakers, each speaker gets its own set of tiers marked with "@ABC" in the tier name ("ABC" is the speaker name abbreviation, consistent with the speaker metadata. 

## Language attributes

Several tiers (at least orth, word, and the different translations) include data in a specific language, which should be coded in EAF. This is how ELAN stores that kind of language information in EAF:

```
<TIER LANG_REF="kca" LINGUISTIC_TYPE_REF="khanty" TIER_ID="khanty"/>
…
<LANGUAGE LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001" LANG_ID="kca" LANG_LABEL="Khanty (kca)"/>
```
