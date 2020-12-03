# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 12:39:54 2020

@author: thde00
"""

import os
path = input("Enter path: \n > ")
# path = 'C:\\Users\\thde00\\wiktionaries\\es_wiktionary'
#path = 'C:\\Users\\thde00\\wiktionaries\\nl_wiktionary'
#path = 'C:\\Users\\thde00\\wiktionaries\\en_wiktionary'
#path = "Z:\\PROJECTS\\Pret-a-LLOD\\WPs\\WP3\\WordNets\\orbn_n-v-a.xml\\orbn_n-v-a_single_files"
#path = "C:\\Users\\thde00\\Desktop\\WordNets\\odwn\\odwn_orbn_gwg.LMF_1.3_files"
files = os.listdir(path)
keyword = 'Kiefer' # to search for a specific word?
#keyword = 'form-spelling="namen en rugnummers"'
for file in files:
    f=open(os.path.join(path,file),'r', encoding="utf8")
    for x in f:
        if keyword in x:
            print(keyword, " : ",f)
    f.close()