import os
import json
import pprint
import time
from xml.etree import ElementTree as ET

import templates
import common
import query_db_getall
import query_db_getdetail

import sqlite3
from PySide import QtCore

#        (Album text,
#        Artist text,
#        Track text,
#        Title text,
#        Date text,
#        Genre text,
#        Length text,
#        Sample_Rate text,
#        Bitrate text,
#        Filesize int,
#        Fullurl text,
#        TopLevel text,
#        HasDesc text,
#        HasPic text,
#        LastAcess int,
#        LastModification int,
#        MyRating text,
#        MyPlaylist text)''')    
        
class queryDbWorker(QtCore.QThread):
    postStringsWorkerSig = QtCore.Signal(str)


    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.lib = common.common() 
        self.templates = templates.templates()
        self.query_db_getall = query_db_getall.queryDbGetAll()
        self.query_db_getdetail = query_db_getdetail.queryDbGetDetail()


    def __del__(self):
        self.exiting = True


    def set_values(self, curdir, query, configxml, dbpath):
        self.curdir = curdir
        self.query = query
        self.configxml = configxml
        self.dbpath = dbpath
        self.query_db_getall.set_values(curdir, configxml, dbpath)
        self.query_db_getdetail.set_values(curdir, configxml, dbpath)
        
        
    def run(self):
        html = 'Hello'
        # Get all happens when index page item is choosen
        if self.query[0] == 'get_all':
            html = self.query_db_getall.go(self.query[1])
        # Get detail happens after the index page
        if self.query[0] == 'get_detail':
            html = self.query_db_getdetail.go(self.query[1], self.query[2])
        
        self.postStringsWorkerSig.emit(html)



class queryDb(QtCore.QObject):
    postQueryDbSig = QtCore.Signal(str)
    startQueryDbSig = QtCore.Signal(str)
    endQueryDbSig = QtCore.Signal(str)


    def set_values(self, curdir, configxml, dbpath):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
    
    
    @QtCore.Slot(str)
    def get_all(self, what):
        query = []
        query.append('get_all')
        query.append(what)
        self.call_thread(query)
        
        
    @QtCore.Slot(str, str)
    def get_detail(self, what, detail):
        query = []
        query.append('get_detail')
        query.append(what)
        query.append(detail)
        self.call_thread(query)
        
        
    def call_thread(self, query):
        self.query = query
        self.worker = queryDbWorker()
        self.worker.set_values(self.curdir, query, self.configxml, self.dbpath)
        self.worker.finished.connect(self.say_end)
        self.worker.started.connect(self.say_start)
        self.worker.postStringsWorkerSig.connect(self.post_html)
        self.worker.start()

        
        
        
    def say_end(self):
        self.endQueryDbSig.emit('End query')
        
    def say_start(self):
        # This is shown when querying something
        html = ET.Element('html')
        head = ET.SubElement(html, 'head')
        
        meta = ET.SubElement(head, 'meta')
        meta.attrib['http-equiv'] = 'content-type'
        meta.attrib['content'] = 'text/html; charset=utf-8'
        
        style = ET.SubElement(head, 'link')
        style.attrib['rel'] = 'stylesheet'
        style.attrib['type'] = 'text/css'
        style.attrib['href'] = 'file://' + os.path.join(self.curdir, 'style.css')
        
        goback = ET.SubElement(html, 'div', {'id':'goback'})
        span = ET.SubElement(goback, 'span', {'class':'novisibility'})
        span.text = 'iamherejustforshow'
        
        div = ET.SubElement(html, 'div', {'class':'loadingDiv'})
        for item in self.query:
            div2 = ET.SubElement(div, 'div')
            div2.text = item
            
        self.startQueryDbSig.emit(ET.tostring(html))
 
 
    def post_html(self, html):
        self.postQueryDbSig.emit(html)
        
        

        
        
        
        
        
        

