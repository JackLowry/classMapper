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

      fs.writeFile("tmp/"+uuid, "" + data.home + "\n" + data.file, function(err) {
        if(err) {
            console.log("uh oh")
            return console.log(err);
        }

        var schedule = {"Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[]}
        var spawn = require("child_process").spawn;
        var mapper = spawn('python3',["mapper.py", "tmp/"+uuid] );

        mapper.stderr.on('data', (data) => {
          console.error(`stderr: ${data}`);
        });

        class_details = null;
        mapper.on('close', (code) => {
           console.log(`child process exited with code ${code}`);

           fs.readFile('tmp/' + uuid + '_response', (err, data) => {
             if(err) throw err;

             lines = data.toString().split("\n")

             class_details = lines[0]
             console.log("class_details: " + class_details + "\n")
             socket.emit("textSchedule",class_details);

             for(i = 1; i < lines.length; i++) {
               if(lines[i] in schedule) {
                 let day = lines[i];
                 while(!(lines[i+1] in schedule) && (i+1 < lines.length) && lines[i+1]){
                   i++;
                   schedule[day].push(lines[i])
                 }
                 console.log("" + day + " length: " + schedule[day].length)
               }
             }
           fs.unlink('tmp/' + uuid + '_response')

           console.log(schedule)
           getDayRoute("Monday");
           socket.on('getDayRouteSocket',function(day){
             getDayRoute(day);
           });

            //for(let day in schedule){
          function getDayRoute(day)
          {
            //console.log(day);
            points = []
            destinations = []
            //console.log(schedule);
            if(schedule[day].length > 0) {
              route = JSON.parse(schedule[day][0])["routes"][0]
              destinations.push({"location":route["legs"][0]["start_location"], "address":route["legs"][0]["start_address"]})
              //console.log(": " + JSON.stringify(destinations[destinations.length-1]) + " day: " + day + " item: " + -1 +"\n")
              //console.log("points length:" + points.length + "\n")
            }
              for(i = 0; i < schedule[day].length; i++) {
                route = JSON.parse(schedule[day][i])["routes"][0]
                routeLine = route["overview_polyline"]["points"]
                destinations.push({"location":route["legs"][0]["end_location"], "address":route["legs"][0]["end_address"]})
                //console.log("dest_stuff: " + JSON.stringify(destinations[destinations.length-1]) + " day: " + day + " item: " + i + "\n")
                decodedLine = routeLine.replace(/\"/g, "")
                decodedLine = decodePolyline(decodedLine)
                points = points.concat(decodedLine)
                //console.log("points length:" + points.length + "\n")
              }
            socket.emit("polyline",{line:points, destinations:destinations});
            }




           })
        });

      });

  });

});
