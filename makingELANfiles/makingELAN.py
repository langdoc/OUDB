# -*- coding: utf-8 -*-
from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
#Verbindung zur Datenbank
import pymysql
from pymysql import connect, err, sys, cursors
#fuer Datum
import datetime
import pytz #timzone
import re
from ZugangsdatenDB import getZugangsdaten

#zum Testen von flex only

hostname, portname, username, passwdname, dbname = getZugangsdaten()

#Verbindung zur DB aufbauen
dbObj = pymysql.connect(host = hostname, port = portname, user = username, passwd = passwdname, db = dbname, charset='utf8')
cursor = dbObj.cursor()

#alle benoetigten Texte holen
cursor.execute('Select id_text, dialect, public_glossed from documents_info where public = 1 and id_text = 1313')
listDocInfo = list(cursor)

#Texte mit audio
cursor.execute("Select DISTINCT id_text from elan_data where elan_speaker = 'default' and nr_wav_file = 1")
audios = list(cursor)
audiosList = []
for elem in audios:
    audiosList.append(elem[0])

for singleText in listDocInfo:
    annotationIDcounter = 0
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
    cursor.execute("Select audio_filename from digital_resources where audio_filename regexp '.wav$' and id_text = %s;",(idText))
    audioFile = cursor.fetchone()

    #ipa only
    if idText not in audiosList and flex == 0:
        #aktuellsten IPA-Text finden
        cursor.execute('SELECT max(id_IPA) FROM `ipa` where id_text = %s;',(idText))
        resultLatestIPA = cursor.fetchone()
        cursor.execute('select IPA_text from ipa where id_IPA ='+str(resultLatestIPA[0]))
        resultIPAtext = cursor.fetchone()
        ipa = resultIPAtext[0]
        ipa = ipa.replace('#', '')
        #Anzahl der W�rter f�r Anzahl der ben�igten time slots berechnen --> ein Wort hat einen time slot
        numTS =  len(ipa.split())
        #Liste mit Saetzen aus dem IPA-Text gernerieren
        delimiterSent = ['.', '!', '?']
        for char in delimiterSent: #Delimiter f�r S�tze festlegen
            if char in ipa:
                ipa = ipa.replace(char, char[0]+'endmarker')
        listSents = re.split('endmarker',ipa) #ein Satz = 1 Eintrag
        annotationIDcounter = 0
        #verschiedene Counter für die time slots
        timeValueCounter = 0
        tsCounterStart = 0
        tsCounterEnd = 0
        timeOrder = SubElement(root, 'TIME_ORDER')
        #so viele time slots anlegen, wie es Woerter gibt
        tsRef = 0
        for x in range(0, numTS+len(listSents)):
            timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(tsRef), TIME_VALUE=str(timeValueCounter))
            tsRef += 1
            timeValueCounter += 400
        tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@ABC")
        annotation = SubElement(tierRef, 'ANNOTATION')
        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts0', TIME_SLOT_REF2='ts1')
        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
        annotationValue.text = str(idText)
        annotationIDcounter += 1
        tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", LANG_REF=langRef, PARENT_REF="ref@ABC", TIER_ID="orth@ABC")
        tierWord = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="wordT", LANG_REF=langRef, PARENT_REF="orth@ABC", TIER_ID="word@ABC")
            #Saetze erstellen
        for sent in listSents:
            listWords = sent.split(' ')
            tsCounterEnd += len(listWords)
            annotation = SubElement(tierOrth, 'ANNOTATION')
            alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(tsCounterStart), TIME_SLOT_REF2='ts'+str(tsCounterEnd))
            annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
            annotationValue.text = sent
            annotationIDcounter += 1
            tsCounterWord = tsCounterStart
            tsCounterStart += len(listWords)
                #Woerter erstellen
            for word in listWords:
                if word != '':
                    annotation = SubElement(tierWord, 'ANNOTATION')
                    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(tsCounterWord), TIME_SLOT_REF2='ts'+str(tsCounterWord+1))
                    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    annotationValue.text = word
                    annotationIDcounter += 1
                    tsCounterWord += 1
                    
    #ipa audio
    if idText in audiosList and flex == 0:
        cursor.execute('Select time_code, time_code_end, nr_sentence, elan_sentence from elan_data where id_text = %s;',(idText))
        tmpList = list(cursor)
        cursor.execute("Select audio_filename from digital_resources where audio_filename regexp '.wav$' and id_text = %s;",(idText))
        audioFile = cursor.fetchone()
        audioDict = {}
        textDict = {} #für Sätze aus elan_data
        i=1 #für Sätze aus elan_data
        for elem in tmpList:
            audioDict[elem[2]] = int(elem[0]*1000), int(elem[1]*1000)
            textDict[i] = elem[3] #für Sätze aus elan_data
            i = i + 1 #für Sätze aus elan_data

        timeOrder = SubElement(root, 'TIME_ORDER')
        tsCounter = 0
        tsDict = {} 
        for elem in audioDict.items():
            tsRef1 = elem[1][0]
            tsRef2 = elem[1][1]
            timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(tsCounter), TIME_VALUE=str(tsRef1))
            tsCounter +=1
            timeSlot2 = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(tsCounter), TIME_VALUE=str(tsRef2))
            tsDict[elem[0]] = tsCounter-1, tsRef1, tsCounter, tsRef2
            tsCounter += 1
        
        header.set('MEDIA_FILE', '')
        header.set('TIME_UNITS', 'milliseconds')
        mediaDescriptor = SubElement(header, 'MEDIA_DESCRIPTOR')
        mediaDescriptor.set('MEDIA_URL', audioFile[0])
        mediaDescriptor.set('MIME_TYPE', 'audio/x-wav')
        mediaDescriptor.set('RELATIVE_MEDIA_URL', audioFile[0])
        property = SubElement(header, 'PROPERTY')
        property.set('NAME', 'lastUsedAnnotationId')
        
        ##aktuellsten IPA-Text finden
        cursor.execute('SELECT max(id_IPA) FROM `ipa` where id_text = %s;',(idText))
        resultLatestIPA = cursor.fetchone()
        cursor.execute('select IPA_text from ipa where id_IPA ='+str(resultLatestIPA[0]))
        resultIPAtext = cursor.fetchone()
        ipa = resultIPAtext[0]
        ipa = ipa.replace('#', '')
        ##Liste mit Saetzen aus dem IPA-Text generieren
        delimiterSent = ['.', '!', '?']
        for char in delimiterSent: #Delimiter fuer Saetze festlegen
            if char in ipa:
                ipa = ipa.replace(char, char[0]+'endmarker')
        listSents = re.split('endmarker',ipa) #ein Satz = 1 Eintrag
        annotationIDcounter = 0
        
        tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@ABC")
        annotation = SubElement(tierRef, 'ANNOTATION')
        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts0', TIME_SLOT_REF2='ts1')
        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
        annotationValue.text = str(idText)
        annotationIDcounter += 1
        tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", LANG_REF=langRef, PARENT_REF="ref@ABC", TIER_ID="orth@ABC")
        ##Saetze erstellen
        for index in range(1, len(tsDict)+1): #+1
            tsRef1aligAnn = tsDict[index][0]
            tsRef2aligAnn = tsDict[index][2]
            annotation = SubElement(tierOrth, 'ANNOTATION')
            alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(tsRef1aligAnn), TIME_SLOT_REF2='ts'+str(tsRef2aligAnn))
            annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
            annotationValue.text = textDict[index] #Sätze aus elan_data verwendet! (aus ipa: auskommentiert)
            #annotationValue.text = listSents[index]
            annotationIDcounter += 1    
            
    #flex only   
    if idText not in audiosList and flex == 1:
        #Liste mit id_sentences für einen Text
        cursor.execute('select id_sentence from flex_sentences where id_text = %s', (idText))
        resultIdSentences = list(cursor)
        #Liste mit id_tokens für alle Sätze eines Textes
        dictTokens = {} #dict mit allen Token eines Textes
        dictTS = {} #dict mit allen time slots
        timeSlotCounter = 0
        timeSlotCounterCopy = 0
        
        #parent tier für time slots anlegen
        timeOrder = SubElement(root, 'TIME_ORDER')
        #tier Ref anlegen
        tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@ABC")
        annotation = SubElement(tierRef, 'ANNOTATION')
        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts0', TIME_SLOT_REF2='ts1')
        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
        annotationValue.text = str(idText)
        annotationIDcounter += 1
        #parent tier für Originalsatz anlegen
        tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="ref@ABC", LANG_REF=langRef, TIER_ID="orth@ABC")
        #parent tier fuer Originalwort anlegen
        tierWord = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="wordT", PARENT_REF="orth@ABC", LANG_REF=langRef, TIER_ID="word@ABC")
        #parent tiers fuer Morpheme, Lemmata etc. anlegen
        tierMorph = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="morphT", PARENT_REF="word@ABC", LANG_REF=langRef, TIER_ID="morph@ABC")
        tierMorphVar = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="morph@ABC", LANG_REF=langRef, TIER_ID="morph-var@ABC")
        tierLemma = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="lemmaT", PARENT_REF="morph@ABC", LANG_REF=langRef, TIER_ID="lemma@ABC")
        tierGloss = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="glossT", PARENT_REF="lemma@ABC", LANG_REF=langRef, TIER_ID="gloss@ABC")
        tierPos = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="posT", PARENT_REF="lemma@ABC", LANG_REF=langRef, TIER_ID="pos@ABC")
        #parent tiers für Übersetzungen anlegen:
        tierRus = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-rusT", PARENT_REF="orth@ABC", LANG_REF='ru', TIER_ID="ft-rus@ABC")
        tierHun = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-hunT", PARENT_REF="orth@ABC", LANG_REF='hu', TIER_ID="ft-hun@ABC")
        tierEng = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-engT", PARENT_REF="orth@ABC", LANG_REF='en', TIER_ID="ft-eng@ABC")
        tierFin = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-finT", PARENT_REF="orth@ABC", LANG_REF='fi', TIER_ID="ft-fin@ABC")
        tierDeu = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-deuT", PARENT_REF="orth@ABC", LANG_REF='de', TIER_ID="ft-deu@ABC")
        
        #künstliche time codes anlegen
        timeCode = 0
        timeCodeEnd = 1200 #darf bei time slot später keine float-zahl werden; muss durch 6 teilbar sein; Wert unten auch 2mal aendern
        for id in resultIdSentences:
            cursor.execute('select id_token from flex_tokens where id_sentence = %s ', (id))
            tokenIDList = list(cursor)
            cursor.execute('select trans_en, trans_de, trans_ru, trans_hu, trans_fi from flex_sentences where id_sentence = %s ', (id))
            transList = list(cursor)
            #print(transList)
            idSent = id[0]
            timeCodeSpan = timeCodeEnd - timeCode
            numIDtokens = len(tokenIDList) #Anzahl der Token in einem Satz
            numTSperSent = numIDtokens*6 #jedes Token kann aus bis zu 6 Morphemen bestehen, jedes Morphem bekommt einen time slot; numTSperSent = Anzahl time slots pro Satz
            timeValueSpan = timeCodeSpan/numTSperSent #Länge eines time slots
            
            sentToPrint = ''
            timeSlotCounterCopy = timeSlotCounter #timeslotcountercopy (fuer Woerter an timeslotcounter (fuer saetze) anpassen
            for elem in tokenIDList:
                cursor.execute('select form_token, segment_0, segment_1, segment_2, segment_3, segment_4, segment_5, vt_0, vt_1, vt_2, vt_3, vt_4, vt_5, cf_0, cf_1, cf_2, cf_3, cf_4, cf_5, gls_0, gls_1, gls_2, gls_3, gls_4, gls_5, pos_0, pos_1, pos_2, pos_3, pos_4, pos_5 from flex_tokens where id_token = %s ', (elem[0]))
                tokenLevel = cursor.fetchall()
                #print(tokenLevel)
                sentToPrint += tokenLevel[0][0] + ' ' #Wörter zu einem Satz zusammenfügen
                #Wörter mit time slots anlegen
                #form_token = ganzes Wort
                if tokenLevel[0][0] != '':
                    annotation = SubElement(tierWord, 'ANNOTATION')
                    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    annotationValue.text = tokenLevel[0][0]
                    annotationIDcounter += 1
                #morph 0
                if tokenLevel[0][1] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][1]
                   annotationIDcounter += 1
                #morph 1            
                if tokenLevel[0][2] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][2]
                   annotationIDcounter += 1
                #morph 2 
                if tokenLevel[0][3] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][3]
                   annotationIDcounter += 1
                #morph 3           
                if tokenLevel[0][4] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][4]
                   annotationIDcounter += 1
                #morph 4
                if tokenLevel[0][5] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][5]
                   annotationIDcounter += 1
                #morph 5            
                if tokenLevel[0][6] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][6]
                   annotationIDcounter += 1
                   
                #morphVar 0            
                if tokenLevel[0][7] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][7]
                   annotationIDcounter += 1
                #morphVar 1            
                if tokenLevel[0][8] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][8]
                   annotationIDcounter += 1
                #morphVar 2 
                if tokenLevel[0][9] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][9]
                   annotationIDcounter += 1
                #morphVar 3           
                if tokenLevel[0][10] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][10]
                   annotationIDcounter += 1
                #morphVar 4
                if tokenLevel[0][11] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][11]
                   annotationIDcounter += 1
                #morphVar 5            
                if tokenLevel[0][12] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][12]
                   annotationIDcounter += 1  

                #lemma 0            
                if tokenLevel[0][13] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][13]
                   annotationIDcounter += 1
                #lemma 1            
                if tokenLevel[0][14] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][14]
                   annotationIDcounter += 1
                #lemma 2 
                if tokenLevel[0][15] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][15]
                   annotationIDcounter += 1
                #lemma 3           
                if tokenLevel[0][16] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][16]
                   annotationIDcounter += 1
                #lemma 4
                if tokenLevel[0][17] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][17]
                   annotationIDcounter += 1
                #lemma 5            
                if tokenLevel[0][18] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][18]
                   annotationIDcounter += 1               
            
                #gloss 0            
                if tokenLevel[0][19] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][19]
                   annotationIDcounter += 1
                #gloss 1            
                if tokenLevel[0][20] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][20]
                   annotationIDcounter += 1
                #gloss 2 
                if tokenLevel[0][21] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][21]
                   annotationIDcounter += 1
                #gloss 3           
                if tokenLevel[0][22] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][22]
                   annotationIDcounter += 1
                #gloss 4
                if tokenLevel[0][23] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][23]
                   annotationIDcounter += 1
                #gloss 5            
                if tokenLevel[0][24] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][24]
                   annotationIDcounter += 1
            
                #pos 0            
                if tokenLevel[0][25] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][25]
                   annotationIDcounter += 1
                #pos 1            
                if tokenLevel[0][26] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][26]
                   annotationIDcounter += 1
                #pos 2 
                if tokenLevel[0][27] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][27]
                   annotationIDcounter += 1
                #pos 3           
                if tokenLevel[0][28] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][28]
                   annotationIDcounter += 1
                #pos 4
                if tokenLevel[0][29] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][29]
                   annotationIDcounter += 1
                #pos 5            
                if tokenLevel[0][30] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][30]
                   annotationIDcounter += 1

                timeSlotCounterCopy += 6

            #child tiers für Originalsatz füllen
            annotation = SubElement(tierOrth, 'ANNOTATION')
            alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
            annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
            annotationValue.text = sentToPrint
            annotationIDcounter += 1
             #child tiers für Uebersetzungen fuellen
            if transList[0][2] != '':
                annotation = SubElement(tierRus, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][2]
                annotationIDcounter += 1
            if transList[0][3] != '':
                annotation = SubElement(tierHun, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][3]
                annotationIDcounter += 1
            if transList[0][0] != '':
                annotation = SubElement(tierEng, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][0]
                annotationIDcounter += 1
            if transList[0][4] != '':
                annotation = SubElement(tierFin, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][4]
                annotationIDcounter += 1
            if transList[0][1] != '':
                annotation = SubElement(tierDeu, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][1]
                annotationIDcounter += 1 
            
            for singleToken in range(0, numTSperSent+1):
                timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(timeSlotCounter), TIME_VALUE=str(int(timeCode+singleToken*timeValueSpan)))#timeValue für ein Token + time value für ein einzelnes Morphem
                annotationIDcounter += 1
                timeSlotCounter += 1    
        #time codes für nächsten Satz erhöhen --> ein Satz hat eine Länge von 1200
            timeCode += 1200
            timeCodeEnd += 1200
        
    #flex audio
    if idText in audiosList and flex == 1:
        header.set('MEDIA_FILE', '')
        header.set('TIME_UNITS', 'milliseconds')
        mediaDescriptor = SubElement(header, 'MEDIA_DESCRIPTOR')
        mediaDescriptor.set('MEDIA_URL', audioFile[0])
        mediaDescriptor.set('MIME_TYPE', 'audio/x-wav')
        mediaDescriptor.set('RELATIVE_MEDIA_URL', audioFile[0])
        property = SubElement(header, 'PROPERTY')
        property.set('NAME', 'lastUsedAnnotationId')

        cursor.execute('Select nr_sentence, time_code, time_code_end from elan_data where id_text = %s;',(idText))
        elanList = list(cursor)
        numElanSents = len(elanList)
        #Liste mit id_sentences für einen Text
        cursor.execute('select id_sentence from flex_sentences where id_text = %s', (idText))
        resultIdSentences = list(cursor)
        #Liste mit id_tokens für alle Sätze eines Textes
        dictTokens = {} #dict mit allen Token eines Textes
        dictTS = {} #dict mit allen time slots
        timeSlotCounter = 0
        timeSlotCounterCopy = 0

        #parent tier für time slots anlegen
        timeOrder = SubElement(root, 'TIME_ORDER')
        #tier Ref anlegen
        tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@ABC")
        annotation = SubElement(tierRef, 'ANNOTATION')
        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts0', TIME_SLOT_REF2='ts1')
        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
        annotationValue.text = str(idText)
        annotationIDcounter += 1
        #parent tier für Originalsatz anlegen
        tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="ref@ABC", LANG_REF=langRef, TIER_ID="orth@ABC")
        #parent tier fuer Originalwort anlegen
        tierWord = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="wordT", PARENT_REF="orth@ABC", LANG_REF=langRef, TIER_ID="word@ABC")
        #parent tiers fuer Morpheme, Lemmata etc. anlegen
        tierMorph = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="morphT", PARENT_REF="word@ABC", LANG_REF=langRef, TIER_ID="morph@ABC")
        tierMorphVar = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="morph@ABC", LANG_REF=langRef, TIER_ID="morph-var@ABC")
        tierLemma = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="lemmaT", PARENT_REF="morph@ABC", LANG_REF=langRef, TIER_ID="lemma@ABC")
        tierGloss = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="glossT", PARENT_REF="lemma@ABC", LANG_REF=langRef, TIER_ID="gloss@ABC")
        tierPos = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="posT", PARENT_REF="lemma@ABC", LANG_REF=langRef, TIER_ID="pos@ABC")
        #parent tiers für Übersetzungen anlegen:
        tierRus = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-rusT", PARENT_REF="orth@ABC", LANG_REF='ru', TIER_ID="ft-rus@ABC")
        tierHun = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-hunT", PARENT_REF="orth@ABC", LANG_REF='hu', TIER_ID="ft-hun@ABC")
        tierEng = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-engT", PARENT_REF="orth@ABC", LANG_REF='en', TIER_ID="ft-eng@ABC")
        tierFin = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-finT", PARENT_REF="orth@ABC", LANG_REF='fi', TIER_ID="ft-fin@ABC")
        tierDeu = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-deuT", PARENT_REF="orth@ABC", LANG_REF='de', TIER_ID="ft-deu@ABC")
        
        for id, nr in zip(resultIdSentences, elanList):
            cursor.execute('select id_token from flex_tokens where id_sentence = %s ', (id))
            tokenIDList = list(cursor)
            cursor.execute('select trans_en, trans_de, trans_ru, trans_hu, trans_fi from flex_sentences where id_sentence = %s ', (id))
            transList = list(cursor)
            #print(transList)
            idSent = id[0]
            timeCode = nr[1]*1000
            timeCodeEnd = nr[2]*1000
            timeCodeSpan = timeCodeEnd - timeCode
            numIDtokens = len(tokenIDList) #Anzahl der Token in einem Satz
            numTSperSent = numIDtokens*6 #jedes Token kann aus bis zu 6 Morphemen bestehen, jedes Morphem bekommt einen time slot; numTSperSent = Anzahl time slots pro Satz
            timeValueSpan = timeCodeSpan/numTSperSent #Länge eines time slots

            sentToPrint = ''
            timeSlotCounterCopy = timeSlotCounter #time slotcountercopy (fuer Woerter) an timeslotcounter (fuer saetze) anpassen

            for elem in tokenIDList:


                cursor.execute('select form_token, segment_0, segment_1, segment_2, segment_3, segment_4, segment_5, vt_0, vt_1, vt_2, vt_3, vt_4, vt_5, cf_0, cf_1, cf_2, cf_3, cf_4, cf_5, gls_0, gls_1, gls_2, gls_3, gls_4, gls_5, pos_0, pos_1, pos_2, pos_3, pos_4, pos_5 from flex_tokens where id_token = %s ', (elem[0]))
                tokenLevel = cursor.fetchall()
                #print(tokenLevel)
                sentToPrint += tokenLevel[0][0] + ' ' #Wörter zu einem Satz zusammenfügen
                #Wörter mit time slots anlegen
                #form_token = ganzes Wort
                if tokenLevel[0][0] != '':
                    annotation = SubElement(tierWord, 'ANNOTATION')
                    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                    annotationValue.text = tokenLevel[0][0]
                    annotationIDcounter += 1
                #morph 0
                if tokenLevel[0][1] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][1]
                   annotationIDcounter += 1
                #morph 1            
                if tokenLevel[0][2] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][2]
                   annotationIDcounter += 1
                #morph 2 
                if tokenLevel[0][3] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][3]
                   annotationIDcounter += 1
                #morph 3           
                if tokenLevel[0][4] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][4]
                   annotationIDcounter += 1
                #morph 4
                if tokenLevel[0][5] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][5]
                   annotationIDcounter += 1
                #morph 5            
                if tokenLevel[0][6] != '':
                   annotation = SubElement(tierMorph, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][6]
                   annotationIDcounter += 1
                   
                #morphVar 0            
                if tokenLevel[0][7] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][7]
                   annotationIDcounter += 1
                #morphVar 1            
                if tokenLevel[0][8] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][8]
                   annotationIDcounter += 1
                #morphVar 2 
                if tokenLevel[0][9] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][9]
                   annotationIDcounter += 1
                #morphVar 3           
                if tokenLevel[0][10] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][10]
                   annotationIDcounter += 1
                #morphVar 4
                if tokenLevel[0][11] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][11]
                   annotationIDcounter += 1
                #morphVar 5            
                if tokenLevel[0][12] != '':
                   annotation = SubElement(tierMorphVar, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][12]
                   annotationIDcounter += 1  

                #lemma 0            
                if tokenLevel[0][13] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][13]
                   annotationIDcounter += 1
                #lemma 1            
                if tokenLevel[0][14] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][14]
                   annotationIDcounter += 1
                #lemma 2 
                if tokenLevel[0][15] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][15]
                   annotationIDcounter += 1
                #lemma 3           
                if tokenLevel[0][16] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][16]
                   annotationIDcounter += 1
                #lemma 4
                if tokenLevel[0][17] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][17]
                   annotationIDcounter += 1
                #lemma 5            
                if tokenLevel[0][18] != '':
                   annotation = SubElement(tierLemma, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][18]
                   annotationIDcounter += 1               
            
                #gloss 0            
                if tokenLevel[0][19] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][19]
                   annotationIDcounter += 1
                #gloss 1            
                if tokenLevel[0][20] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][20]
                   annotationIDcounter += 1
                #gloss 2 
                if tokenLevel[0][21] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][21]
                   annotationIDcounter += 1
                #gloss 3           
                if tokenLevel[0][22] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][22]
                   annotationIDcounter += 1
                #gloss 4
                if tokenLevel[0][23] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][23]
                   annotationIDcounter += 1
                #gloss 5            
                if tokenLevel[0][24] != '':
                   annotation = SubElement(tierGloss, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][24]
                   annotationIDcounter += 1
            
                #pos 0            
                if tokenLevel[0][25] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+1))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][25]
                   annotationIDcounter += 1
                #pos 1            
                if tokenLevel[0][26] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+1), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+2))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][26]
                   annotationIDcounter += 1
                #pos 2 
                if tokenLevel[0][27] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+2), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+3))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][27]
                   annotationIDcounter += 1
                #pos 3           
                if tokenLevel[0][28] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+3), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+4))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][28]
                   annotationIDcounter += 1
                #pos 4
                if tokenLevel[0][29] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+4), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+5))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][29]
                   annotationIDcounter += 1
                #pos 5            
                if tokenLevel[0][30] != '':
                   annotation = SubElement(tierPos, 'ANNOTATION')
                   alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounterCopy+5), TIME_SLOT_REF2='ts'+str(timeSlotCounterCopy+6))
                   annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                   annotationValue.text = tokenLevel[0][30]
                   annotationIDcounter += 1

                timeSlotCounterCopy += 6

            #child tiers für Originalsatz füllen
            annotation = SubElement(tierOrth, 'ANNOTATION')
            alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
            annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
            annotationValue.text = sentToPrint
            annotationIDcounter += 1
             #child tiers für Uebersetzungen fuellen
            if transList[0][2] != '':
                annotation = SubElement(tierRus, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][2]
                annotationIDcounter += 1
            if transList[0][3] != '':
                annotation = SubElement(tierHun, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][3]
                annotationIDcounter += 1
            if transList[0][0] != '':
                annotation = SubElement(tierEng, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][0]
                annotationIDcounter += 1
            if transList[0][4] != '':
                annotation = SubElement(tierFin, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][4]
                annotationIDcounter += 1
            if transList[0][1] != '':
                annotation = SubElement(tierDeu, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(timeSlotCounter), TIME_SLOT_REF2='ts'+str(timeSlotCounter+numTSperSent))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = transList[0][1]
                annotationIDcounter += 1 
            
            for singleToken in range(0, numTSperSent+1):
                timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(timeSlotCounter), TIME_VALUE=str(int(timeCode+singleToken*timeValueSpan)))#timeValue für ein Token + time value für ein einzelnes Morphem
                annotationIDcounter += 1
                timeSlotCounter += 1

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
    #ltIpa = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="codeT", TIME_ALIGNABLE="false") #wird nicht benoetigt
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

    #die nächsten 12 Zeilen nicht aendern!
    #Leerzeichen einfuegen, um das Dokument lesbarer zu machen:
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
    if idText not in audiosList and flex == 0:
        outputFile = open("ipaOnly/"+nameAbbreviation+"_" +str(idText)+".eaf","w",encoding="utf-8")
        outputFile.write(strippedNewLine)
        outputFile.close()
    #ipa  audio
    if idText in audiosList and flex == 0:
        outputFile = open("ipaAudio/"+nameAbbreviation+"_" +str(idText)+".eaf","w",encoding="utf-8")
        outputFile.write(strippedNewLine)
        outputFile.close()
    #flex only
    if idText not in audiosList and flex == 1:
        outputFile = open("flexOnly/"+nameAbbreviation+"_" +str(idText)+".eaf","w",encoding="utf-8")
        outputFile.write(strippedNewLine)
        outputFile.close()    
    #flex audio
    if idText in audiosList and flex == 1:
        outputFile = open("flexAudio/"+nameAbbreviation+"_" +str(idText)+".eaf","w",encoding="utf-8")
        outputFile.write(strippedNewLine)
        outputFile.close()
