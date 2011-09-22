import os
import time
import sqlite3
from PySide import QtCore

import templates
import common
import get_metadata



class buildDbWorker(QtCore.QThread):
    postStringsWorkerSig = QtCore.Signal(int,int)
    
    def __init__(self, parent = None):
        ''''Performance issues : 
                - showing progress bar increases scanning time
                - folders are scanned twice
                - dicts have different methods, 
                  some are faster but block the gui.
                - signaling progress also slowsdown things
        '''
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.lib = common.common() 
        self.templates = templates.templates()
        self.get_data = get_metadata.getMetadata()


    def __del__(self):
        self.exiting = True


    def set_values(self,curdir,configxml,dbpath):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        self.locations = self.configxml.find('locations')
        # Enable this to catch new pics and descs
        self.rebuild_db = self.configxml.find('rebuild_db').text
        self.exts = self.configxml.find('exts').text.split(',')
        self.thumbs_big = self.configxml.find('thumbs_big').text.split(',')
        self.thumbs_small = self.configxml.find('thumbs_small').text.split(',')
        self.overwrite_art = self.configxml.find('overwrite_art').text
        self.tempplaylists = {}
        
        
    def run(self):
        '''This function is auto magically called by thread'''
        locs = []
        for location in self.locations.getiterator('location'):
            locs.append(location.text)
        self.all_files = self.lib.walkDirs(locs)
        self.processed_files = 0

        self.create_db()
        
        
 
    def create_db(self):
        conn = sqlite3.connect(self.dbpath)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS soundsz
        (Album text,
        Artist text,
        Track text,
        Title text,
        Date text,
        Genre text,
        Length text,
        Sample_Rate text,
        Bitrate text,
        Filesize int,
        Fullurl text,
        TopLevel text,
        HasDesc text,
        HasPic text,
        LastAcess int,
        LastModification int,
        MyRating text,
        MyPlaylist text)''')
        
        # Only happens if option is set
        self.erase_all_records(c)
        
        # todo create soundsz table if not exists
        
        # get full_url list to check if file is in db 
        c.execute('select * from soundsz')
        dbfiles = []
        for row in c:
            dbfiles.append(row[10])
            
        self.remove_db_deadlinks(conn, c, dbfiles) 
        self.scan_dirs(conn, c, dbfiles)    
               
        conn.commit()
        c.close()
        self.tempplaylists = None
                


    def erase_all_records(self,c):
        '''When rebuilding db, create a dict of fullurl - playlist,
        to load when re-adding files'''
        
        if self.rebuild_db == 'yes':
            self.lib.shout('Rebuilding db')
            c.execute('select * from soundsz')
            for row in c:
                self.tempplaylists[row[10]] = row[17]
                
            self.lib.shout('Erasing all records')
            c.execute('''DELETE FROM soundsz''')

        
            
            
                         
                            
    def remove_db_deadlinks(self, conn, c, dbfiles):
        '''Remove dead files'''
        for dbfile in dbfiles:
            if dbfile not in self.all_files:
                self.lib.shout('Removing record',dbfile)
                c.execute('delete from soundsz where Fullurl=?', [dbfile])
                conn.commit()
                
                

    def scan_dirs(self, conn, c, dbfiles):
        for location in self.locations.getiterator('location'):
            if os.path.exists(location.text):
                
                for top_level in os.listdir(unicode(location.text)):
                    second_level = os.path.join(location.text, top_level)
                    for root, dirs, files in os.walk(unicode(second_level)):
                        for fn in files:
                            full_url = os.path.join(root, fn)
                            filename, ext = os.path.splitext(fn)

                            self.create_folder_art(root, full_url, filename, ext)
                            self.processed_files += 1
                            self.insert_in_db(conn, c, dbfiles, top_level, full_url, ext)
                            self.postStringsWorkerSig.emit(len(self.all_files),self.processed_files)
            else:
                print('Error path does not exist',location.text)
  
  
  
    def create_folder_art(self, root, full_url, filename, ext):
        if filename+ext == 'folder.jpg':
            small_path = os.path.join(root, 'folder_small' + ext)
            big_path = os.path.join(root, 'folder_big' + ext)
            g = self.overwrite_art
            
            if not os.path.exists(small_path) or g == 'yes':
                self.lib.shout('creating image',small_path)
                self.lib.createImgThumbFit(full_url, small_path, self.thumbs_small)
            if not os.path.exists(big_path) or g == 'yes':
                self.lib.shout('creating image',big_path)
                self.lib.createImgThumb(full_url, big_path, self.thumbs_big)



    def insert_in_db(self, conn, c, dbfiles, top_level, full_url, ext):
        go = self.yes_to_append(dbfiles, c, conn, ext, full_url)
        if go == 'yes':
            t = self.get_file_details(top_level, full_url, ext)
            c.execute('insert into soundsz values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', t)
            
            

    def yes_to_append(self,dbfiles, c,conn,ext, full_url):
        '''Check if file is to be added to DB.'''
        # Todo : Find a way to find files which have metadata changes
        # I tend to make changes in large quantities, so i just reload
        # the whole library
        go = 'no'
        if ext.lower().replace('.','') in self.exts:
            if full_url not in dbfiles:
                go = 'yes'
                self.lib.shout('New file',full_url)
        return go



    def get_file_details(self, top_level, full_url, ext):
        tags = self.get_data.go(ext, full_url)
        t = []
        for i in tags:
            t.append(i)
        
        statinfo = os.stat(full_url)
        filedir = os.path.dirname(full_url)
        haspic = os.path.exists(os.path.join(filedir,'folder.jpg'))
        hasdesc = os.path.exists(os.path.join(filedir, 'desc.txt'))
        lastacess = statinfo.st_atime
        lastmod = statinfo.st_mtime
        filesize = statinfo.st_size

        if full_url in self.tempplaylists:
            playlist = self.tempplaylists[full_url]
        else:
            playlist = 'not'
        
        t.append(int(round(filesize)))
        t.append(full_url)
        t.append(top_level)
        t.append(hasdesc)
        t.append(haspic)
        t.append(int(round(lastacess)))
        t.append(int(round(lastmod)))
        t.append('not')
        t.append(playlist)
        return t
 
 


class buildDb(QtCore.QObject):
    postBuildDbSig = QtCore.Signal(int,int)
    startBuildDbSig = QtCore.Signal(str)
    endBuildDbSig = QtCore.Signal(str)


    def set_values(self,curdir,configxml,dbpath):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        

    @QtCore.Slot()
    def go(self):
        self.worker = buildDbWorker()
        self.worker.set_values(self.curdir,self.configxml,self.dbpath)
        self.worker.finished.connect(self.say_end)
        self.worker.started.connect(self.say_start)
        self.worker.postStringsWorkerSig.connect(self.post_html)
        self.worker.start()


    def say_end(self):
        self.endBuildDbSig.emit('End scanning')
        total_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.begin_time))
        print(total_time)


    def say_start(self):
        self.begin_time = time.time()
        self.startBuildDbSig.emit('Started scanning')
        
        
    def post_html(self,total,current):
        self.postBuildDbSig.emit(total,current)
        
        

        
        
        
        
        
        
