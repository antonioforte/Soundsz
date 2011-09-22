import os
import json
import pprint
import time
from xml.etree import ElementTree as ET
import templates
import common
import sqlite3
from PySide import QtCore



class queryDbGetDetail:
    
    def set_values(self,curdir,configxml,dbpath):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        self.lib = common.common() 
        self.templates = templates.templates()
        self.fields_to_show = configxml.find('fields_to_show').text.split(',')
 
        
    def go(self,what,detail):
        conn = sqlite3.connect(self.dbpath)
        c = conn.cursor()
        c.execute('SELECT * FROM soundsz WHERE '+what+'=? ORDER BY Fullurl',[detail])
        c.row_factory = sqlite3.Row
        
        html = self.templates.get_common_html(self.curdir)
        body = html.find('body')
        body.attrib['data-mode'] = 'afterfront'
        body.attrib['data-what'] = what
        body.attrib['data-detail'] = detail
        
        goback = ET.SubElement(body, 'div')
        goback.attrib['id'] = 'goback' 
        homelink = ET.SubElement(goback, 'a')
        homelink.attrib['href'] = 'file://' + os.path.join(self.curdir, 'index.html')
        homelink.text = 'Hall'
        backlink = ET.SubElement(goback, 'span')
        backlink.attrib['onclick'] = "query_db.get_all('"+what+"')"
        backlink.text = 'back'

        wrapper = ET.SubElement(body, 'div')
        wrapper.attrib['id'] = 'afterFrontWrapper'

        if what == 'TopLevel':
            # This gets tracks from top level folders
            self.get_top_level_html(detail,c,wrapper)
        else:
            # This is to get albums, genres, artists, playlists
            self.get_album_html(detail,c,wrapper)
            
        return ET.tostring(html)

            
            
    def get_album_html(self,detail,c,wrapper):
        '''This is to get a list of files of the detail.
        The detail may be genre, album, artist or playlist
        '''
        folder_files = {}
        folder = detail
        folder_files[folder] = []
        for row in c:
            folder_files[folder].append(row)

        for folder in folder_files.keys():
            haspic = folder_files[folder][0]['HasPic']
            full_url = folder_files[folder][0]['Fullurl']
            has_desc = folder_files[folder][0]['HasDesc']     

            div = ET.SubElement(wrapper,'div',{'class':'wrpTopLevelDir'})
            div_label = ET.SubElement(div,'div',{'class':'wrpTopLevelDirLabel'})
            span_text = folder
            span = ET.SubElement(div_label,'span',{'data-label':span_text})
            span.text = span_text
            
            self.append_label_buttons(div_label)
            self.append_folder_info(haspic,has_desc,full_url,folder_files[folder],div)
            self.append_folder_table(folder_files[folder],folder,div)




    def get_top_level_html(self,detail,c,wrapper):
        '''Get list of files in the top level folder'''
        folder_files = {}
        for row in c:
            folder = os.path.dirname(row['Fullurl'])
            if folder not in folder_files.keys():
                folder_files[folder] = []
            folder_files[folder].append(row)

        for folder in folder_files.keys():
            haspic = folder_files[folder][0]['HasPic']
            full_url = folder_files[folder][0]['Fullurl']
            has_desc = folder_files[folder][0]['HasDesc']            

            div = ET.SubElement(wrapper,'div',{'class':'wrpTopLevelDir'})
            div_label = ET.SubElement(div,'div',{'class':'wrpTopLevelDirLabel'})

            span = ET.SubElement(div_label,'span',{'data-label':folder[folder.index(detail):]})
            span.text = folder[folder.index(detail):]
            
#            span = ET.SubElement(div_label,'span',{'data-label':span_text})
#            span.text = folder
            
            self.append_label_buttons(div_label)
            self.append_folder_info(haspic,has_desc,full_url,folder_files[folder],div)
            self.append_folder_table(folder_files[folder],folder,div)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    def append_label_buttons(self, div_label):
        btn_play_all = ET.SubElement(div_label, 'button', 
             {'data-what2do':'play_all', 'data-desc':'label_buttons'})
        btn_play_all.text = 'play'
        btn_show_info = ET.SubElement(div_label, 'button', 
            {'data-what2do':'show_info', 'data-desc':'label_buttons'})
        btn_show_info.text = 'info'
        btn_show_tracks = ET.SubElement(div_label, 'button', 
            {'data-what2do':'show_tracks', 'data-desc':'label_buttons'})
        btn_show_tracks.text = 'tracks'


 
    def append_folder_table(self, files, folder, div):
        conn = sqlite3.connect(":memory:")
        c = conn.cursor()
        c.row_factory = sqlite3.Row

        c.execute('''CREATE TABLE folder_files 
        (Album text,
        Artist text,
        Track int,
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
        
        for row in files:
            t = []
            for item in row:
                t.append(item)
            c.execute('insert into folder_files values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', t)

        conn.commit()
        c.execute('select * from folder_files order by Track')
        d = c.fetchall()

        # create table
        table_div = ET.SubElement(div,'div',{'class':'files_table_wrapper'})
        table = ET.SubElement(table_div,'table')
        
        # add table headers
        # Todo : Must fix play files to enable table headers
#        tr = ET.SubElement(table, 'tr')
#        for field in self.fields_to_show:
#            td = ET.SubElement(tr, 'td')
#            td.text = field  
        
        # add rows
        for track in d:
            tr = ET.SubElement(table, 'tr')
            tr.attrib['track_src'] = track['Fullurl']
            for field in self.fields_to_show:
                td = ET.SubElement(tr, 'td')
                if field == 'Track':
                    td.text = str(track[field])                    
                elif field == 'Length':
                    td.text = time.strftime('%M:%S', time.gmtime(float(track[field].split('.')[0])))                    
                elif field == 'Filesize':
                    td.text = str(int(track[field]) / 1024 / 1024)+' mb'                    
                elif field == 'MyPlaylist':
                    td.attrib['class'] = 'add2Playlist'
                    td.text = track[field]
                else:
                    td.text = track[field]







    def append_folder_info(self, haspic, has_desc, full_url, files, div):
        folder_time = 0
        folder_size = 0
        folder_albums = []
        folder_artists = []
        folder_genres = []
        folder_dates = []
        
        for track in files:
            folder_time += float(track['Length'].split('.')[0])
            folder_size += int(track['Filesize'])
            if track['Album'] not in folder_albums: folder_albums.append(track['Album'])
            if track['Artist'] not in folder_artists: folder_artists.append(track['Artist'])
            if track['Genre'] not in folder_genres: folder_genres.append(track['Genre'])
            if track['Date'] not in folder_dates: folder_dates.append(track['Date'])
            
        div_info = ET.SubElement(div,'div',{'class':'info'})

        div_info_img = ET.SubElement(div_info,'div',{'class':'div_info_img'})
        img_src = os.path.join(self.curdir, 'res', 'default_big.png')
        if haspic == str(1):
            img_src = os.path.join(os.path.dirname(full_url), 'folder_big.jpg')
        img = ET.SubElement(div_info_img, 'img', {'src':'file://' + img_src})
            
        div_total_time = ET.SubElement(div_info,'div')
        div_total_time.text = time.strftime('%H:%M:%S',time.gmtime(folder_time))
        
        div_total_size = ET.SubElement(div_info,'div')
        div_total_size.text = str(folder_size / 1024 / 1024) +' mb'
        
        div_artists = ET.SubElement(div_info,'div')
        div_artists.text = ', '.join(folder_artists)

        div_albums = ET.SubElement(div_info,'div')
        div_albums.text = ', '.join(folder_albums)
        
        div_total_tracks = ET.SubElement(div_info,'div')
        div_total_tracks.text = str(len(files))+' tracks'
        
        div_genres = ET.SubElement(div_info,'div')
        div_genres.text = ', '.join(folder_genres)

        div_date = ET.SubElement(div_info,'div')
        div_date.text = ', '.join(folder_dates)
                
        div_hasdesc = ET.SubElement(div_info,'div')
        if has_desc == '1': 
            span = ET.SubElement(div_hasdesc,'span')
            desc_file_url = os.path.join(os.path.dirname(full_url), 'desc.txt')
            
            # Maybe show some characters from the description
            #span.text = self.lib.get_snippet_file(desc_file_url)
            span.text = 'has description'
            span.attrib['id'] = 'get_desc'
            span.attrib['data_fullurl'] = desc_file_url
        else:
            div_hasdesc.text = 'No description'   










