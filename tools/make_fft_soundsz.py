import os
import tempfile
import subprocess
from scipy.io import wavfile
import numpy 
import logging
import logging.handlers
from matplotlib import pyplot
import hashlib
import datetime
import cPickle
import Image
import ImageChops



class Main:   

    def __init__(self,soundsz_folder, fft_folder, exts, overwrite_fft, overwrite_svg,overwrite_png): 
                
        # convert file to wav
        # read wav file
        # save dat file
        # delete wav file
        # plot all to svg using dat files 
        # convert all svg to png using fixed size
        # resize all png

        self.log = self.create_log()
        self.log.debug('---------------------------------------------------------')
        self.log.debug('Starting %s ' % self.date_fmt())
        
        self.tempdir = tempfile.gettempdir()
        self.overwrite_fft = overwrite_fft
        self.overwrite_svg = overwrite_svg
        self.overwrite_png = overwrite_png
        self.png_width = 798
        self.png_height = 150
        
        # save dat files
        self.go_save_dat_files(soundsz_folder, fft_folder, exts) 
        self.shout('All done saving dat files')
        self.log.debug('Ending saving dat files %s ' % self.date_fmt())
        
        ## plot dat files
        #self.log.debug('Starting ploting dat files %s ' % self.date_fmt())
        #self.go_plot_data(fft_folder)
        #self.shout('All done ploting dat files')
        #self.log.debug('Ending ploting dat files %s ' % self.date_fmt())

        ## convert svg to png
        #self.log.debug('Starting convert svg to png %s ' % self.date_fmt())
        #self.go_convert_svg2png(fft_folder)
        #self.shout('All done convert svg to png')
        #self.log.debug('Ending convert svg to png %s ' % self.date_fmt())

        ## resize pngs
        #self.log.debug('Starting resize pngs %s ' % self.date_fmt())
        #self.resize_pngs(fft_folder)
        #self.shout('All done resize pngs')
        #self.log.debug('Ending resize pngs %s ' % self.date_fmt())



    def go_save_dat_files(self, soundsz_folder, fft_folder, exts):
        # Todo : show total tracks / current track
        allsoundfiles = self.walkDir(soundsz_folder, exts)
        for file in allsoundfiles:
            ext = file[1]
            fullurl = file[0]
            filename = file[2]
            output_filename = os.path.join(self.tempdir, filename + '.wav')
            output_fft_file = self.get_output_fft_file(soundsz_folder, fft_folder, fullurl)
            
            if not os.path.exists(output_fft_file) or self.overwrite_fft:
                print('Saving dat files : ',allsoundfiles.index(file),len(allsoundfiles))
                
                self.convert_file(ext, fullurl, filename, output_filename)
                data = self.read_wav(output_filename)
                self.save_data(output_fft_file, data)
                self.delete_temp_wav_file(output_filename)



    def go_plot_data(self, fft_folder):
        alldatfiles = self.walkDir(fft_folder, '.dat')
        for datfile in alldatfiles:
            print('go_plot_data : ',alldatfiles.index(datfile),len(alldatfiles))
                
            url, ext = os.path.splitext(datfile[0])
            svg_path = url + '.svg'
            if not os.path.exists(svg_path) or self.overwrite_svg:
                data = self.get_dat_file(datfile[0])
                if data != 'not':
                    self.plot_data(svg_path,data)



    def resize_pngs(self,fft_folder):
        allpngfiles = self.walkDir(fft_folder, '.png')
        for pngfile in allpngfiles:
            print('resize_pngs : ',allpngfiles.index(pngfile),len(allpngfiles))
                
            png_path = pngfile[0]
            if not os.path.exists(png_path) or self.overwrite_png:
                try:
                    im=Image.open(png_path)
                    dims = self.getbbox(im,(255,255,255))
                    d = (dims[0],0,dims[2],im.size[1])
        
                    new = im.crop(d)
                    new2 = new.resize((self.png_width, self.png_height))
                    new2.save(png_path)
                    
                    print('Resize png : ',png_path)
                    self.log.debug('Resize png %s ' % png_path)
                except Exception as e:
                    print('Problems resize_pngs : ',e)
                    self.log.debug('Error resize_pngs %s ' % png_path)
    
    
    
    
    
    def getbbox(self,im, bgcolor):
        if im.mode != "RGB":
            im = im.convert("RGB")
            bg = Image.new("RGB", im.size, bgcolor)
            diff = ImageChops.difference(im, bg)
            bbox = diff.getbbox()
        if bbox:
            return bbox
        return None # no contents
    
    

    def go_convert_svg2png(self, fft_folder):
        allsvgfiles = self.walkDir(fft_folder, '.svg')
        for svgfile in allsvgfiles:
            url, ext = os.path.splitext(svgfile[0])
            png_path = url + '.png'
            
            print('go_convert_svg2png : ',allsvgfiles.index(svgfile),len(allsvgfiles))
               
            #if not os.path.exists(png_path) or self.overwrite_png:
            if not os.path.exists(png_path):
                cmd = ["inkscape",
                       "-f ",svgfile[0],
                       "--export-png",png_path,
                       "--export-width",str(self.png_width),
                       "--export-height",str(self.png_height)]
    
                try:
                    self.shout('-----------------------------------')
                    proc = subprocess.call(cmd)
                    self.shout('Running : ',cmd[0])
                except Exception as e:
                    print('Problems inkscape : ',e)
                    print('Problems inkscape : ',cmd)
                    self.log.debug('Error CMD %s ' % cmd[0])
                
                if not os.path.exists(png_path):
                    self.log.debug('Error CMD %s ' % cmd[0])
                    self.shout('Error CMD: ',cmd[0],svgfile[0])



    def plot_data(self,svg_path,data):
        try:
            fig = pyplot.figure()
            fig.set_dpi(100)
            
            pyplot.axis('off')
            pyplot.plot(data,linewidth=1.0,color='#333333')
            
            fig.savefig(svg_path, transparent = True, bbox_inches='tight', pad_inches=0)
            pyplot.clf()
            pyplot.close('all')
            self.shout('Plotting svg : ',svg_path)
            self.log.debug('Plotting svg')
        except Exception as e:
            self.shout('Problems plotting data : ',e)
            self.log.debug('Error plotting data %s ' % svg_path)
                
        

    def save_data(self,output_fft_file,data):
        if data != False:
            hz = data[0]
            samples = data[1]
            length = samples / hz
            sample_size = 1024

            p = []
            i = 0
            for item in samples:
                if i == sample_size:
                    i = 0
                    p.append(item)
                i += 1
    
            print('Samples  1024 : ',len(p))
            print('Samples  all : ',len(data[1]))
            self.save_dat_file(output_fft_file,p)





    def save_dat_file(self,url,data):
        try:
            self.create_dirs(os.path.dirname(url))

            cPickle.dump(data, open(url, 'wb'),-1)
            self.log.debug('Saving file %s ' % url)
            self.shout ("Saving file : ", url)

        except Exception as e:
            print ("Error saving file : ", e)
            self.log.debug('Error saving file %s ' % url)



    def get_dat_file(self,url):
        data = 'not'
        try:
            data = cPickle.load(open(url, 'rb'))
            self.log.debug('Loading dat file %s ' % url)
            self.shout ("Loading dat file : ", url)
        except Exception as e:
            print ("Error loading dat file : ", e)
            self.log.debug('Error loading dat file %s ' % url)
        return data



    def read_wav(self,output_filename):
        a = False
        try:
            # Return the sample rate (in samples/sec) and data from a WAV file
            a = wavfile.read(output_filename)
            self.shout('Reading file : ',output_filename)
            self.log.debug('Reading data %s ' % output_filename)
        except Exception as e:
            print ("Error read_wav : ", e)
            self.shout('Wav file is : ',output_filename)
            self.log.debug('Error reading data %s ' % output_filename)
        return a



    def get_output_fft_file(self,soundsz_folder,fft_folder,fullurl):
        s = 'not'
        try:
            s = os.path.join(fft_folder,fullurl[len(soundsz_folder):]+'.dat')
        except Exception as e:
            print ('Error is : ',e)
            self.shout ("Error get_output_fft_file")
            self.log.debug('Error get_output_fft_file %s ' % fullurl)
        return s



    def create_dirs(self,dir):
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
                self.log.debug('Creating dir %s ' % dir)
                self.shout ("Creating dir : ", dir)
            except Exception as e:
                print ("Error creating dir: ",e)

    
    
    def convert_file(self,ext,fullurl,filename,output_filename):
        ext = ext.lower()
        if ext == '.mp3':
            cmd = ["lame", "--decode", fullurl, output_filename]
        elif ext == ".ogg":
            cmd = ["oggdec", fullurl, "-o", output_filename]
        elif ext == ".flac":
            cmd = ["flac", "-f", "-d", "-o", output_filename, fullurl]

        try:
            self.shout('-----------------------------------')
            proc = subprocess.call(cmd)
            self.shout('Running : ',cmd[0])
        except Exception as e:
            self.shout('Problems running : ',cmd[0])
            self.log.debug('Error CMD %s ' % ', '.join(cmd))
        
        if not os.path.exists(output_filename):
            self.log.debug('Error CMD %s ' % ', '.join(cmd))
            self.shout('Error CMD: ',cmd[0],fullurl)
        else:
            self.log.debug('Running CMD %s ' % ', '.join(cmd))
            self.shout('Running CMD: ',cmd[0],fullurl)
            
            
            
    def walkDir(self,dir,exts):
        items = []
        try:
            for root,dirs,files in os.walk(unicode(dir)):
                for file in files:
                    full_url = os.path.join(dir,root,file)
                    url, ext = os.path.splitext(full_url)
                    if ext.lower() in exts:
                        items.append([full_url,ext,file])
        except Exception as e:
            self.shout ("Error walkDir : ", e)
        return items
            


    def delete_temp_wav_file(self,full_url):
        try:
            if os.path.exists(full_url):
                os.remove(full_url)
                self.shout('Delete file : ',full_url)
                self.log.debug('Deleting file %s ' % full_url)
        except Exception as e:
            self.shout ("Error deleteFile : ", e)
            self.log.debug('Problems deleting file %s ' % full_url)



    def create_log(self):
        curdir = os.path.dirname(__file__)
        LOG_FILENAME = os.path.join(curdir,'logs','create_fft_log.log')

        my_logger = logging.getLogger('MyLogger')
        my_logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=2000000, backupCount=10)
        
        my_logger.addHandler(handler)
        return my_logger
            


    def date_fmt(self):
        return datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
            


    def shout(self,*args):
        #pass
        print(', '.join(args))
        
        

if __name__ == "__main__":
    soundsz_folder = "/media/vault_small/som/"
    fft_folder = '/media/vault_small/som/FFT'
    exts = ['.mp3','.ogg','.flac']
    overwrite_fft = False
    overwrite_svg = False
    overwrite_png = False
    Main(soundsz_folder,fft_folder,exts,overwrite_fft,overwrite_svg,overwrite_png)
            
            
            
            
            
            
            
