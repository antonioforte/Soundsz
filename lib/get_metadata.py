import os
import templates
import common
import tag_strings

import mutagen2.flac
import mutagen2.mp3
import mutagen2.oggvorbis
import mutagen2.asf
import mutagen2.mp4
import mutagen2.musepack


class getMetadata:
    ''' Get metadata from audio files.
    The following fields are the ones being queried :
        length
        sample rate
        bitrate
        album
        artist
        tracknumber
        title
        date
        genre
    '''

    def go(self,ext,full_url):
         # get info and tag strings
         # if file cannot be scanned 
         # all tags will be 'not'
         tags = ['not','not','not','not','not','not','not','not','not']
         try:
             info_obj = self.get_info_obj(ext, full_url)
    
             length = str(info_obj.info.length)
             sample_rate = info_obj.info.sample_rate
             bitrate = self.get_bitrate(ext,full_url,info_obj)
             
             # get fields for each file type
             attribs = tag_strings.GetTagStrings().return_data(ext.lower())
             tags = self.parse_tags(info_obj,attribs)
             tags[2] = self.make_trackn_int(tags[2])

             tags.append(length)
             tags.append(sample_rate)
             tags.append(bitrate)
         except Exception as e:
             print ("Error could not get info: ", e)
         return tags
    
    
    
    def get_info_obj(self,ext,full_url):
        info_obj = 'not'
        ext = ext.lower()
        
        if ext == '.mp3':
            info_obj = mutagen2.mp3.MP3(full_url)
        elif ext == '.flac':
            info_obj = mutagen2.flac.FLAC(full_url) 
        elif ext == '.ogg':
            info_obj = mutagen2.oggvorbis.OggVorbis(full_url)
        elif ext == '.mpc':
            info_obj = mutagen2.musepack.Musepack(full_url)
        elif ext == '.m4a':
            info_obj = mutagen2.mp4.MP4(full_url)
        elif ext == '.wma':
            info_obj = mutagen2.asf.ASF(full_url)
        else:
            print('Not supported by mutagen',ext,full_url)

        return info_obj
    
    
    def get_bitrate(self,ext,full_url,info_obj):
        # Flac is lossless, bitrate does not affect quality
        if ext == '.flac':
            b = 'not'
        else:
            b = info_obj.info.bitrate
        return b
    
    
    def parse_tags(self,info_obj,attribs):
        # get metadata fields from info object
        # if it fails tag will be not
        # Todo : If tag is empty append not
        tags = []
        for attrib in attribs:
            try:
                tags.append(unicode(info_obj[attrib][0]))
            except Exception as e:
                tags.append('not')
        return tags


    def make_trackn_int(self,h):
        # this is here to remove
        # total tracks from tracknumber
        d = h
        hasslash = h.find('/')
        parens = h.find('(') #this is to find .m4a files tracknumber
        if hasslash != -1:
            d = h.split('/')[0]
        if parens != -1:
            d = h.replace('(','').replace(')','').split(',')[0]
        if d.find('not') == -1:
            d = int(d)
        else:
            d = 0
        return int(d)
    
    
    
