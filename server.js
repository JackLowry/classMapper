const http = require("http");
const client = require('socket.io').listen(4000).sockets;
const uuidv1 = require('uuid/v1');
const fs = require('fs');
client.on('connection', function(socket){
    socket.on("upload", function(data){
      //data.file

      uuid = uuidv1();

      fs.writeFile("tmp/"+uuid, data.file, function(err) {
        if(err) {
            console.log("uh oh")
            return console.log(err);
        }

        schedule = {"Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[]}
        var spawn = require("child_process").spawn;
        var mapper = spawn('python3',["mapper.py", "tmp/"+uuid] );

        mapper.stderr.on('data', (data) => {
          console.error(`stderr: ${data}`);
        });

        mapper.on('close', (code) => {
           console.log(`child process exited with code ${code}`);

           if(data in schedule) {
             schedule[data].push()
           }
        });

      });

  });
});
