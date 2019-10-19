const http = require("http");
const client = require('socket.io').listen(4000).sockets;
client.on('connection', function(socket){
    socket.on("upload", function(data){
    //data.file
  });
});
