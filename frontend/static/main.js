(function () {
    var signalObj = null;

    window.addEventListener('DOMContentLoaded', function () {        
        var canvas = document.getElementById('c');
        var video = document.getElementById('v');
        var ctx = canvas.getContext('2d');

        var isStreaming = false;
        var start = document.getElementById('start');
        var stop = document.getElementById('stop');

        var led0 = document.getElementById('led0');
        var led1 = document.getElementById('led1');
        var led2 = document.getElementById('led2');

        var slider = document.getElementById("throttleSlider");
        var output = document.getElementById("throttleValue");
        var motor_init = document.getElementById("motorInit");
        
        output.innerHTML = slider.value; // Display the default slider value
        
        // Update the current slider value (each time you drag the slider handle)
        slider.oninput = function() {
          output.innerHTML = this.value;
        }

        // Every 100ms, I need to run a function
        setInterval(function () {
            // Send a GET request to the controller server for the system state
            var xhr = new XMLHttpRequest();
            // Make the get request asynchronously
            xhr.open('GET', '/api/system_info', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send();

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);
                    
                    var ledStates = response.led_data.led_states;

                    // Update the color of the LEDs
                    var leds = [led0, led1, led2];
                    for (var i = 0; i < leds.length; i++) {
                        var led = leds[i];


                        var mystate = -1;
                        for (var j = 0; j < ledStates.length; j++) {
                            if (parseInt(ledStates[j][0]) === i) {
                                mystate = parseInt(ledStates[j][1]);
                                break;
                            }
                        }

                        led.setAttribute('data-state', mystate);

                        if (mystate === 1) {
                            led.style.backgroundColor = 'red';
                        } else if (mystate === 0) {
                            led.style.backgroundColor = 'black';
                        } else {
                            led.style.backgroundColor = 'gray';
                        }
                    }


                    var num_motors = response.motor_data.num_motors;

                    // By default, assume the motor is not initialized
                    motor_init.style.backgroundColor = 'black';
                    motor_init.textContent = 'Enable Motor';
                    motor_init.setAttribute('data-state', 0);
                
                    // Update the motor init button
                    if (num_motors > 0) {
                        console.log("I have a motor! " + num_motors);
                        var motorStates = response.motor_data.motor_states;
                        motor = motorStates[0];
                        console.log("Motor state: ");
                        var started = motor.started == "true";
                        console.log(started);
                        if (started) {
                            motor_init.style.backgroundColor = 'red';
                            motor_init.textContent = 'Disable Motor';
                            motor_init.setAttribute('data-state', started ? 1 : 0);
                        } 
                    } 
                    
                }
            }

        }, 200);


        motor_init.addEventListener('click', function (e) {
            // I need to send a toggle message to the server. First, get the state of the motor
            var state = this.getAttribute('data-state');
            state = parseInt(state);

            var xhr = new XMLHttpRequest();
            if (state == 0) {
                console.log("Sending init");
                xhr.open('POST', '/api/motor_init', true);
            } else {
                console.log("Sending close");
                xhr.open('POST', '/api/motor_close', true);
            }
            xhr.send();
        });


        function toggleLed() {
            // I need to send a toggle message to the server. First, get the state of the LED
            var state = this.getAttribute('data-state');
            state = parseInt(state);

            // the LED index is the last character of the id
            var ledIndex = this.id[this.id.length - 1];
            ledIndex = parseInt(ledIndex);

            var newState = state === 1 ? 0 : 1;
            console.log("LED " + ledIndex + ". Old state: " + state + ", new state: " + newState);

            // Send a command POST request with a JSON payload to the controller server
            var xhr = new XMLHttpRequest();
            // Make the post request asynchronously
            xhr.open('POST', '/api/led_control', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            // The json payload is of the form {"states": [[1, newstate]]}
            var payload = JSON.stringify({ "states": [[ledIndex, newState]] });
            console.log("Sending payload: " + payload);
            xhr.send(payload);
        }

        led0.addEventListener('click', toggleLed, false);
        led1.addEventListener('click', toggleLed, false);
        led2.addEventListener('click', toggleLed, false);

        start.addEventListener('click', function (e) {
            // This is the IP of the server running the camera stream.
            // TODO: Make sure that port 1002 is public!
            // TODO: Use a better way to get the address of the server
            var address = 'roverpi.local:1002/webrtc';
            var protocol = location.protocol === "https:" ? "wss:" : "ws:";
            var wsurl = protocol + '//' + address;

            if (!isStreaming) {
                // Change the canvas color to white
                canvas.style.backgroundColor = 'var(--tyrian-purple)';

                signalObj = new signal(wsurl,
                    function (stream) {
                        console.log('got a stream!');

                        // Play the stream in browser. Need to handle promises properly.
                        video.srcObject = stream;
                        var playPromise = video.play();

                        if (playPromise !== undefined) {
                            playPromise.then(_ => {
                                // Automatic playback started!
                                // Show playing UI.
                            })
                                .catch(error => {
                                    // Auto-play was prevented
                                    // Show paused UI.
                                });
                        }
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
            canvas.style.backgroundColor = 'var(--midnight-green-eagle-green)';
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

        // Should detect gamepad connection and disconnection
        const gamepads = {};

        function gamepadHandler(event, connecting) {
          const gamepad = event.gamepad;
          // Note:
          // gamepad === navigator.getGamepads()[gamepad.index]
        
          if (connecting) {
            gamepads[gamepad.index] = gamepad;
          } else {
            delete gamepads[gamepad.index];
          }
        }
        
        window.addEventListener("gamepadconnected", (e) => { gamepadHandler(e, true); }, false);
        window.addEventListener("gamepaddisconnected", (e) => { gamepadHandler(e, false); }, false);

        window.addEventListener("gamepadconnected", (e) => {
            const gp = navigator.getGamepads()[e.gamepad.index];
            console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
              gp.index, gp.id,
              gp.buttons.length, gp.axes.length);
          });
    });
})();