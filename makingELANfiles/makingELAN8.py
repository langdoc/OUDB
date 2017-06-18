# -*- coding: utf-8 -*-
from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
#Verbindung zur Datenbank
import pymysql
from pymysql import connect, err, sys, cursors
#f�r Datum
import datetime
import pytz #timzone
import re
from ZugangsdatenDB import getZugangsdaten

#zum Testen von flex only + flex audio

hostname, portname, username, passwdname, dbname = getZugangsdaten()

#Verbindung zur DB aufbauen
dbObj = pymysql.connect(host = hostname, port = portname, user = username, passwd = passwdname, db = dbname, charset='utf8')
cursor = dbObj.cursor()

#alle benoetigten Texte holen
cursor.execute('Select id_text, dialect, public_glossed from documents_info where public = 1')
listDocInfo = list(cursor)

#Texte mit audio
cursor.execute("Select DISTINCT id_text from elan_data where elan_speaker = 'default' and nr_wav_file = 1")
audios = list(cursor)
audiosList = []
for elem in audios:
    audiosList.append(elem[0])

for singleText in listDocInfo:
    if singleText[0] == 728:
        idText = singleText[0]
        dialect = singleText[1]
        flex = singleText[2]
        nameAbbreviation = dialect[-3:-1]
        filenameElan = nameAbbreviation + '_'+str(idText)+ '.eaf'
        if dialect[-2] == 'K' or dialect[-2] == 'A':
            langRef = 'kca'
        if dialect[-2] == 'M' or dialect[-2] == 'V':
            langRef = 'mns'
            #XML aufbauen
        root = Element('ANNOTATION_DOCUMENT', AUTHOR='', DATE=datetime.datetime.now(pytz.timezone('Europe/Paris')).isoformat(), FORMAT='2.8', VERSION='2.8')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:noNamespaceSchemaLocation', "http://www.mpi.nl/tools/elan/EAFv2.8.xsd")
        header = SubElement(root, 'HEADER')
    
    #ipa only
    # if idText not in audiosList and flex == 0:
        #aktuellsten IPA-Text finden
        # cursor.execute('SELECT max(id_IPA) FROM `ipa` where id_text = %s;',(idText))
        # resultLatestIPA = cursor.fetchone()
        # cursor.execute('select IPA_text from ipa where id_IPA ='+str(resultLatestIPA[0]))
        # resultIPAtext = cursor.fetchone()
        # ipa = resultIPAtext[0]
        # ipa = ipa.replace('#', '')
        #Anzahl der W�rter f�r Anzahl der ben�igten time slots berechnen --> ein Wort hat einen time slot
        # numTS =  len(ipa.split())
        #Liste mit Saetzen aus dem IPA-Text gernerieren
        # delimiterSent = ['.', '!', '?']
        # for char in delimiterSent: #Delimiter f�r S�tze festlegen
            # if char in ipa:
                # ipa = ipa.replace(char, char[0]+'endmarker')
        # listSents = re.split('endmarker',ipa) #ein Satz = 1 Eintrag
        # annotationIDcounter = 0
        #verschiedene Counter für die time slots
        # timeValueCounter = 0
        # tsCounterStart = 0
        # tsCounterEnd = 0
        # timeOrder = SubElement(root, 'TIME_ORDER')
        #so viele time slots anlegen, wie es Woerter gibt
        # tsRef = 0
        # for x in range(0, numTS+len(listSents)):
            # timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(tsRef), TIME_VALUE=str(timeValueCounter))
            # tsRef += 1
            # timeValueCounter += 400
        # tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@ABC")
        # annotation = SubElement(tierRef, 'ANNOTATION')
        # alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts0', TIME_SLOT_REF2='ts1')
        # annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
        # annotationValue.text = str(idText)
        # annotationIDcounter += 1
        # tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", LANG_REF=langRef, PARENT_REF="ref@ABC", TIER_ID="orth@ABC")
        # tierWord = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="wordT", LANG_REF=langRef, PARENT_REF="orth@ABC", TIER_ID="word@ABC")
            #Saetze erstellen
        # for sent in listSents:
            # listWords = sent.split(' ')
            # tsCounterEnd += len(listWords)
            # annotation = SubElement(tierOrth, 'ANNOTATION')
            # alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(tsCounterStart), TIME_SLOT_REF2='ts'+str(tsCounterEnd))
            # annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
            # annotationValue.text = sent
            # annotationIDcounter += 1
            # tsCounterWord = tsCounterStart
            # tsCounterStart += len(listWords)
                #Woerter erstellen
            # for word in listWords:
                # if word != '':
                    # annotation = SubElement(tierWord, 'ANNOTATION')
                    # alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(tsCounterWord), TIME_SLOT_REF2='ts'+str(tsCounterWord+1))
                    # annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    # annotationValue.text = word
                    # annotationIDcounter += 1
                    # tsCounterWord += 1
                    
    #ipa audio
    
    #flex only
        if idText not in audiosList and flex == 1:
            annotationIDcounter = 0
            resultTokenList = [] #Hilfsliste mit allen id_token
            dictIDtokens = {} #Dict mit allen id_tokens über alle Sätze + dazugehörige time slots: jedes Token hat 6 time slots,
            #da ein Token aus bis zu 6 Morphemen bestehen kann. Morpheme sind die kleinste Einheit, weshalb jedem Morphem ein
            #time slot zugeordent wird.
            #verschiedene counter für die time slots
            tsCounter = 0
            tsCounterIntern = 0
            timeValueCounter = 0

            #SQL-Befehle
            #Liste mit id_sentences für einen Text
            cursor.execute('select id_sentence from flex_sentences where id_text = %s', (idText))
            resultIdSentences = list(cursor)
            #Liste mit id_tokens für alle Sätze eines Textes
            for id in resultIdSentences:
                cursor.execute('select id_token from flex_tokens where id_sentence = %s ', (id[0]))
                resultTokenList += list(cursor)
            #Dict mit id_tokens und den dazugehörigen time slots
            for elem in resultTokenList:
                dictIDtokens[elem[0]] = (tsCounter, tsCounter+6)
                tsCounter = tsCounter+6

            #XML
            timeOrder = SubElement(root, 'TIME_ORDER')
            for x in range(0, tsCounter+2):
                timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(tsCounterIntern), TIME_VALUE=str(timeValueCounter)) #TIME_VALUE wieder reingetan
                tsCounterIntern += 1
                timeValueCounter += 400 #wieder reingetan

            tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@ABC")
            annotation = SubElement(tierRef, 'ANNOTATION')
            alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts0', TIME_SLOT_REF2='ts1')
            annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
            annotationValue.text = str(idText)
            annotationIDcounter += 1

            tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="ref@ABC", LANG_REF=langRef, TIER_ID="orth@ABC")
            for id in resultIdSentences:
                id_sentence = id[0]
                cursor.execute('select group_concat(form_token SEPARATOR " "), MIN(id_token), MAX(id_token) from flex_tokens join flex_sentences using (id_sentence) where id_text = %s and id_sentence = %s order by id_token', (idText, id_sentence))
                result1sentence = list(cursor)
                minIDtoken = result1sentence[0][1]
                maxIDtoken = result1sentence[0][2]
                annotation = SubElement(tierOrth, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(dictIDtokens[minIDtoken][0]), TIME_SLOT_REF2='ts'+str(dictIDtokens[maxIDtoken][1]))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = result1sentence[0][0]
                annotationIDcounter += 1

            tierWord = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="wordT", PARENT_REF="orth@ABC", LANG_REF=langRef, TIER_ID="word@ABC")
            for key, value in dictIDtokens.items():
                cursor.execute('select form_token from flex_tokens where id_token = %s', (key))
                resultWord = cursor.fetchone()
                annotation = SubElement(tierWord, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(value[0]), TIME_SLOT_REF2='ts'+str(value[1]))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = resultWord[0]
                annotationIDcounter += 1

            def makingMorphLemmaPosGloss(columnName, tier, annotationIDcounter):
                for key, value in dictIDtokens.items():
                    cursor.execute('select ' +columnName+ '_0 from flex_tokens where id_token = '+str(key))
                    result0 = cursor.fetchone()
                    if result0[0] != '':
                        annotation = SubElement(tier, 'ANNOTATION')
                        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(value[0]), TIME_SLOT_REF2='ts'+str(value[0]+1))
                        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                        annotationValue.text = result0[0]
                        annotationIDcounter += 1

                    cursor.execute('select ' +columnName+ '_1 from flex_tokens where id_token = '+str(key))
                    result1 = cursor.fetchone()
                    if result1[0] != '':
                        annotation = SubElement(tier, 'ANNOTATION')
                        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(value[0]+1), TIME_SLOT_REF2='ts'+str(value[0]+2))
                        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                        annotationValue.text = result1[0]
                        annotationIDcounter += 1

                    cursor.execute('select ' +columnName+ '_2 from flex_tokens where id_token = '+str(key))
                    result2 = cursor.fetchone()
                    if result2[0] != '':
                        annotation = SubElement(tier, 'ANNOTATION')
                        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(value[0]+2), TIME_SLOT_REF2='ts'+str(value[0]+3))
                        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                        annotationValue.text = result2[0]
                        annotationIDcounter += 1

                    cursor.execute('select ' +columnName+ '_3 from flex_tokens where id_token = '+str(key))
                    result3 = cursor.fetchone()
                    if result3[0] != '':
                        annotation = SubElement(tier, 'ANNOTATION')
                        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(value[0]+3), TIME_SLOT_REF2='ts'+str(value[0]+4))
                        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                        annotationValue.text = result3[0]
                        annotationIDcounter += 1

                    cursor.execute('select ' +columnName+ '_4 from flex_tokens where id_token = '+str(key))
                    result4 = cursor.fetchone()
                    if result4[0] != '':
                        annotation = SubElement(tier, 'ANNOTATION')
                        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(value[0]+4), TIME_SLOT_REF2='ts'+str(value[0]+5))
                        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                        annotationValue.text = result4[0]
                        annotationIDcounter += 1

                    cursor.execute('select ' +columnName+ '_5 from flex_tokens where id_token = '+str(key))
                    result5 = cursor.fetchone()
                    if result5[0] != '':
                        annotation = SubElement(tier, 'ANNOTATION')
                        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(value[0]+5), TIME_SLOT_REF2='ts'+str(value[1]))
                        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                        annotationValue.text = result5[0]
                        annotationIDcounter += 1
                return annotationIDcounter

            tierMorph = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="morphT", PARENT_REF="word@ABC", LANG_REF=langRef, TIER_ID="morph@ABC")
            annotationIDcounter = makingMorphLemmaPosGloss('segment', tierMorph, annotationIDcounter)

            tierMorphVar = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="morph@ABC", LANG_REF=langRef, TIER_ID="morph-var@ABC")
            annotationIDcounter = makingMorphLemmaPosGloss('vt', tierMorphVar, annotationIDcounter)

            tierLemma = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="lemmaT", PARENT_REF="morph@ABC", LANG_REF=langRef, TIER_ID="lemma@ABC")
            annotationIDcounter = makingMorphLemmaPosGloss('cf', tierLemma, annotationIDcounter)

            tierGloss = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="glossT", PARENT_REF="lemma@ABC", LANG_REF=langRef, TIER_ID="gloss@ABC")
            annotationIDcounter = makingMorphLemmaPosGloss('gls', tierGloss, annotationIDcounter)

            tierPos = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="posT", PARENT_REF="lemma@ABC", LANG_REF=langRef, TIER_ID="pos@ABC")
            annotationIDcounter = makingMorphLemmaPosGloss('pos', tierPos, annotationIDcounter)

            tierRus = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-rusT", PARENT_REF="orth@ABC", LANG_REF='ru', TIER_ID="ft-rus@ABC")
            tierHun = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-hunT", PARENT_REF="orth@ABC", LANG_REF='hu', TIER_ID="ft-hun@ABC")
            tierEng = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-engT", PARENT_REF="orth@ABC", LANG_REF='en', TIER_ID="ft-eng@ABC")
            tierFin = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-finT", PARENT_REF="orth@ABC", LANG_REF='fi', TIER_ID="ft-fin@ABC")
            tierDeu = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-deuT", PARENT_REF="orth@ABC", LANG_REF='de', TIER_ID="ft-deu@ABC")
            for id in resultIdSentences:
                id_sentence = id[0]
                cursor.execute('select MIN(id_token), MAX(id_token) from flex_tokens join flex_sentences using (id_sentence) where id_text = %s and id_sentence = %s order by id_token', (idText, id_sentence))
                result1sentence = list(cursor)
                minIDtoken = result1sentence[0][0]
                maxIDtoken = result1sentence[0][1]

                cursor.execute('select trans_ru from flex_sentences where id_sentence = %s', (id_sentence))
                result = cursor.fetchone()
                if result[0] != '':
                    annotation = SubElement(tierRus, 'ANNOTATION')
                    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(dictIDtokens[minIDtoken][0]), TIME_SLOT_REF2='ts'+str(dictIDtokens[maxIDtoken][1]))
                    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    annotationValue.text = result[0]
                    annotationIDcounter += 1

                cursor.execute('select trans_hu from flex_sentences where id_sentence = %s', (id_sentence))
                result = cursor.fetchone()
                if result[0] != '':
                    annotation = SubElement(tierHun, 'ANNOTATION')
                    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(dictIDtokens[minIDtoken][0]), TIME_SLOT_REF2='ts'+str(dictIDtokens[maxIDtoken][1]))
                    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    annotationValue.text = result[0]
                    annotationIDcounter += 1

                cursor.execute('select trans_en from flex_sentences where id_sentence = %s', (id_sentence))
                result = cursor.fetchone()
                if result[0] != '':
                    annotation = SubElement(tierEng, 'ANNOTATION')
                    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(dictIDtokens[minIDtoken][0]), TIME_SLOT_REF2='ts'+str(dictIDtokens[maxIDtoken][1]))
                    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    annotationValue.text = result[0]
                    annotationIDcounter += 1

                cursor.execute('select trans_fi from flex_sentences where id_sentence = %s', (id_sentence))
                result = cursor.fetchone()
                if result[0] != '':
                    annotation = SubElement(tierFin, 'ANNOTATION')
                    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(dictIDtokens[minIDtoken][0]), TIME_SLOT_REF2='ts'+str(dictIDtokens[maxIDtoken][1]))
                    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    annotationValue.text = result[0]
                    annotationIDcounter += 1

                cursor.execute('select trans_de from flex_sentences where id_sentence = %s', (id_sentence))
                result = cursor.fetchone()
                if result[0] != '':
                    annotation = SubElement(tierDeu, 'ANNOTATION')
                    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(dictIDtokens[minIDtoken][0]), TIME_SLOT_REF2='ts'+str(dictIDtokens[maxIDtoken][1]))
                    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    annotationValue.text = result[0]
                    annotationIDcounter += 1
    
    #flex audio
    #if idText in audioDict and flex == 1
    #     cursor.execute("Select audio_filename from digital_resources where audio_filename regexp '.wav$' and id_text = %s;",(idText))
    #     audioFile = cursor.fetchone()
    #     print(idText, audioFile)
    #     header.set('MEDIA_FILE', '')
    #     header.set('TIME_UNITS', 'milliseconds')
    #     mediaDescriptor = SubElement(header, 'MEDIA_DESCRIPTOR')
    #     mediaDescriptor.set('MEDIA_URL', audioFile[0])
    #     mediaDescriptor.set('MIME_TYPE', 'audio/x-wav')
    #     mediaDescriptor.set('RELATIVE_MEDIA_URL', audioFile[0])
    #     property = SubElement(header, 'PROPERTY')
    #     property.set('NAME', 'lastUsedAnnotationId')
        
    #allgemeines Ende
    #linguistic types
        ltRef = SubElement(root, 'LINGUISTIC_TYPE', GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="refT", TIME_ALIGNABLE="true")
        ltOrth = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="orthT", TIME_ALIGNABLE="false")
        ltWord = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Subdivision", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="wordT", TIME_ALIGNABLE="false")
        ltMorph = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Subdivision", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="morphT", TIME_ALIGNABLE="false")
        ltLemma = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="lemmaT", TIME_ALIGNABLE="false")
        ltGloss = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="glossT", TIME_ALIGNABLE="false")
        ltPos = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="posT", TIME_ALIGNABLE="false")
        ltEng = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="ft-engT", TIME_ALIGNABLE="false")
        ltRus = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="ft-rusT", TIME_ALIGNABLE="false")
        ltHun = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="ft-hunT", TIME_ALIGNABLE="false")
        ltDeu = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="ft-deuT", TIME_ALIGNABLE="false")
        ltFin = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="ft-finT", TIME_ALIGNABLE="false")
            #ltIpa = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="codeT", TIME_ALIGNABLE="false") #wir nicht ben�tigt?
        ltMorphVar = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="morph-varT", TIME_ALIGNABLE="false")
            #Sprachtypen anlegen
        if langRef == 'mns':
            langMansi = SubElement(root, 'LANGUAGE', LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001", LANG_ID="mns", LANG_LABEL="Mansi (mns)")
        if langRef == 'kca':
            langKhanty = SubElement(root, 'LANGUAGE', LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001", LANG_ID="kca", LANG_LABEL="Khanty (kca)")
        langDeutsch = SubElement(root, 'LANGUAGE', LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001", LANG_ID="de", LANG_LABEL="Deutsch (de)")
        langEnglisch = SubElement(root, 'LANGUAGE', LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001", LANG_ID="en", LANG_LABEL="Englisch (en)")
        langRussisch = SubElement(root, 'LANGUAGE', LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001", LANG_ID="ru", LANG_LABEL="Russisch (ru)")
        langUngarisch = SubElement(root, 'LANGUAGE', LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001", LANG_ID="hu", LANG_LABEL="Ungarisch (hu)")
        langFinnisch = SubElement(root, 'LANGUAGE', LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001", LANG_ID="fi", LANG_LABEL="Finnisch (fi)")

        constraint1 = SubElement(root, 'CONSTRAINT', DESCRIPTION="Time subdivision of parent annotation's time interval, no time gaps allowed within this interval", STEREOTYPE="Time_Subdivision")
        constraint2 = SubElement(root, 'CONSTRAINT', DESCRIPTION="Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered", STEREOTYPE="Symbolic_Subdivision")
        constraint3 = SubElement(root, 'CONSTRAINT', DESCRIPTION="1-1 association with a parent annotation", STEREOTYPE="Symbolic_Association")
        constraint4 = SubElement(root, 'CONSTRAINT', DESCRIPTION="Time alignable annotations within the parent annotation's time interval, gaps are allowed", STEREOTYPE="Included_In")
            
            #Leerzeichen einf�gen, um das Dokument lesbarer zu machen:
        rough_string = ET.tostring(root, 'utf-8')
        dom = minidom.parseString(rough_string)
            #eigene processing instruction einf�gen
        pi = dom.createProcessingInstruction('xml version="1.0"', 'encoding="UTF-8"')
        root = dom.firstChild
        dom.insertBefore(pi, root)
        prettyXML = dom.toprettyxml()
            #automatische erzeugte XML processing instruction l�schen
        stripped = prettyXML.lstrip('<?xml version="1.0" ?>')
            #1. Leerzeile entfernen
        strippedNewLine = stripped.lstrip()
    
    ##ipa only
    # if idText not in audiosList and flex == 0:
        # outputFile = open("ipaOnly/"+nameAbbreviation+"_" +str(idText)+".eaf","w",encoding="utf-8")
        # outputFile.write(strippedNewLine)
        # outputFile.close()
    #ipa + audio
    # if idText in audiosList and flex == 0:
        # outputFile = open("ipaAudio/"+nameAbbreviation+"_" +str(idText)+".eaf","w",encoding="utf-8")
        # outputFile.write(strippedNewLine)
        # outputFile.close()
        if idText not in audiosList and flex == 1:
            outputFile = open("flexOnly/"+nameAbbreviation+"_" +str(idText)+".eaf","w",encoding="utf-8")
            outputFile.write(strippedNewLine)
            outputFile.close()
        # if idText in audioList and flex == 1
            # outputFile = open("flexAudio/"+nameAbbreviation+"_" +str(idText)+".eaf","w",encoding="utf-8")
            # outputFile.write(strippedNewLine)
            # outputFile.close()