#!/usr/bin/env python
from __future__ import division
from xml.etree import ElementTree as ET
import threading
import sqlite3
import sys
import os
import time

from PySide import QtCore
from PySide import QtGui
from PySide import QtWebKit
from PySide import QtNetwork

import lib.common
import lib.query_db
import lib.build_db
import lib.play_files
import lib.add_2_playlist
import lib.myconfig

# Todo:

#    - Make hover buttons to scroll down and up


  


class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.lib = lib.common.common() 

        self.curdir = self.get_app_dir()
        self.configxml = self.lib.getXml(os.path.join(self.curdir, 'config.xml'))
        self.dbpath = os.path.join(self.curdir, 'res', 'data.db')
        
        self.resize(1200, 700)
        self.setWindowTitle('New Soundsz')
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.curdir,'res','app_icon.png')))
        self.center()
        
        self.buildDB = lib.build_db.buildDb()
        self.buildDB.set_values(self.curdir, self.configxml,self.dbpath)
        self.buildDB.postBuildDbSig.connect(self.buildDB_update_status)
        self.buildDB.startBuildDbSig.connect(self.buildDB_start)
        self.buildDB.endBuildDbSig.connect(self.buildDB_end)

        self.queryDB = lib.query_db.queryDb()
        self.queryDB.set_values(self.curdir, self.configxml,self.dbpath)
        self.queryDB.postQueryDbSig.connect(self.queryDB_post_query)
        self.queryDB.startQueryDbSig.connect(self.queryDB_start)
        self.queryDB.endQueryDbSig.connect(self.queryDB_end)

        self.setup_files = lib.play_files.setupFiles()
        self.add_2_playlist = lib.add_2_playlist.add2Playlist()
        self.myconfig = lib.myconfig.MyConfig()
        self.myconfig.set_values(self.curdir, self.configxml)
        self.myconfig.postQueryDbSig.connect(self.myconfig_post_query)
        self.theinit()



    def theinit(self):
        self.web = QtWebKit.QWebView(self)
        self.web.loadFinished.connect(self.web_load_end)

        self.web.setRenderHints(QtGui.QPainter.HighQualityAntialiasing |
                                QtGui.QPainter.SmoothPixmapTransform |
                                QtGui.QPainter.TextAntialiasing)

        self.websettings = self.web.settings()
        self.websettings.setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, 7)

        start_page = os.path.join(self.curdir,'index.html')
        self.web.load(QtCore.QUrl(start_page))
        
        self.page = self.web.page()
        self.mainframe = self.page.mainFrame()
        self.mainframe.javaScriptWindowObjectCleared.connect(self.js_cleared)

        self.setCentralWidget(self.web)
        self.web.show()


    def myconfig_post_query(self, html):
        self.web.setHtml(html)  
        
        
    def queryDB_post_query(self, html):
        self.web.setHtml(html)
        
    def queryDB_start(self, html):
        self.web.setHtml(html)
        
    def queryDB_end(self, html):
        print('queryDB_end')
        
        
    def buildDB_update_status(self, total,current):
        self.results.setPlainText(str(total)+' of '+str(current))
         
    def buildDB_start(self, html):
        print('buildDB_start')
        self.results = self.mainframe.findFirstElement("div#results2")
        self.results.setPlainText('Starting...')
        
    def buildDB_end(self, html):
        print('buildDB_end')

        
          
        
    def web_load_end(self):
        print('wbLoadEnd')
        self.apply_events_front()
        self.setup_files_page()
        self.add_2_playlist_events()


    def add_2_playlist_events(self):
        tds = self.mainframe.findAllElements("td.add2Playlist").toList()
        self.add_2_playlist.set_values(self,self.mainframe, self.curdir, self.configxml,self.dbpath)
        for td in tds:
            td.evaluateJavaScript('''
                this.addEventListener('mouseup', function(e) { 
                    var track_src = this.parentNode.getAttribute('track_src');
                    add_2_playlist.go(track_src);
                },false);
                ''')


    def apply_events_front(self):
        body = self.mainframe.findFirstElement('body')
        for div in body.findAll('div.launchQueryFront').toList():
            div.evaluateJavaScript('''
                this.addEventListener('mouseup', function(e) { 
                    var what = document.body.getAttribute('data-what');
                    var detail = this.getAttribute('data-detail');
                
                    query_db.get_detail(what,detail);
                },false);
                ''')


    def setup_files_page(self):
        buttons = self.mainframe.findAllElements("div.wrpTopLevelDirLabel button").toList()
        self.setup_files.set_values(self.mainframe,self.configxml,self.curdir)
        for button in buttons:
            button.evaluateJavaScript('''
                this.addEventListener('mouseup', function(e) { 
                    var what2do = this.getAttribute('data-what2do');
                    var folder = this.parentNode.getElementsByTagName('span')[0];
                    var foldertext = folder.textContent;
                
                    setup_files.go(what2do,foldertext);
                },false);
                ''')
            
            
    def js_cleared(self):
        print('js cleared')
        self.mainframe.addToJavaScriptWindowObject("query_db", self.queryDB)
        self.mainframe.addToJavaScriptWindowObject("build_db", self.buildDB)
        self.mainframe.addToJavaScriptWindowObject("setup_files",self.setup_files)
        self.mainframe.addToJavaScriptWindowObject("add_2_playlist",self.add_2_playlist)
        self.mainframe.addToJavaScriptWindowObject("my_config",self.myconfig)

     
    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
        
              
    def keyPressEvent(self, event):
        '''This method does not need to be instanciated
        because self is a MainWindow.
        MainWindow looks for a keyPressEvent method'''
        print ("keyPressEvent : ",event.key())
        if event.key() == QtCore.Qt.Key_X:
            self.showFullScreen()
        if event.key() == QtCore.Qt.Key_C:
            self.showNormal()
        if event.key() == QtCore.Qt.Key_U:
               self.web.setZoomFactor(1.5)
        if event.key() == QtCore.Qt.Key_I:
               self.web.setZoomFactor(1)
        if event.key() == QtCore.Qt.Key_O:
               self.web.setZoomFactor(0.8)
               
               
               
    def about(self):
        info = "theBrowser"
        QtGui.QMessageBox.information(self, "Information", info)

        
        
    def get_app_dir(self):
        '''Get script or exe directory.'''
        if hasattr(sys, 'frozen'): #py2exe, cx_freeze
            app_path = os.path.dirname(sys.executable)
            print ('Executing exe', app_path)
        elif __file__: #source file          
            app_path = os.path.abspath(os.path.dirname(__file__))
            print ('Executing source file', app_path)
            
        return app_path 
       
       

       
       
       
if __name__ == "__main__":
    '''Get script or exe directory.'''
    app_path = ''
    if hasattr(sys, 'frozen'): #py2exe, cx_freeze
        app_path = os.path.dirname(sys.executable)
    elif __file__: #source file
        app_path = os.path.dirname(__file__)
    
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Soundsz")
    splash_pix = QtGui.QPixmap(os.path.join(app_path,'res','splash.png'))
    splash = QtGui.QSplashScreen(splash_pix)
    splash.setMask(splash_pix.mask())
    splash.show()

    #time.sleep(2)

    main = MainWindow()
    splash.finish(main)
    main.show()

    sys.exit(app.exec_())




        




