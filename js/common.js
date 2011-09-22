


var LibCommon = new Object();
LibCommon.init = function(){
    var mode = document.body.getAttribute('data-mode');
    var navletterslocation = document.body.getAttribute('data-navletterslocation');

    if (mode == 'front') {
        var headID = document.getElementsByTagName("head")[0];         
        var newScript = document.createElement('script');
        newScript.type = 'text/javascript';
        newScript.src = navletterslocation;
        newScript.onload = LibCommon.go;
        headID.appendChild(newScript);
    }


    //var get_desc = document.getElementById('get_desc');
    //if (get_desc != null){
    //    dom_addEventListener(get_desc,"mouseup",LibCommon.first); 
    //}
}

LibCommon.go = function(){
    navletters.init('frontWrapper',0);
}


//Let the games begin
dom_onDomReady(LibCommon.init);
//end
