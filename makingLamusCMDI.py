# -*- coding: utf-8 -*-
from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, ElementTree
#Verbindung zur Datenbank
import pymysql
from pymysql import connect, err, sys, cursors
#from pymysql.cursors import DictCursor
from ZugangsdatenDB import getZugangsdaten

hostname, portname, username, passwdname, dbname = getZugangsdaten()

#Verbindung zur DB aufbauen
dbObj = pymysql.connect(host = hostname, port = portname, user = username, passwd = passwdname, db = dbname, charset='utf8')
cursor = dbObj.cursor()

cursor.execute('Select id_text, dialect, title_vernacular, genre_content, informant, collector, public_glossed from documents_info where public = 1')
listDocInfo = list(cursor)

#audio
cursor.execute("Select DISTINCT elan_data.id_text, audio_filename, audio_size from elan_data inner join digital_resources on elan_data.id_text = digital_resources.id_text where elan_speaker = 'default' and nr_wav_file = 1 and audio_filename regexp '.wav$' order by id_text")
audioList = list(cursor)
audioDict = {}
for elem in audioList:
    audioDict[elem[0]] = elem[1], elem[2]

for singleText in listDocInfo:
    idText = singleText[0]
    dialect = singleText[1]
    title = singleText[2]
    genre = singleText[3]
    informant = singleText[4]
    collector = singleText[5]
    ipa = singleText[6]
    nameAbbreviation = dialect[-3:-1]
    filenameElan = nameAbbreviation + '_'+str(idText)+ '.eaf'
    if dialect[-2] == 'K':
        dialectOberbegriff = 'Khanty'
        iso = 'ISO639-3:kca'
    if dialect[-2] == 'M':
        dialectOberbegriff = 'Mansi'
        iso = 'ISO639-3:mns'

    #XML aufbauen
    root = Element('CMD', CMDVersion='1.1', xmlns="http://www.clarin.eu/cmd/")
    root.set('xmlns:cmd', 'http://www.clarin.eu/cmd/')
    root.set('xmlns:functx', "http://www.functx.com")
    root.set('xmlns:imdi',"http://www.mpi.nl/IMDI/Schema/IMDI")
    root.set('xmlns:iso', "http://www.iso.org/")
    root.set('xmlns:lat', "http://lat.mpi.nl/")
    root.set('xmlns:sil', "http://www.sil.org/")
    root.set('xmlns:xs', "http://www.w3.org/2001/XMLSchema")
    root.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    root.set('xsi:schemaLocation', "http://www.clarin.eu/cmd/ http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/clarin.eu:cr1:p_1407745712035/xsd")
    
    header = SubElement(root, 'Header')
    mdCreator = SubElement(header, 'MdCreator')
    mdCreator.text = 'OUDB'
    mdCreationDate = SubElement(header, 'MdCreationDate')
    mdCreationDate.text = '2017-06-26'
    mdSelfLink = SubElement(header, 'MdSelfLink')
    mdProfile = SubElement(header, 'MdProfile')
    mdProfile.text = 'clarin.eu:cr1:p_1407745712035'
    mdCollectionDisplayName = SubElement(header, 'MdCollectionDisplayName')
    mdCollectionDisplayName.text = 'Donated Corpora : Permic Varieties'
    
    resourcesOben = SubElement(root, 'Resources')
    resourceProxyList = SubElement(resourcesOben, 'ResourceProxyList')
    resourceProxyText = SubElement(resourceProxyList, 'ResourceProxy', id='res1')
    resourceTypeText = SubElement(resourceProxyText, 'ResourceType', mimetype="text/x-eaf+xml")
    resourceTypeText.text = 'Resource'
    resourceRefText = SubElement(resourceProxyText, 'ResourceRef')
    resourceRefText.set('lat:localURI', filenameElan)
    resourceRefText.text = filenameElan
    journalFileProxyList = SubElement(resourcesOben, 'JournalFileProxyList')
    resourceRelationList = SubElement(resourcesOben, 'ResourceRelationList')
    
    components = SubElement(root, 'Components')
    latSession = SubElement(components, 'lat-session')
    history = SubElement(latSession, 'History')
    nameComponents = SubElement(latSession, 'Name')
    nameComponents.text = nameAbbreviation+'_'+str(idText)
    titleElement = SubElement(latSession, 'Title')
    titleElement.text = title
    dateLat = SubElement(latSession, 'Date')
    dateLat.text = 'Unspecified'
    descriptionSmall = SubElement(latSession, 'descriptions')
    descriptionBig = SubElement(descriptionSmall, 'Description')
    descriptionBig.text = dialect
    location = SubElement(latSession, 'Location')
    continent = SubElement(location, 'Continent')
    continent.text = 'Asia'
    country = SubElement(location, 'Country')
    country.text = 'Russian Federation'
    region = SubElement(location, 'Region')
    address = SubElement(location, 'Address')
    project = SubElement(latSession, 'Project')
    nameProject = SubElement(project, 'Name')
    contact = SubElement(project, 'Contact')
    content = SubElement(latSession, 'Content')
    genreContent = SubElement(content, 'Genre')
    #genreContent.text = genre
    subGenre = SubElement(content, 'SubGenre')
    subGenre.text = 'Unspecified'
    task = SubElement(content, 'Task')
    task.text = 'Unspecified'
    modal = SubElement(content, 'Modalities')
    subject = SubElement(content, 'Subject')
    comContext = SubElement(content, 'CommunicationContext')
    interactivity = SubElement(comContext, 'Interactivity')
    interactivity.text = 'Unspecified'
    planningType = SubElement(comContext, 'PlanningType')
    planningType.text = 'Unspecified'
    involvement = SubElement(comContext, 'Involvement')
    involvement.text = 'Unspecified'
    socialContext = SubElement(comContext, 'SocialContext')
    socialContext.text = 'Unspecified'
    eventStructure = SubElement(comContext, 'EventStructure')
    eventStructure.text = 'Unspecified'
    channel = SubElement(comContext, 'Channel')
    channel.text = 'Unspecified'
    contentLangS = SubElement(content, 'Content_Languages')
    contentLang = SubElement(contentLangS, 'Content_Language')
    idIso = SubElement(contentLang, 'Id')
    idIso.text = iso
    nameContentLang = SubElement(contentLang, 'Name')
    nameContentLang.text = dialectOberbegriff
    dominant = SubElement(contentLang, 'Dominant')
    dominant.text = 'Unspecified'
    sourceLang = SubElement(contentLang, 'SourceLanguage')
    targetLang = SubElement(contentLang, 'TargetLanguage')
    
    actors = SubElement(latSession, 'Actors')
    actor1 = SubElement(actors, 'Actor')
    roleActor1 = SubElement(actor1, 'Role')
    roleActor1.text = 'Speaker/Signer'
    nameActor1 = SubElement(actor1, 'Name')
    nameActor1.text = informant
    familySocRole = SubElement(actor1, 'FamilySocialRole')
    familySocRole.text = 'Unspecified'
    ethnicGroup = SubElement(actor1, 'EthnicGroup')
    ethnicGroup.text = 'Unspecified'
    birthdate = SubElement(actor1, 'BirthDate')
    birthdate.text = '0000'
    sex = SubElement(actor1, 'Sex')
    sex.text = 'Unspecified'
    education = SubElement(actor1, 'Education')
    age = SubElement(actor1, 'Age')
    
    actor2 = SubElement(actors, 'Actor')
    roleActor2 = SubElement(actor2, 'Role')
    roleActor2.text = 'Collector'
    nameActor2 = SubElement(actor2, 'Name')
    nameActor2.text = collector
    familySocRole = SubElement(actor2, 'FamilySocialRole')
    familySocRole.text = 'Unspecified'
    ethnicGroup = SubElement(actor2, 'EthnicGroup')
    ethnicGroup.text = 'Unspecified'
    birthdate = SubElement(actor2, 'BirthDate')
    birthdate.text = '0000'
    sex = SubElement(actor2, 'Sex')
    sex.text = 'Unspecified'
    education = SubElement(actor2, 'Education')
    age = SubElement(actor2, 'Age')

    #neu:
    nameProject.text = 'OUDB'
    sourceLang.text = 'Unspecified'
    targetLang.text = 'Unspecified'

    resourcesUnten = SubElement(latSession, 'Resources')

    if idText in audioDict.keys():
        filenameAudio = audioDict[idText][0]
        size = audioDict[idText][1]

        resourceProxyAudio = SubElement(resourceProxyList, 'ResourceProxy', id='res2')
        resourceTypeAudio = SubElement(resourceProxyAudio, 'ResourceType', mimetype="audio/x-wav")
        resourceTypeAudio.text = 'Resource'
        resourceRefAudio = SubElement(resourceProxyAudio, 'ResourceRef')
        resourceRefAudio.set('lat:localURI', filenameAudio)
        resourceRefAudio.text = filenameAudio

        mediaFile = SubElement(resourcesUnten, 'MediaFile', ref='res2')
        typeMediaFile = SubElement(mediaFile, 'Type')
        formatMediaFile = SubElement(mediaFile, 'Format')
        formatMediaFile.text = 'audio/x-wav'
        sizeMediaFile = SubElement(mediaFile, 'Size')
        #sizeMediaFile.text = str(size)
        quality = SubElement(mediaFile, 'Quality')
        quality.text = 'Unspecified'
        recConditions = SubElement(mediaFile, 'RecordingConditions')
        timePos = SubElement(mediaFile, 'TimePosition')
        start = SubElement(timePos, 'Start')
        start.text = 'Unspecified'
        end = SubElement(timePos, 'End')
        end.text = 'Unspecified'

        #neu:
        typeMediaFile.text = 'audio'


    writtenResource = SubElement(resourcesUnten, 'WrittenResource')
    writtenResource.set('ref', 'res1')
    dateWrittenRes = SubElement(writtenResource, 'Date')
    dateWrittenRes.text = 'Unspecified'
    typeWrittenRes = SubElement(writtenResource, 'Type')
    typeWrittenRes.text = 'document'
    subTypeWrittenRes = SubElement(writtenResource, 'SubType')
    formatWrittenRes = SubElement(writtenResource, 'Format')
    formatWrittenRes.text = 'text/x-eaf+xml'
    sizeWrittenRes = SubElement(writtenResource, 'Size')
    derivationWrittenRes = SubElement(writtenResource, 'Derivation')
    derivationWrittenRes.text = 'Unspecified'
    charEncoding = SubElement(writtenResource, 'CharacterEncoding')
    charEncoding.text = 'Unspecified'
    contentEncoding = SubElement(writtenResource, 'ContentEncoding')
    contentEncoding.text = 'Unspecified'
    langID = SubElement(writtenResource, 'LanguageId')
    anonym = SubElement(writtenResource, 'Anonymized')
    validation = SubElement(writtenResource, 'Validation')
    typeValidation = SubElement(validation, 'Type')
    methodValidation = SubElement(validation, 'Methodology')
    level = SubElement(validation, 'Level')
    access = SubElement(writtenResource, 'Access')
    availability = SubElement(access, 'Availability')
    availability.text = 'Unspecified'
    dateAccess = SubElement(access, 'Date')
    dateAccess.text = 'Unspecified'
    owner = SubElement(access, 'Owner')
    publisher = SubElement(access, 'Publisher')
    references = SubElement(latSession, 'References')
    #neu:
    langID.text = 'Unspecified'
    anonym.text = 'Unspecified'
    anonym.text = 'Unspecified'
    typeValidation.text = 'Unspecified'
    methodValidation.text = 'Unspecified'
    level.text = 'Unspecified'
    owner.text = 'Unspecified'
    publisher.text = 'Unspecified'


    #neu:
    contact2 = SubElement(access, 'Contact')



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
	
    if idText not in audioDict.keys() and ipa == 0:
        outputFile = open("ipaOnlyCMDI/"+nameAbbreviation+"_" +str(idText)+".cmdi","w",encoding="utf-8")
        outputFile.write(strippedNewLine)
        outputFile.close()
    if idText not in audioDict.keys() and ipa == 1:
        outputFile = open("flexOnlyCMDI/"+nameAbbreviation+"_" +str(idText)+".cmdi","w",encoding="utf-8")
        outputFile.write(strippedNewLine)
        outputFile.close()
    if idText in audioDict.keys() and ipa == 0:
        outputFile = open("ipaAudioCMDI/"+nameAbbreviation+"_" +str(idText)+".cmdi","w",encoding="utf-8")
        outputFile.write(strippedNewLine)
        outputFile.close()
    if idText in audioDict.keys() and ipa == 1:
        outputFile = open("flexAudioCMDI/"+nameAbbreviation+"_" +str(idText)+".cmdi","w",encoding="utf-8")
        outputFile.write(strippedNewLine)
        outputFile.close()
