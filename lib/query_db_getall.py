import os
import json
import pprint
import time
from xml.etree import ElementTree as ET
import templates
import common
import sqlite3
from PySide import QtCore



class queryDbGetAll:
    
    def set_values(self,curdir,configxml,dbpath):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        self.lib = common.common() 
        self.templates = templates.templates()
        
        
        
    def go(self,what):
        conn = sqlite3.connect(self.dbpath)
        c = conn.cursor()
        
        html = self.templates.get_common_html(self.curdir)

        body = html.find('body')
        body.attrib['data-mode'] = 'front'
        body.attrib['data-what'] = what
        body.attrib['data-navletterslocation'] = 'file://' + os.path.join(self.curdir,'js', 'navletters.js')
        
        goback = ET.SubElement(body, 'div')
        goback.attrib['id'] = 'goback' 
        homelink = ET.SubElement(goback, 'a')
        homelink.attrib['href'] = 'file://' + os.path.join(self.curdir, 'index.html')
        homelink.text = 'Hall'
        
        wrapper = ET.SubElement(body, 'div')
        wrapper.attrib['id'] = 'frontWrapper'

        self.get_front_divs(what,c,wrapper)
        return ET.tostring(html)
    
    
    
    def get_front_divs(self,what,c,wrapper):
        c.execute('SELECT * FROM soundsz ORDER BY '+what)
        c.row_factory = sqlite3.Row

        whats = []
        for row in c:
            tempwhat = row[str(what)]
            haspic = row[13]
            full_url = row[10]

            if tempwhat not in whats and tempwhat != 'not':
                whats.append(tempwhat)
                img_src = 'file://'+os.path.join(self.curdir, 'res', 'default_small.png')
                
                if haspic == str(1):
                    img_src = 'file://'+os.path.join(os.path.dirname(full_url), 'folder_small.jpg')
                    
                div = ET.SubElement(wrapper,'div')
                div.attrib['class'] = 'launchQueryFront'
                div.attrib['data-detail'] = tempwhat
                img = ET.SubElement(div, 'img', {'src':img_src})
                span = ET.SubElement(div, 'span')
                span.text = self.lib.getShortString(25,tempwhat)
                
                
                
                
                
                
                
                