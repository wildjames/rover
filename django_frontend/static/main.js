(function () {
    var signalObj = null;

    window.addEventListener('DOMContentLoaded', function () {
        var isStreaming = false;
        var start = document.getElementById('start');
        var stop = document.getElementById('stop');
        var led0 = document.getElementById('led0');
        var led1 = document.getElementById('led1');
        var led2 = document.getElementById('led2');
        var canvas = document.getElementById('c');
        var video = document.getElementById('v');
        var ctx = canvas.getContext('2d');

        // Every 100ms, I need to run a function
        setInterval(function () {
            console.log("I will update the state of the LEDs");

            // Send a GET request to the controller server for the system state
            var xhr = new XMLHttpRequest();
            // Make the get request asynchronously
            xhr.open('GET', '/rover/system_info', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send();

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    console.log("Received response: " + xhr.responseText);
                    var ledStates = response.led_data.led_states;
                    console.log("LED states: " + ledStates);

                    // Update the state of the LEDs
                    led0.setAttribute('data-state', ledStates[0]);
                    led1.setAttribute('data-state', ledStates[1]);
                    led2.setAttribute('data-state', ledStates[2]);

                    // Update the color of the LEDs
                    if (ledStates[0] === 1) {led0.style.backgroundColor = 'red';} 
                    else {led0.style.backgroundColor = 'black';}

                    if (ledStates[1] === 1) {led1.style.backgroundColor = 'red';} 
                    else {led1.style.backgroundColor = 'black';}

                    if (ledStates[2] === 1) {led2.style.backgroundColor = 'red';} 
                    else {led2.style.backgroundColor = 'black';}

                }
            }

        }, 1000);

        led0.addEventListener('click', function (e) {
            // I need to send a toggle message to the server. First, get the state of the LED
            var state = led0.getAttribute('data-state');
            state = parseInt(state);

            // the LED index is the last character of the id
            var ledIndex = led0.id[led0.id.length - 1];
            ledIndex = parseInt(ledIndex);

            var newState = state === 1 ? 0 : 1;
            console.log("LED " + ledIndex + ". Old state: " + state + ", new state: " + newState);
            
            // Send a command POST request with a JSON payload to the controller server
            var xhr = new XMLHttpRequest();
            // Make the post request asynchronously
            xhr.open('POST', '/rover/led_control', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            // The json payload is of the form {"states": [[1, newstate]]}
            var payload = JSON.stringify({"states": [[ledIndex, newState]]});
            console.log("Sending payload: " + payload);
            xhr.send(payload);
        }, false);

        led1.addEventListener('click', function (e) {
            // I need to send a toggle message to the server. First, get the state of the LED
            var state = led1.getAttribute('data-state');
            state = parseInt(state);

            // the LED index is the last character of the id
            var ledIndex = led1.id[led1.id.length - 1];
            ledIndex = parseInt(ledIndex);

            var newState = state === 1 ? 0 : 1;
            console.log("LED " + ledIndex + ". Old state: " + state + ", new state: " + newState);
            
            // Send a command POST request with a JSON payload to the controller server
            var xhr = new XMLHttpRequest();
            // Make the post request asynchronously
            xhr.open('POST', '/rover/led_control', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            // The json payload is of the form {"states": [[1, newstate]]}
            var payload = JSON.stringify({"states": [[ledIndex, newState]]});
            console.log("Sending payload: " + payload);
            xhr.send(payload);
        }, false);

        led2.addEventListener('click', function (e) {
            // I need to send a toggle message to the server. First, get the state of the LED
            var state = led2.getAttribute('data-state');
            state = parseInt(state);

            // the LED index is the last character of the id
            var ledIndex = led2.id[led2.id.length - 1];
            ledIndex = parseInt(ledIndex);

            var newState = state === 1 ? 0 : 1;
            console.log("LED " + ledIndex + ". Old state: " + state + ", new state: " + newState);
            
            // Send a command POST request with a JSON payload to the controller server
            var xhr = new XMLHttpRequest();
            // Make the post request asynchronously
            xhr.open('POST', '/rover/led_control', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            // The json payload is of the form {"states": [[1, newstate]]}
            var payload = JSON.stringify({"states": [[ledIndex, newState]]});
            console.log("Sending payload: " + payload);
            xhr.send(payload);        }, false);

        start.addEventListener('click', function (e) {
            var address = '192.168.1.170:1002/webrtc';
            var protocol = location.protocol === "https:" ? "wss:" : "ws:";
            var wsurl = protocol + '//' + address;

            if (!isStreaming) {
                signalObj = new signal(wsurl,
                        function (stream) {
                            console.log('got a stream!');
                            //var url = window.URL || window.webkitURL;
                            //video.src = url ? url.createObjectURL(stream) : stream; // deprecated
                            video.srcObject = stream;
                            video.play();
                        },
                        function (error) {
                            alert(error);
                        },
                        function () {
                            console.log('websocket closed. bye bye!');
                            video.srcObject = null;
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                            isStreaming = false;
                        },
                        function (message) {
                            alert(message);
                        }
                );
            }
        }, false);

        stop.addEventListener('click', function (e) {
            if (signalObj) {
                signalObj.hangup();
                signalObj = null;
            }
        }, false);

        // Wait until the video stream can play
        video.addEventListener('canplay', function (e) {
            if (!isStreaming) {
                canvas.setAttribute('width', video.videoWidth);
                canvas.setAttribute('height', video.videoHeight);
                isStreaming = true;
            }
        }, false);

        // Wait for the video to start to play
        video.addEventListener('play', function () {
            // Every 33 milliseconds copy the video image to the canvas
            setInterval(function () {
                if (video.paused || video.ended) {
                    return;
                }
                var w = canvas.getAttribute('width');
                var h = canvas.getAttribute('height');
                ctx.fillRect(0, 0, w, h);
                ctx.drawImage(video, 0, 0, w, h);
            }, 33);
        }, false);

    });
})();