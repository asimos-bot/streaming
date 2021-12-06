var WebCamera  = require('webcamjs');
const screenshot = require('screenshot-desktop');
var socket = require('socket.io-client')('IP');
const { v4: uuidv4 } = require('uuid');
let enabled = false;
var interval;

document.getElementById("camButton").addEventListener('click',function(){
    console.log('Entrei')
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


document.getElementById("startStream").addEventListener('click',function(event) {
    // var uuid = uuidv4();
    // socket.emit("join-message", uuid);
    // event.reply("uuid", uuid);

    // interval = setInterval(function() {
    //     screenshot().then((img) => {
    //         var imgStr = new ArrayBuffer(img).toString('base64');
    //         var obj = {};
    //         obj.image = imgStr;
    //         obj.room = uuid;

    //         socket.emit("screen-data", JSON.stringify(obj));
    //     }). catch((e) => { console.log(e)})
    // }, 100)  
    const config = { method: 'GET' };

    fetch('LIST_VIDEOS',config).then(function(response) {
            console.log(response);
    })
    
});
    
function closeStream() {
    clearInterval(interval);
}


