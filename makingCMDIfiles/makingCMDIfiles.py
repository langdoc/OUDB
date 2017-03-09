# -*- coding: utf-8 -*-
#Modul für MySQL-Schnittstelle in Python
import pymysql
from pymysql import connect, err, sys, cursors

#Verbindung zur DB aufbauen (noch ausfüllen)
dbObj = pymysql.connect(host = '', port = 0, user = '', passwd = '', db = 'babel', charset='utf8')
cursor = dbObj.cursor();
#alle IDs auslesen
cursor.execute('select distinct id_text from documents_info order by id_text')
resultIDs = list(cursor)

def makingCMDIfile(id_text):
      id_text = str(id_text)

      #Dateien mit Teilen für .cmdi-Datei öffnen
      file1 = open("xml1.xml","r",encoding="utf-8")
      file2 = open("xml2.xml","r",encoding="utf-8")
      file3 = open("xml3.xml","r",encoding="utf-8")
      file4 = open("xml4.xml","r",encoding="utf-8")
      file5 = open("xml5.xml","r",encoding="utf-8")
      xml1 = file1.read()
      xml2 = file2.read()
      xml3 = file3.read()
      xml4 = file4.read()
      xml5 = file5.read()
      #Datei mit SQL-Abfrage für Informanten-Namen für YK
      fileState9 = open("SQLstatement9.sql","r",encoding="utf-8")
      textState9 = fileState9.read()

      cursor.execute("select substring_index(dialect, ' ', -1) from documents_info where id_text like %s;",(id_text))
      result1 = cursor.fetchone()
      shortDialect = str(result1[0]).strip('(' ')')

      #.cmdi-Datei anlegen
      outputFile = open("CMDIs/"+shortDialect+'_'+str(id_text)+".cmdi","w",encoding="utf-8")

      #SQL-Befehle ausführen
      cursor.execute('select id_text from documents_info where id_text like %s;',(id_text))
      result2 = cursor.fetchone()
      cursor.execute('select title_vernacular from documents_info where id_text like %s;',(id_text))
      result3 = cursor.fetchone()
      cursor.execute("select if(rec_date,rec_date,'Unspecified') from documents_info where id_text like %s;",(id_text))
      result4 = cursor.fetchone()
      cursor.execute('select genre_content from documents_info where id_text like %s;',(id_text))
      result5 = cursor.fetchone()
      cursor.execute("select IF(dialect regexp 'khanty','ISO639-3:kca', 'ISO639-3:mns') from documents_info where id_text like %s;",(id_text))
      result6 = cursor.fetchone()
      cursor.execute("select IF(dialect regexp 'khanty','Khanty', 'Mansi') from documents_info where id_text like %s;",(id_text))
      result7 = cursor.fetchone()
      cursor.execute('select dialect from documents_info where id_text like %s;',(id_text))
      result8 = cursor.fetchone()

      cursor.execute(textState9 +' '+id_text)
      result9 = cursor.fetchone()
      result9Clean = ''
      for i in range(1, len(result9)):
            if result9[i] != '':
                  result9Clean += result9[i]

      cursor.execute('select collector from documents_info where id_text like %s;',(id_text))
      result10 = cursor.fetchone()

      #CMDI mit Ergebnissen aus SQL-Befehlen zusammenstellen & in Datei schreiben
      fileCMDI = str(xml1+shortDialect+'_'+str(result2[0])+'</Name>\n'+' '*9+'<Title>'+result3[0]+
      '</Title>\n'+' '*9+'<Date>'+result4[0]+'</Date>'+xml2+result5[0]+'</Genre> \n'+' '*16+'<CommunicationContext/>\n'+' '*15+
      '<Content_Languages>\n'+' '*18+'<Content_Language>\n'+
      ' '*21+'<Id>'+result6[0]+'</Id>\n'+' '*21+'<Name>'+result7[0]+
      '</Name>\n'+' '*21+'<descriptions>\n'+' '*24+'<Description>'+result8[0]+'</Description>\n'
      +xml3+result9Clean+'</Name>\n'+xml4+result10[0]+'</Name>\n'+xml5)

      outputFile.write(fileCMDI)
      outputFile.close()

#für jeden Datensatz (id_text) eine .cmdi-Datei erstellen
for elem in resultIDs:
      elemValue = elem[0] #elemValue ist eine id_text
      makingCMDIfile(elemValue)
