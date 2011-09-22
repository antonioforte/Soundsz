import os
import common
import sqlite3

from PySide import QtCore
from PySide import QtGui
from PySide import QtWebKit

'''
Popup a dialog thats allows to
associate tracks with playlists.

If the line edit does not have text, 
the associated playlist will be the one 
specified in the combobox.
'''


class add2PlaylistDialog(QtGui.QDialog):
    def __init__(self, parent,track_src,tracks,dbpath):
        QtGui.QDialog.__init__(self, parent)
        
        self.lib = common.common() 
        self.track_src = track_src
        self.tracks = tracks
        
        self.conn = sqlite3.connect(dbpath)
        c = self.conn.cursor()
        c.row_factory = sqlite3.Row

        self.setup_ui()
        self.label_track_src.setText(track_src)
        self.label_track_wrapper.setText(os.path.dirname(track_src))
        
        self.insert_existing_playlists(c)
        
        self.exec_()
        

        
    def insert_existing_playlists(self,c):
        c.execute('SELECT * FROM soundsz ORDER BY MyPlaylist') 
        playlists = []
        for row in c:
            if row['MyPlaylist'] not in playlists:
                self.playlist_chooser.addItem(row['MyPlaylist'])
                playlists.append(row['MyPlaylist'])
        return playlists
        
        
        
    def reject_dialog(self):
        self.lib.shout('add2PlaylistDialog.reject_dialog')
        self.close()

    
    def accept_dialog(self):
        what2insert = self.comboBox_what2add.currentText()
        c = self.conn.cursor()
        if what2insert == 'add track':
            self.insert_2_db(c,self.track_src)
            
        if what2insert == 'add all tracks':
            for item in self.tracks:
                self.insert_2_db(c,item)

        self.close()


        
    def insert_2_db(self,c,track_src):
        if len(self.lineEdit.text()) == 0:
            playlist_name = self.playlist_chooser.currentText()
        elif len(self.lineEdit.text()) > 0:
            playlist_name = self.lineEdit.text()
        else:
            playlist_name = 'not'
        
        self.lib.shout('add2PlaylistDialog.insert_2_db')
        self.lib.shout('playlist_name is',playlist_name)
        self.lib.shout('track_src is',track_src)
        
        c.execute('UPDATE soundsz SET MyPlaylist=? WHERE Fullurl=?',(playlist_name,track_src)) 
        self.conn.commit()

        
        
                
                
    def setup_ui(self):
        self.resize(300, 200)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)

        self.label_track_src = QtGui.QLabel(self)
        self.label_track_src.setText("track source")
        self.label_track_src.setObjectName("label_track_src")
        self.label_track_src.setSizePolicy(sizePolicy)
        self.gridLayout.addWidget(self.label_track_src, 0, 0, 1, 1)
        
        self.label_track_wrapper = QtGui.QLabel(self)
        self.label_track_wrapper.setText("track wrapper")
        self.label_track_wrapper.setSizePolicy(sizePolicy)
        self.label_track_wrapper.setObjectName("label_track_wrapper")
        self.gridLayout.addWidget(self.label_track_wrapper, 1, 0, 1, 1)
        
        self.comboBox_what2add = QtGui.QComboBox(self)
        self.comboBox_what2add.setObjectName("comboBox_what2add")
        self.comboBox_what2add.addItem("add track")
        self.comboBox_what2add.addItem("add all tracks")
        self.gridLayout.addWidget(self.comboBox_what2add, 2, 0, 1, 1)
        
        self.playlist_chooser = QtGui.QComboBox(self)
        self.playlist_chooser.setObjectName("playlist_chooser")
        self.gridLayout.addWidget(self.playlist_chooser, 2, 1, 1, 1)
        
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 3, 0, 1, 2)
        
        self.ok = QtGui.QPushButton(self)
        self.ok.setObjectName("ok")
        self.ok.setText("ok")
        self.gridLayout.addWidget(self.ok, 4, 1, 1, 1)
        
        self.cancel = QtGui.QPushButton(self)
        self.cancel.setObjectName("cancel")
        self.cancel.setText("cancel")
        self.gridLayout.addWidget(self.cancel, 4, 0, 1, 1)
        
        self.ok.clicked.connect(self.accept_dialog)
        self.cancel.clicked.connect(self.reject_dialog)

                
                
                





class add2Playlist(QtCore.QObject):
    
    def set_values(self, parent,mainframe, curdir, configxml, dbpath):
        self.mainframe = mainframe
        self.parent = parent
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        self.lib = common.common() 
        
        
    @QtCore.Slot(str)
    def go(self, track_src):
        print('add2Playlist.go', track_src)
        table = self.get_table(track_src)
        tracks = self.get_tracks(table)
        self.thediag = add2PlaylistDialog(self.parent,track_src,tracks,self.dbpath)


    def get_tracks(self,table):
        tracks = []    
        trs = table.findAll('tr').toList()
        for tr in trs:
            tracks.append(tr.attribute('track_src'))
        return tracks


    def get_table(self, track_src):  
        table = 'not'    
        trs = self.mainframe.findAllElements('tr').toList()
        for tr in trs:
            tr_track_src = tr.attribute('track_src')
            if tr_track_src == track_src:
                table = tr.parent() 
        return table
                

                
                
                
                
                
                
                
                
