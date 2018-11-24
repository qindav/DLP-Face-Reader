//Global blob for pcds
var text;

//Local form uploads
document.getElementById('fileinput').addEventListener('change', function(){
    var file = this.files[0];
    // This code is only for demo ...
    console.log("name : " + file.name);
    console.log("size : " + file.size);
    console.log("type : " + file.type);
    console.log("date : " + file.lastModified);

    var reader = new FileReader();
    reader.onload = function(e) {
        text = reader.result;
        //console.log(text);
    }
    reader.readAsText(file);
    drawStuff(file);

}, false);

//Server data upload
function LinkCheck(url)
{
    var http = new XMLHttpRequest();
    http.open('GET', url, false);
    http.send();
    return http.status!=404;
}
function checkFiles(){
    if(LinkCheck('upload.pcd')){
        var file = null;
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", 'upload.pcd', false);
        xmlhttp.send();
        if (xmlhttp.status==200)
            text = xmlhttp.response;
        
        console.log("name : " + file);
        crapdrawStuff('upload.pcd');
    }
    else{
        console.log("Nothing is here");
    }
}

function download(data, filename, type) {
    var file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a"),
                url = URL.createObjectURL(file);
                console.log(url);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);  
        }, 0); 
    }
}
function downloadFile(){
    if(text == null)
        alert('No files submitted')
    download(text,"export.pcd",".txt");
}


