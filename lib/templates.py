import os
from xml.etree import ElementTree as ET

class templates:
    
    def Page(self,curdir,title):
        string = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<link href="file://'''+curdir+'''/style.css" rel="stylesheet" type="text/css" />
<script type="text/javascript" src="file://''' + curdir + '''/js/dom_helper.js"></script>
<script type="text/javascript" src="file://''' + curdir + '''/js/common.js"></script>
<title>'''+title+'''</title>
</head>
<body>

<div id="goback">
    <a href="file://'''+curdir+'''/index.html">Home</a>
</div>

_contents_

</body>
</html>'''

        return string
    

    def get_common_html(self,curdir):
        html = ET.Element('html')
        head = ET.SubElement(html, 'head')
        
        meta = ET.SubElement(head, 'meta')
        meta.attrib['http-equiv'] = 'content-type'
        meta.attrib['content'] = 'text/html; charset=utf-8'
        
        style = ET.SubElement(head, 'link')
        style.attrib['rel'] = 'stylesheet'
        style.attrib['type'] = 'text/css'
        style.attrib['href'] = 'file://' + os.path.join(curdir, 'style.css')
        
        script2 = ET.SubElement(head, 'script')
        script2.attrib['type'] = 'text/javascript'
        script2.attrib['src'] = 'file://' + os.path.join(curdir, 'js', 'dom_helper.js')
        script2.text = '/*nonsense*/'

        script1 = ET.SubElement(head, 'script')
        script1.attrib['type'] = 'text/javascript'
        script1.attrib['src'] = 'file://' + os.path.join(curdir, 'js', 'common.js')
        script1.text = '/*nonsense*/'

        title = ET.SubElement(head, 'title')
        title.text = 'hello'
        
        body = ET.SubElement(html, 'body')
        return html  
    
    
    
    
    
    
