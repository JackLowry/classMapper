const http = require("http");
const client = require('socket.io').listen(4000).sockets;
const uuidv1 = require('uuid/v1');
const fs = require('fs');
const decodePolyline = require('decode-google-map-polyline');
client.on('connection', function(socket){
    socket.on("upload", function(data){
      console.log("upload recieved")
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

           fs.readFile('tmp/' + uuid + '_response', (err, data) => {
             if(err) throw err;

             lines = data.toString().split("\n")
             for(i = 0; i < lines.length; i++) {
               if(lines[i] in schedule) {
                 let day = lines[i];
                 while(!(lines[i+1] in schedule) && (i+1 < lines.length) && lines[i+1]){
                   i++;
                   schedule[day].push(lines[i])
                 }
               }
             }

           console.log(schedule)

            //for(let day in schedule){
            let day = "Monday"
            points = []
            destinations = []
            if(schedule[day].length > 0) {
              destinations.push(JSON.parse(schedule[day][0])["routes"]["legs"][0][start_address])
            }
              for(i = 0; i < schedule[day].length; i++) {
                trip = JSON.parse(schedule[day][i])["routes"][0]["overview_polyline"]["points"]
                destinations.push(JSON.parse(schedule[day][0])["routes"]["legs"][i][end_address])
                decodedLine = trip.replace(/\"/g, "")
                decodedLine = decodePolyline(decodedLine)
                points = points.concat(decodedLine)
                console.log(i)
              }
            socket.emit("polyline",{line:points});
            //}

           })
        });

      });

  });

});
