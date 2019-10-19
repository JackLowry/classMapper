const http = require("http");
const client = require('socket.io').listen(4000).sockets;
const decodePolyline = require('decode-google-map-polyline');
client.on('connection', function(socket){
    socket.on("upload", function(data){
    //data.file
    var spawn = require("child_process").spawn;
    var process = spawn('python',["./mapper.py",
                            req.query.data.file] );
    process.stdout.on('data', function(data) {
      console.log(data);
    });
  });
    socket.emit("polyline",{line:decodePolyline(polyline)});
    console.log(decodePolyline(polyline));

});
var polyline = 'y~ivFtzmeMZaAf@wAcDmFM]EMMMh@gCd@mC@SA}@s@_Im@eHO{AMaB@]Ae@@k@LaA`A}E~@cE|A{HrAkGf@_DpAeK\\_Bd@cB`@}@\\YP?JEHMDQ?Q?GVoB`BsDpC}FBIc@c@w@u@YWKAcAaAgAeAE@OVIWCCSO?IfAaCo@k@}@u@EKAKVeANDP?LITa@F';
