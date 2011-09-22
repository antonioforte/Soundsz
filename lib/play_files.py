from __future__ import division
from PySide import QtCore
from PySide.phonon import Phonon
from xml.etree import ElementTree as ET
import common
import time
import os


class setupFiles(QtCore.QObject):

    def set_values(self, w,configxml, curdir):
        self.w = w
        self.curdir = curdir
        self.page_title = self.w.title()
        self.configxml = configxml
        self.fft_folder = self.configxml.find('fft_folder').text
        # this is going to break when having multiple locations
        self.soundsz_folder = self.configxml.find('locations').getiterator('location')[0].text
        self.doc = self.w.documentElement()
        self.lib = common.common()
        self.cur_folder = ''
        self.audio_tag = ''
        self.playlist = ''
        self.curtrack = 0
    
    
    @QtCore.Slot(str, str)
    def go(self, what2do, folder):
        '''This function is called from javascript when clicking
        the tracks, info or play all buttons'''

        print('what 2 to',str(what2do))
        
        what2do = str(what2do)
        # stop playback when exiting the page
        self.eval_js(self.doc,
            '''window.addEventListener("unload", setup_files.stop, false);''')

        if what2do == 'play_all':
            tracks, folder_wrapper = self.get_folder_tracks(folder)
            self.curtrack = 0
            self.playlist = tracks
            self.cur_folder = folder_wrapper
            self.create_player()
            self.create_buttons_events()
            
            self.media_object = Phonon.MediaObject(self)
            self.audio = Phonon.AudioOutput(Phonon.MusicCategory)
            self.media_object.setTickInterval(1000)

            self.media_object.tick.connect(self.draw_time)
            self.media_object.stateChanged.connect(self.stateChanged)
            self.media_object.finished.connect(self.next)

            Phonon.createPath(self.media_object, self.audio)
        if what2do == 'show_info':
            self.show_hide_info(folder,'div.info')
        if what2do == 'show_tracks':
            self.show_hide_info(folder,'div.files_table_wrapper')



    @QtCore.Slot()
    def play(self):       
        track_src = self.playlist[self.curtrack].keys()[0]
        is_playing = self.media_object.state()
        play_btn = self.cur_folder.findFirst('button.play')
        title_btn = self.cur_folder.findFirst('div.player button.title')
        
        if is_playing == Phonon.PausedState:
            self.media_object.play()
            play_btn.setPlainText('pause')

        if is_playing == Phonon.PlayingState:
            self.media_object.pause()
            play_btn.setPlainText('play')

        if is_playing == Phonon.LoadingState:
            self.media_object.setCurrentSource(Phonon.MediaSource(track_src))
            self.media_object.play()
            play_btn.setPlainText('pause')
            self.change_volume(0.5, 15, 'start')

        self.update_curtrack_btn()   
        title_btn.setPlainText(self.playlist[self.curtrack][track_src][0]) 
              
           
    def create_buttons_events(self):
        play_btn = self.cur_folder.findFirst('div.player button.play')
        next_btn = self.cur_folder.findFirst('div.player button.next')
        pre_btn = self.cur_folder.findFirst('div.player button.previous') 
        self.eval_js(play_btn,'''this.addEventListener('mouseup',setup_files.play,false);''')
        self.eval_js(next_btn,'''this.addEventListener('mouseup',setup_files.next,false);''')
        self.eval_js(pre_btn,'''this.addEventListener('mouseup',setup_files.previous,false);''')
        # change track volume
        self.eval_js(self.cur_folder.findFirst('div.volume canvas'), '''
            this.addEventListener("click", 
                function(e) { 
                    var x = e.clientX - this.offsetLeft;
                    var y = e.clientY - this.offsetTop;
                    setup_files.change_volume(x,y,'manual');
                }, false);''')
        # change track current time
        self.eval_js(self.cur_folder.findFirst('div.timebar canvas'), '''
            this.addEventListener("click", 
                function(e) { 
                    var x = e.clientX - this.offsetLeft;
                    var y = e.clientY - this.offsetTop;
                    setup_files.change_cur_time(x,y);
                }, false);''')


    def create_player(self):
        defaultpngfftpath = os.path.join(self.curdir,'res','spectrum_default.png')

        self.doc.findFirst('div.player').removeFromDocument()
        player = '''<div class="player">
           <button class="title">title</button>
           <button class="time">time</button>
           <button class="curtrack">curtrack</button>
           <div id="fftplaceholder">
               <img src="file://'''+defaultpngfftpath+'''" id="fftpng" width="798px" height="150px" />
           </div>
           <div class="timebar"><canvas width="798px" height="15px" /></div>
           <div class="volume"><canvas width="798px" height="15px" /></div>
           <button class="previous">previous</button>
           <button class="next">next</button>
           <button class="play">play</button>
        </div>
        '''
        self.cur_folder.findFirst('div').appendOutside(player)  

        
        
    @QtCore.Slot()
    def previous(self):
        print ('setupFiles.previous')
        self.curtrack -= 1
        if self.curtrack < 0:
            self.curtrack = len(self.playlist) - 1
        self.insert_track()


    @QtCore.Slot()
    def stop(self):  
        print('Stopping')
        try:
            self.media_object.stop()
        except Exception as e:
            print ("Problems stopping playback: ", e)
  

    @QtCore.Slot()
    def next(self): 
        print ('setupFiles.next')
        self.curtrack += 1
        if self.curtrack >= len(self.playlist):
            self.curtrack = 0
        self.insert_track()

           
    def stateChanged(self,newState, oldState):
        print('stateChanged : ',self.media_object.state())
        s = self.media_object.state()
        if s == Phonon.ErrorState:
            print('There is an error: ',self.media_object.errorType())
            
        
    def update_curtrack_btn(self):
        curtrack_btn = self.cur_folder.findFirst('div.player button.curtrack')
        text = str(self.curtrack+1)+' / '+str(len(self.playlist))
        curtrack_btn.setPlainText(text)
        self.update_curtrack_row()
        self.create_fft()

            
            
            
    def update_curtrack_row(self):
        table_rows = self.cur_folder.findAll('tr').toList()
        track_src = self.playlist[self.curtrack].keys()[0]
        cur_title = self.playlist[self.curtrack][track_src][1]
        for tr in table_rows:
            tr_track = tr.attribute('track_src')
            if track_src == tr_track:
                tr.setStyleProperty('background','#222222')
            else:
                tr.setStyleProperty('background','transparent')
                



    def insert_track(self):
        track_src = self.playlist[self.curtrack].keys()[0]
        title_btn = self.cur_folder.findFirst('div.player button.title')
        title_btn.setPlainText(self.playlist[self.curtrack][track_src][0])
        self.update_curtrack_btn()
        self.media_object.setCurrentSource(Phonon.MediaSource(track_src))
        self.media_object.play()
        self.create_fft()
        print('insert track : ',str(track_src), self.curtrack)               
        
        
        


    def create_fft(self):
        track_src = self.playlist[self.curtrack].keys()[0]
        pngfftpath = os.path.join(self.fft_folder,
                                  track_src[len(self.soundsz_folder):]+'.png')
        defaultpngfftpath = os.path.join(self.curdir,'res','spectrum_default.png')

        if os.path.exists(pngfftpath):
            print('Loading png fft : ',pngfftpath)
            fftimage = self.cur_folder.findFirst('img#fftpng')
            fftimage.setAttribute('src','file://' + pngfftpath)
        else:
            print('Loading png fft default: ',pngfftpath)
            fftimage = self.cur_folder.findFirst('img#fftpng')
            fftimage.setAttribute('src','file://' + defaultpngfftpath) 





    def draw_time(self,cur_time):  
        time_el = self.cur_folder.findFirst('button.time')
        canvas = self.cur_folder.findFirst('div.timebar canvas')
        strat = canvas.StyleResolveStrategy(2)
        canvas_w = canvas.styleProperty('width', strat).replace('px', '')
        canvas_h = canvas.styleProperty('height', strat).replace('px', '')
        
        cur_time = cur_time
        cur_total = self.media_object.totalTime()

        progress = (int(canvas_w) / cur_total) * cur_time
        self.draw_in_canvas(canvas,progress,canvas_h)  
               
        curtime = time.strftime("%M:%S", time.gmtime(cur_time/1000))
        curtotal = time.strftime("%M:%S", time.gmtime(cur_total/1000))
        time_el.setPlainText(str(curtime) + ' / ' + str(curtotal))
        

    @QtCore.Slot(int, int, str)
    def change_volume(self, x, y, mode):
        canvas = self.cur_folder.findFirst('div.volume canvas')
        strat = canvas.StyleResolveStrategy(2)
        canvas_w = canvas.styleProperty('width', strat).replace('px', '')
        canvas_h = canvas.styleProperty('height', strat).replace('px', '')
        cur_total = 5.0
        
        if mode == 'start':
            newvolume = x
            x = (int(canvas_w) / cur_total) * x
        else:
            newvolume = x / (int(canvas_w) / cur_total)
            
        self.draw_in_canvas(canvas,x,canvas_h)
        self.audio.setVolume(newvolume)
        print('change_volume : ',newvolume)  


    @QtCore.Slot(int, int)
    def change_cur_time(self, x, y):
        canvas = self.cur_folder.findFirst('div.timebar canvas')
        strat = canvas.StyleResolveStrategy(2)
        canvas_w = canvas.styleProperty('width', strat).replace('px', '')
        canvas_h = canvas.styleProperty('height', strat).replace('px', '')
        
        cur_total = self.media_object.totalTime()
        newtime = x / (int(canvas_w) / cur_total)
        
        self.draw_in_canvas(canvas,x,canvas_h)
        self.media_object.seek(newtime)


    def draw_in_canvas(self,canvas,x,canvas_h):
        self.eval_js(canvas, '''
        ctx = this.getContext('2d');
        ctx.clearRect(0, 0, this.width, this.height);
        ctx.strokeStyle = "#1269ac";
        ctx.lineWidth = 1;
        ctx.beginPath();        
        ctx.moveTo(''' + str(x) + ''',0);
        ctx.lineTo(''' + str(x) + ''',''' + canvas_h + ''');
        ctx.stroke();
        ''')
        
        
    def eval_js(self, el, js):
        return el.evaluateJavaScript(js)


    def show_hide_info(self,folder,selector):
        labels = self.doc.findAll("div.wrpTopLevelDirLabel span").toList()
        for label in labels:
            label_text = label.attribute('data-label')
            if label_text == folder:
                folder_wrapper = label.parent().parent()
                div_info = folder_wrapper.findFirst(selector)
                strat = div_info.StyleResolveStrategy(2)
                
                div_info_display = div_info.styleProperty('display', strat)
                if div_info_display == 'none':
                    div_info.setStyleProperty('display','block')
                else:
                    div_info.setStyleProperty('display','none')
                    

    def get_folder_tracks(self, folder):
        tracks = []
        folder_wrapper = 'not'
        
        labels = self.doc.findAll("div.wrpTopLevelDirLabel span").toList()
        for label in labels:
            label_text = label.attribute('data-label')
            if label_text == folder:
                folder_wrapper = label.parent().parent()
                table = folder_wrapper.findFirst('table')
                for tr in table.findAll('tr').toList():
                    track_src = tr.attribute('track_src')  
                    track = {track_src:[]}
                    for td in tr.findAll('td').toList():
                        track[track_src].append(td.toPlainText())
                    tracks.append(track)
                            
        return tracks, folder_wrapper                 
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
