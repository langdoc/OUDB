from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
#Verbindung zur Datenbank
import pymysql
#für Datum
import datetime
import pytz
import re
from ZugangsdatenDB import getZugangsdaten

hostname, portname, username, passwdname, dbname = getZugangsdaten()

#Verbindung zur DB aufbauen
dbObj = pymysql.connect(host = hostname, port = portname, user = username, passwd = passwdname, db = dbname, charset='utf8')
cursor = dbObj.cursor()
cursor.execute('select distinct id_text, public_glossed from documents_info order by id_text')
resultIDtexts = list(cursor)

resultIDtextINipaRaw = [] #Liste mit allen id_text, die in der ipa-Tabelle stehen
cursor.execute('select distinct id_text from ipa')
resultIDtextINipa = list(cursor)
for elem in resultIDtextINipa:
    resultIDtextINipaRaw.append(elem[0])

def makingTiersFlex(id_text, root, shortDialect):
    annotationIDcounter = 0
    resultTokenList = [] #Hilfsliste mit allen id_token
    dictIDtokens = {} #Dict mit allen id_tokens über alle Sätze + dazugehörige time slots: jedes Token hat 6 time slots,
    # da ein Token aus bis zu 6 Morphemen bestehen kann. Morpheme sind die kleinste Einheit, weshalb jedem Morphem ein
    # time slot zugeordent wird.
    #verschiedene counter für die time slots
    tsCounter = 0
    tsCounterIntern = 0
    timeValueCounter = 0

    #language attribute festlegen
    if shortDialect.endswith('M') == True or shortDialect.endswith('V') == True:
        lang = 'mns'
    if shortDialect.endswith('K') == True or shortDialect.endswith('A') == True:
        lang = 'kca'

    #SQL-Befehle
    #Liste mit id_sentences für einen Text
    cursor.execute('select id_sentence from flex_sentences where id_text = %s', (id_text))
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
        timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(tsCounterIntern), TIME_VALUE=str(timeValueCounter))
        tsCounterIntern += 1
        timeValueCounter += 400

    tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@ABC")
    annotation = SubElement(tierRef, 'ANNOTATION')
    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts0', TIME_SLOT_REF2='ts1')
    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
    annotationValue.text = id_text
    annotationIDcounter += 1

    tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="ref@ABC", LANG_REF=lang, TIER_ID="orth@ABC")
    for id in resultIdSentences:
        id_sentence = id[0]
        cursor.execute('select group_concat(form_token SEPARATOR " "), MIN(id_token), MAX(id_token) from flex_tokens join flex_sentences using (id_sentence) where id_text = %s and id_sentence = %s order by id_token', (id_text, id_sentence))
        result1sentence = list(cursor)
        minIDtoken = result1sentence[0][1]
        maxIDtoken = result1sentence[0][2]
        annotation = SubElement(tierOrth, 'ANNOTATION')
        alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(dictIDtokens[minIDtoken][0]), TIME_SLOT_REF2='ts'+str(dictIDtokens[maxIDtoken][1]))
        annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
        annotationValue.text = result1sentence[0][0]
        annotationIDcounter += 1

    tierWord = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="wordT", PARENT_REF="orth@ABC", LANG_REF=lang, TIER_ID="word@ABC")
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

    tierMorph = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="morphT", PARENT_REF="word@ABC", LANG_REF=lang, TIER_ID="morph@ABC")
    annotationIDcounter = makingMorphLemmaPosGloss('segment', tierMorph, annotationIDcounter)

    tierMorphVar = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="morph@ABC", LANG_REF=lang, TIER_ID="morph-var@ABC")
    annotationIDcounter = makingMorphLemmaPosGloss('vt', tierMorphVar, annotationIDcounter)

    tierLemma = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="lemmaT", PARENT_REF="morph@ABC", LANG_REF=lang, TIER_ID="lemma@ABC")
    annotationIDcounter = makingMorphLemmaPosGloss('cf', tierLemma, annotationIDcounter)

    tierGloss = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="glossT", PARENT_REF="lemma@ABC", LANG_REF=lang, TIER_ID="gloss@ABC")
    annotationIDcounter = makingMorphLemmaPosGloss('gls', tierGloss, annotationIDcounter)

    tierPos = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="posT", PARENT_REF="lemma@ABC", LANG_REF=lang, TIER_ID="pos@ABC")
    annotationIDcounter = makingMorphLemmaPosGloss('pos', tierPos, annotationIDcounter)

    tierRus = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-rusT", PARENT_REF="orth@ABC", LANG_REF='ru', TIER_ID="ft-rus@ABC")
    tierHun = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-hunT", PARENT_REF="orth@ABC", LANG_REF='hu', TIER_ID="ft-hun@ABC")
    tierEng = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-engT", PARENT_REF="orth@ABC", LANG_REF='en', TIER_ID="ft-eng@ABC")
    tierFin = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-finT", PARENT_REF="orth@ABC", LANG_REF='fi', TIER_ID="ft-fin@ABC")
    tierDeu = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-deuT", PARENT_REF="orth@ABC", LANG_REF='de', TIER_ID="ft-deu@ABC")
    for id in resultIdSentences:
        id_sentence = id[0]
        cursor.execute('select MIN(id_token), MAX(id_token) from flex_tokens join flex_sentences using (id_sentence) where id_text = %s and id_sentence = %s order by id_token', (id_text, id_sentence))
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
    #ltIpa = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="codeT", TIME_ALIGNABLE="false") #wir nicht benötigt?
    ltMorphVar = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="morph-varT", TIME_ALIGNABLE="false")

def makingTiersIPA(id_text, root, shortDialect):
    annotationIDcounter = 0
    #verschiedene Counter für die time slots
    tsCounter = 0
    tsCounterIntern = 0
    timeValueCounter = 0
    tsCounterStart = 0
    tsCounterEnd = 0

    #language attribute festlegen
    if shortDialect.endswith('M') == True or shortDialect.endswith('V') == True:
        lang = 'mns'
    if shortDialect.endswith('K') == True or shortDialect.endswith('A') == True:
        lang = 'kca'

    #aktuellsten IPA-Text finden
    cursor.execute('SELECT max(id_IPA) FROM `ipa` where id_text = %s;',(id_text))
    resultLatestIPA = cursor.fetchone()

    cursor.execute('select IPA_text from ipa where id_IPA ='+str(resultLatestIPA[0]))
    resultIPAtext = cursor.fetchone()
    ipa = resultIPAtext[0]
    #Anzahl der Wörter für Anzahl der benötigten time slots berechnen --> ein Wort hat einen time slot
    numTS =  len(ipa.split())
        #Liste mit Sätzen aus dem IPA-Text gernerieren
    for char in ['#.#', '#!#', '#?#']: #Delimiter für Sätze festlegen
        if char in ipa:
            ipa = ipa.replace(char, char[1]+'endmarker')
    listSents = re.split('endmarker',ipa)

        #XML
    timeOrder = SubElement(root, 'TIME_ORDER')
        #so viele time slots anlegen, wie es Wörter gibt
    tsRef = 0
    for x in range(0, numTS+len(listSents)):
        timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(tsRef), TIME_VALUE=str(timeValueCounter))
        tsRef += 1
        timeValueCounter += 400

    tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@ABC")
    annotation = SubElement(tierRef, 'ANNOTATION')
    alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts0', TIME_SLOT_REF2='ts1')
    annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
    annotationValue.text = id_text
    annotationIDcounter += 1

    tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", LANG_REF=lang, PARENT_REF="ref@ABC", TIER_ID="orth@ABC")
    tierWord = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="wordT", LANG_REF=lang, PARENT_REF="orth@ABC", TIER_ID="word@ABC")
        #Sätze erstellen
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
            #Wörter erstellen
        for word in listWords:
            if word != '':
                annotation = SubElement(tierWord, 'ANNOTATION')
                alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(annotationIDcounter), TIME_SLOT_REF1='ts'+str(tsCounterWord), TIME_SLOT_REF2='ts'+str(tsCounterWord+1))
                annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
                annotationValue.text = word
                annotationIDcounter += 1
                tsCounterWord += 1

        #linguistic types
    ltRef = SubElement(root, 'LINGUISTIC_TYPE', GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="refT", TIME_ALIGNABLE="true")
    ltOrth = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="orthT", TIME_ALIGNABLE="false")
    ltWord = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Subdivision", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="wordT", TIME_ALIGNABLE="false")

def makingELAN(id_text, publicGlossed):
    id_textInt = id_text
    id_text = str(id_text)
    #output file name generieren
    cursor.execute("select substring_index(dialect, ' ', -1) from documents_info where id_text like %s;",(id_text))
    result1 = cursor.fetchone()
    shortDialect = str(result1[0]).strip('(' ')')

    outputFile = open("ELANsFromTemplate/"+shortDialect+'_'+str(id_text)+".eaf","w",encoding="utf-8")

    #XML aufbauen
    root = Element('ANNOTATION_DOCUMENT', AUTHOR='', DATE=datetime.datetime.now(pytz.timezone('Europe/Paris')).isoformat(), FORMAT="2.8", VERSION="2.8")
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:noNamespaceSchemaLocation', "http://www.mpi.nl/tools/elan/EAFv2.8.xsd")
    header = SubElement(root, 'HEADER')#Attribute gelöscht: , MEDIA_FILE='', TIME_UNITS="milliseconds", da deprecated bzw. nicht benötigt

    #feststellen, ob Annotationen, aus Flex oder aus IPA generiert werden
    if publicGlossed == 1:
        makingTiersFlex(id_text, root, shortDialect)
    if publicGlossed == 0 and id_textInt in resultIDtextINipaRaw:
        makingTiersIPA(id_text, root, shortDialect)

    #Sprachtypen anlegen
    if shortDialect.endswith('M') == True or shortDialect.endswith('V') == True:
        langMansi = SubElement(root, 'LANGUAGE', LANG_DEF="http://cdb.iso.org/lg/CDB-00131050-001", LANG_ID="mns", LANG_LABEL="Mansi (mns)")
    if shortDialect.endswith('K') == True or shortDialect.endswith('A') == True:
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

    #Leerzeichen einfügen, um das Dokument lesbarer zu machen:
    rough_string = ET.tostring(root, 'utf-8')
    dom = minidom.parseString(rough_string)
    #eigene processing instruction einfügen
    pi = dom.createProcessingInstruction('xml version="1.0"', 'encoding="UTF-8"')
    root = dom.firstChild
    dom.insertBefore(pi, root)
    prettyXML = dom.toprettyxml()
    #automatische erzeugte XML processing instruction löschen
    stripped = prettyXML.lstrip('<?xml version="1.0" ?>')
    #1. Leerzeile entfernen
    strippedNewLine = stripped.lstrip()

    #print(strippedNewLine)
    outputFile.write(strippedNewLine)
    outputFile.close()

#test
#makingELAN(1129, 0) #für IPA
#makingELAN(741, 1) #für Flex

#alle Texte durchgehen
 for elem in resultIDtexts:
     idText = elem[0]
     publicGlossed = elem[1]
     makingELAN(idText, publicGlossed)
