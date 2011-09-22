import sys
import os
from xml.etree import ElementTree as ET
import templates
import common
from PySide import QtCore





class MyConfig(QtCore.QObject):
    postQueryDbSig = QtCore.Signal(str)


    def set_values(self,curdir,configxml):
        self.curdir = curdir
        self.configxml = configxml
        self.lib = common.common() 
        self.templates = templates.templates()



    @QtCore.Slot()
    def go(self):
        html = self.templates.get_common_html(self.curdir)

        body = html.find('body')
        goback = ET.SubElement(body, 'div')
        goback.attrib['id'] = 'goback' 
        
        homelink = ET.SubElement(goback, 'a')
        homelink.attrib['href'] = 'file://' + os.path.join(self.curdir, 'index.html')
        homelink.text = 'Hall'
        
        wrapper = ET.SubElement(body, 'div')
        wrapper.attrib['id'] = 'configWrapper'
        
        self.get_settings(wrapper)
        
        self.postQueryDbSig.emit(ET.tostring(html))
        
        
        

    def get_locations(self, div):
        # Locations
        locations = self.configxml.find('locations')
        for loc in locations.getiterator('location'):
            i1 = ET.SubElement(div, 'input', {
                'class':'configInput', 
                'value':loc.text, 
                'size':'40'})
            # Break line
            br1 = ET.SubElement(div, 'br')



    def get_thumbs_size(self,div):
        # Thumbs small size
        thumbs_small = self.configxml.find('thumbs_small').text
        l2 = ET.SubElement(div, 'label', {'for':'i2'})
        l2.text = 'Small thumbs size'
        i2 = ET.SubElement(div, 'input', {
                'class':'configInput', 
                'value':thumbs_small, 
                'size':'5', 
                'id':'i2'})
        # Break line
        br2 = ET.SubElement(div, 'br')
        
        # Thumbs big size
        thumbs_big = self.configxml.find('thumbs_big').text
        l3 = ET.SubElement(div, 'label', {'for':'i3'})
        l3.text = 'Big thumbs size'
        i3 = ET.SubElement(div, 'input', {
                'class':'configInput', 
                'value':thumbs_big, 
                'size':'5', 
                'id':'i3'})
        # Break line
        br3 = ET.SubElement(div, 'br')
        



    def get_settings(self,wrapper):
        div = ET.SubElement(wrapper,'div')

        self.get_locations(div)   
        self.get_thumbs_size(div)

        

        #return ET.tostring(html)
        # html = self.writeConfigTabs(theXml.find('configTabs'))
#        html = self.getVideoSettings(theXml.find('video_folders'))
#        return html
        

#        
#    def getVideoSettings(self,xml):
#        wrapper = ET.Element('div')
#        
#        it = xml.getiterator('folder')
#        for folder in it:
#            profileLabel = folder.attrib['profile']
#            profilePath = folder.text
#            n = str(it.index(folder))
#            
#            profile = ET.SubElement(wrapper, "div")
#
#            label = ET.SubElement(profile, "label")
#            label.attrib['for'] = 'vid_'+n
#            label.text = profileLabel
#
#            input = ET.SubElement(profile, "input")
#            input.attrib['id'] = 'vid_'+n
#            input.attrib['type'] = 'text'
#            input.attrib['value'] = profilePath
#            
#            button = ET.SubElement(profile, "button")
#            button.text = 'remove'
#
#        return ET.tostring(wrapper) 
#        
#        
#        
#    def writeConfigTabs(self,xml):
#        wrapper = ET.Element('div')
#        wrapper.attrib['id'] = 'config_tabs_wrapper'
#        
#        it = xml.getiterator('tab')
#        for tab in it:
#            profileLabel = tab.attrib['label']
#            profile = tab.attrib['profile']



