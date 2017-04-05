#noch nciht fertig
#ELAN-Datei erstellen, die aussieht wie ELAN-template.etf
from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
import pymysql
#für Datum
import datetime
import pytz

##Verbindung zur DB aufbauen (noch ausfüllen)
dbObj = pymysql.connect(host = '', port = 0, user = '', passwd = '', db = 'babel', charset='utf8')
cursor = dbObj.cursor()
cursor.execute('select distinct id_text from documents_info order by id_text')
resultIDs = list(cursor)

def makingTiers(id_text, root, speaker):
    tierRef = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="refT", TIER_ID="ref@"+speaker)
    tierRef.text = id_text
    tierOrth = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="ref@"+speaker, TIER_ID="orth@"+speaker)#elan_sentence?
    tierWord = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="wordT", PARENT_REF="orth@"+speaker, TIER_ID="word@"+speaker)#form_token from Flex_tokens
    tierMorph = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="morphT", PARENT_REF="word@"+speaker, TIER_ID="morph@"+speaker)
    tierOrth2 = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="orthT", PARENT_REF="morph@"+speaker, TIER_ID="morph-var@"+speaker)
    tierLemma = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="lemmaT", PARENT_REF="morph@"+speaker, TIER_ID="lemma@"+speaker)
    tierGloss = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="glossT", PARENT_REF="lemma@"+speaker, TIER_ID="gloss@"+speaker)
    tierPos = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="posT", PARENT_REF="lemma@"+speaker, TIER_ID="pos@"+speaker)
    tierRus = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-rusT", PARENT_REF="orth@"+speaker, TIER_ID="ft-rus@"+speaker)
    tierHun = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-hunT", PARENT_REF="orth@"+speaker, TIER_ID="ft-hun@"+speaker)
    tierEng = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-engT", PARENT_REF="orth@"+speaker, TIER_ID="ft-eng@"+speaker)
    tierFin = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="ft-finT", PARENT_REF="orth@"+speaker, TIER_ID="ft-fin@"+speaker)
    tierIPA = SubElement(root, 'TIER', LINGUISTIC_TYPE_REF="codeT", PARENT_REF="ref@"+speaker, TIER_ID="code@"+speaker)
    cursor.execute("select distinct IPA_text from ipa where id_text like %s;",(id_text))
    ipa = cursor.fetchall()
    tierIPA.text = ipa[0]
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
    ltIpa = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="codeT", TIME_ALIGNABLE="false")
    ltMorphVar = SubElement(root, 'LINGUISTIC_TYPE', CONSTRAINTS="Symbolic_Association", GRAPHIC_REFERENCES="false", LINGUISTIC_TYPE_ID="morph-varT", TIME_ALIGNABLE="false")

def makingELAN(id_text):
    id_text = str(id_text)
    #alle IDs auslesen
    cursor.execute("select substring_index(dialect, ' ', -1) from documents_info where id_text like %s;",(id_text))
    result1 = cursor.fetchone()
    shortDialect = str(result1[0]).strip('(' ')')
    #outputFile = open("ELANsFromTemplate/testTemplate.eaf","w",encoding="utf-8")#zum Testeb
    #outputFile = open("ELANsFromTemplate/"+shortDialect+'_'+str(id_text)+".eaf","w",encoding="utf-8")

    cursor.execute('select distinct elan_speaker from elan_data where id_text = %s', (id_text))
    speakers = list(cursor)

    #XML aufbauen
    root = Element('ANNOTATION_DOCUMENT', AUTHOR='', DATE=datetime.datetime.now(pytz.timezone('Europe/Paris')).isoformat(), FORMAT="2.8", VERSION="2.8")
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    root.set('xsi:noNamespaceSchemaLocation', "http://www.mpi.nl/tools/elan/EAFv2.8.xsd")
    header = SubElement(root, 'HEADER', MEDIA_FILE='', TIME_UNITS="milliseconds")
    timeOrder = SubElement(root, 'TIME_ORDER')
    for elem in speakers:
        speaker = elem[0]
        #print(speaker)
        makingTiers(id_text, root, speaker)
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

    print(strippedNewLine)
    # outputFile.write(strippedNewLine)
    # outputFile.close()

#test
makingELAN(1469)
# for elem in resultIDs:
#     elemValue = elem[0]
#     makingELAN(elemValue)