

class GetTagStrings:

    def return_data(self,ext):
        self.data = {
                '.mp3': 
                        ['TALB',
                        'TPE1',
                        'TRCK',
                        'TIT2',
                        'TDRC',
                        'TCON'], 
                '.flac': 
                        ['album',
                        'artist',
                        'tracknumber',
                        'title',
                        'date',
                        'genre'], 
                '.ogg': 
                        ['album',
                        'artist',
                        'tracknumber',
                        'title',
                        'date',
                        'genre'],
                '.wma': 
                        ['WM/AlbumTitle',
                        'WM/AlbumArtist',
                        'WM/TrackNumber',
                        'Title',
                        'WM/Year',
                        'WM/Genre'], 
                '.m4a': 
                        ['\xa9alb',
                        '\xa9ART',
                        'trkn',
                        '\xa9nam',
                        '\xa9day',
                        '\xa9gen'], 
                '.mpc': 
                        ['Album',
                        'Artist',
                        'Track',
                        'Title',
                        'Year',
                        'Genre']
                    }

        return self.data[ext]
      
