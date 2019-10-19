const http = require("http");
const client = require('socket.io').listen(4000).sockets;
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
});
