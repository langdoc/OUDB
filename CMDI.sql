

select concat(replace(substring_index(dialect,'(',-1),')',''),"_",id_text) cmdi_name,concat("<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<CMD xmlns=\"http://www.clarin.eu/cmd/\"
     xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"
     CMDVersion=\"1.1\"
     xsi:schemaLocation=\"http://www.clarin.eu/cmd/ http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/clarin.eu:cr1:p_1271859438204/xsd \">
   <Header>
      <MdCreator>axel</MdCreator>
      <MdCreationDate>2017-02-01+01:00</MdCreationDate>
      <MdProfile>clarin.eu:cr1:p_1271859438204</MdProfile>
   </Header>
   <Resources>
      <ResourceProxyList/>
      <JournalFileProxyList/>
      <ResourceRelationList/>
   </Resources>
   <Components>
      <Session>
         <Name>",
         replace(substring_index(dialect,'(',-1),')',''),"_",id_text,
         "</Name>
         <Title>iːttən əntə nɛripti (AJM)</Title>
         <Date>",
         IF(rec_date,rec_date,'Unspecified'),
         "</Date>
         <MDGroup>
            <Location>
               <Continent>Asia</Continent>
               <Country>Russian Federation</Country>
            </Location>
            <Project>
               <Name>OUDB</Name>
               <Title/>
               <Id/>
               <Contact>
                  
               </Contact>
            </Project>
            <Keys/>
            <Content>
               <Genre>",
               genre_content,
               "</Genre>
               <CommunicationContext/>
               <Content_Languages>
                  <Content_Language>
                     <Id>ISO639-3:kca</Id>
                     <Name>Khanty</Name>
                     
                     <descriptions>
                        <Description>yugan khanty (YK)</Description>
                     </descriptions>
                  </Content_Language>
               </Content_Languages>
               <Keys/>
            </Content>
            <Actors>
               <Actor>
                  <Role>Speaker/Signer</Role>
                  <Name>OAL</Name>
                  <FullName/>
                  <Code/>
                  <FamilySocialRole/>
                  <EthnicGroup/>
                  <Age>Unspecified</Age>
                  <BirthDate>Unspecified</BirthDate>
                  <Sex>Unspecified</Sex>
                  <Education/>
                  <Anonymized>Unspecified</Anonymized>
                  <Keys/>
                  <Actor_Languages/>
               </Actor>
               <Actor>
                  <Role>Collector</Role>
                  <Name>Zsófia Schön</Name>
                  <FullName/>
                  <Code/>
                  <FamilySocialRole/>
                  <EthnicGroup/>
                  <Age>Unspecified</Age>
                  <BirthDate>Unspecified</BirthDate>
                  <Sex>Unspecified</Sex>
                  <Education/>
                  <Anonymized>Unspecified</Anonymized>
                  <Keys/>
                  <Actor_Languages/>
               </Actor>
            </Actors>
         </MDGroup>
         <Resources>
            
         </Resources>
      </Session>
   </Components>
</CMD>
") cmdi_content from documents_info
