import os




class Main:   

    def __init__(self): 

        soundsz_folder = "/media/vault_small/som/"
        fft_folder = '/media/vault_small/som/FFT/'
        pngs = self.walkDir(fft_folder,['.png'])
        soundfiles = self.walkDir(soundsz_folder,['.mp3','.ogg','.flac'])

        print('Finding soundfiles without png')
        self.print_orphan_soundfiles(soundfiles,soundsz_folder,fft_folder)
        #print('Finding pngs without soundfile')
        #self.print_orphan_png(pngs,soundsz_folder,fft_folder)


    def print_orphan_soundfiles(self,soundfiles,soundsz_folder,fft_folder):
        o = 1
        for item in soundfiles:
            fullurl = item[0]

            pngfilepath = os.path.join(fft_folder,
                             fullurl[len(soundsz_folder):]+'.png')
            
            if not os.path.exists(pngfilepath):
                print(pngfilepath)
                o += 1
        print('Found orphan_soundfiles : ',str(o))


    def print_orphan_png(self,pngs,soundsz_folder,fft_folder):
        o = 1
        for item in pngs:
            fullurl = item[0]
            soundfilepath = os.path.join(soundsz_folder,
                             fullurl[len(fft_folder):].replace(item[1],''))
            
            if not os.path.exists(soundfilepath):
                print(soundfilepath)
                o += 1
        print('Found orphan_png : ',str(0))


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







if __name__ == "__main__":
    Main()
    
    
    
    
    
