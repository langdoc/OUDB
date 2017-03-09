select IF((SELECT informant REGEXP 'Kayukova, Aleksandra Ivanovna [[:punct:]]Taylakova'), 'AIK ' , ""), 
IF((SELECT informant REGEXP 'Kayukova, Alyona Izokovna [[:punct:]]Komplanteeva'), 'AJK ' , ""),
IF((SELECT informant REGEXP 'Multanova, Anna Izokovna [[:punct:]]Komplanteeva'), 'AJM ' , ""), 
IF((SELECT informant REGEXP 'Kaymysova, Evdokiya Nikolaevna [[:punct:]]Kayukova'), 'ENK ' , ""), 
IF((SELECT informant REGEXP 'Pokacheeva, Yulya Fyodorovna [[:punct:]]Karaeva'), 'JFP ' , ""), 
IF((SELECT informant REGEXP 'Kayukova, Lyudmila Nikolaevna'), 'LNK ' , ""), 
IF((SELECT informant REGEXP 'Achimova, Margarita Dmitrievna  [[:punct:]]Kaymisova'), 'MDA ' , ""), 
IF((SELECT informant REGEXP 'Kurlomkina, Natalya Petrovna'), 'NPA' , ""), 
IF((SELECT informant REGEXP 'Lantina, Ol\'ga Aleksandrovna'), 'OAK' , ""), 
IF((SELECT informant REGEXP 'Kayukova, Praskovya Danilovna [[:punct:]]Kel\'mina'), 'OAL' , ""), 
IF((SELECT informant REGEXP 'Kayukova, Ol\'ga Antonovna [[:punct:]]Kel\'mina'), 'PDK' , ""), 
IF((SELECT informant REGEXP 'Nyuglomkina, Polina Ivanovna [[:punct:]]Bysarkina'), 'PIN' , ""), 
IF((SELECT informant REGEXP 'Kayukova, Svetlana Petrovna'), 'SPK' , ""), 
IF((SELECT informant REGEXP 'Kayukova, Tatyana Aleksandrovna'), 'TAK' , ""), 
IF((SELECT informant REGEXP 'Kurlomina, Taisiya Mikhaylovna [[:punct:]]Yarsomova'), 'TMJ' , ""), 
IF((SELECT informant REGEXP 'Kel\'mina, Tat\'yana Mikhaylovna [[:punct:]]Kaymysova'), 'TMK' , ""),
IF((SELECT informant REGEXP 'Usanov, Vasiliy Ivanovich'), 'VIU' , "") from documents_info where id_text like