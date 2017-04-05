#ELAN-Datei aus Tabelle elan_data erstellen, das aussieht wie YK_1469_AZ_katnaj.eaf von Zsofia
from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
import pymysql
#für Datum
import datetime
import pytz

listTimeSlots = []
dictTimeSlots = {}

##Verbindung zur DB aufbauen (noch ausfüllen)
dbObj = pymysql.connect(host = '', port = 0, user = '', passwd = '', db = 'babel', charset='utf8')
cursor = dbObj.cursor()
cursor.execute('select distinct id_text from documents_info order by id_text')
resultIDs = list(cursor)

def makingELAN(id_text):
    #output file anlegen
    id_text = str(id_text)
    #alle IDs auslesen
    cursor.execute("select substring_index(dialect, ' ', -1) from documents_info where id_text like %s;",(id_text))
    result1 = cursor.fetchone()
    shortDialect = str(result1[0]).strip('(' ')')
    outputFile = open("ELANs/"+shortDialect+'_'+str(id_text)+".eaf","w",encoding="utf-8")

    #sql-befehle
    #time slots generieren
    cursor.execute('select time_code, time_code_end from elan_data where id_text = %s order by time_code, time_code_end', (id_text))
    times = list(cursor)
    for elem in times:
        listTimeSlots.append(elem[0]) #*1000 gelöscht
        listTimeSlots.append(elem[1])
    listTimeSlots.sort()

    #XML aufbauen
    root = Element('ANNOTATION_DOCUMENT', AUTHOR='', DATE=datetime.datetime.now(pytz.timezone('Europe/Paris')).isoformat(), FORMAT="2.8", VERSION="2.8")
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:noNamespaceSchemaLocation', "http://www.mpi.nl/tools/elan/EAFv2.8.xsd")
    header = SubElement(root, 'HEADER', MEDIA_FILE='', TIME_UNITS="milliseconds")
    mediaDescriptor = SubElement(header, 'MEDIA_DESCRIPTOR', MEDIA_URL='file:///Users/axel/Documents/Arbeit/momat/__Medientests/bild1.png', MIME_TYPE="image/png", RELATIVE_MEDIA_URL="../../momat/__Medientests/bild1.png")
    property1 = SubElement(header, 'PROPERTY', NAME="URN")
    property1.text = 'urn:nl-mpi-tools-elan-eaf:868d7ae2-9e36-4b05-b225-a8e633b126a1'
    property2 = SubElement(header, 'PROPERTY', NAME="lastUsedAnnotationId")
    property2.text = '37'
    timeOrder = SubElement(root, 'TIME_ORDER')
    #time slots in Elemente eintragen
    ts = 1
    i = 0
    while ts <= len(listTimeSlots):
        timeSlot = SubElement(timeOrder, 'TIME_SLOT', TIME_SLOT_ID='ts'+str(ts), TIME_VALUE=str(round(listTimeSlots[i]*1000)))
        dictTimeSlots[listTimeSlots[i]] = 'ts'+str(ts)
        ts += 1
        i += 1

    cursor.execute('select distinct elan_speaker from elan_data where id_text = %s', (id_text))
    tiers = list(cursor)

    for elem in tiers:
        tier = SubElement(root,'TIER', LINGUISTIC_TYPE_REF="default-lt", TIER_ID=elem[0])
        tierName = elem[0]
        cursor.execute("select nr_sentence from elan_data where elan_speaker = %s and id_text = %s", (tierName, id_text))
        listNr_sentence = list(cursor)
        for a in range(0, len(listNr_sentence)):
            annotation = SubElement(tier, 'ANNOTATION')
            rawNr_sentence = listNr_sentence[a][0]
            cursor.execute("select time_code, time_code_end from elan_data where nr_sentence = %s and id_text = %s", (rawNr_sentence, id_text))
            timePair = cursor.fetchone()
            start = timePair[0]
            end = timePair[1]
            if start in dictTimeSlots:
                startEntry = dictTimeSlots[start]
            if end in dictTimeSlots:
                endEntry = dictTimeSlots[end]
            alignableAnnotation = SubElement(annotation, 'ALIGNABLE_ANNOTATION', ANNOTATION_ID='a'+str(rawNr_sentence), TIME_SLOT_REF1=startEntry, TIME_SLOT_REF2=endEntry)
            annotationValue = SubElement(alignableAnnotation, 'ANNOTATION_VALUE')
            cursor.execute("select elan_sentence from elan_data where nr_sentence = %s and id_text = %s", (rawNr_sentence, id_text))
            sentence = cursor.fetchone()
            annotationValue.text = sentence[0]

    linguisticType = SubElement(root, 'LINGUISTIC_TYPE', GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="default-lt", TIME_ALIGNABLE="true")
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
    #automatische erzeugte fügt XML processing instruction löschen
    stripped = prettyXML.lstrip('<?xml version="1.0" ?>')
    #1. Leerzeile entfernen
    strippedNewLine = stripped.lstrip()

    outputFile.write(strippedNewLine)
    outputFile.close()

for elem in resultIDs:
    elemValue = elem[0]
    makingELAN(elemValue)