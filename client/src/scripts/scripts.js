var WebCamera  = require('webcamjs');
const screenshot = require('screenshot-desktop');
let enabled = false;
var interval;

document.getElementById("camButton").addEventListener('click',function(){
    if(!enabled){
        enabled = true;
        WebCamera.attach('#camdemo');
        console.log("The camera has been started");
    }else{
        enabled = false;
        WebCamera.reset();
        console.log("The camera has been disabled");
    }
},false);


function startStream() {
    interval = setInterval(function() {
        screenshot().then((img) => {
            var imgStr = new Buffer(img).toString('base64');
            var obj = {};
            obj.image = imgStr;
        }). catch((e) => { console.log(e)})
    }, 100)  
}
    
function closeStream() {
    clearInterval(interval);
}
