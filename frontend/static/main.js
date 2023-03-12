(function() {
    var signalObj = null;

    window.addEventListener('DOMContentLoaded', function() {
        var canvas = document.getElementById('canvas');
        var video = document.getElementById('video');
        var ctx = canvas.getContext('2d');

        var isStreaming = false;
        var stream_toggle = document.getElementById('streaming_toggle');

        var token_input = document.getElementById("api_token");
        var api_token = "";
        var valid_api_token = false;

        var relay0 = document.getElementById('relay0');
        var relay1 = document.getElementById('relay1');
        var relay2 = document.getElementById('relay2');

        var motor_init = document.getElementById("motor_toggle");


        function clear_button_styles() {
            // Sets the buttons to their default styles
            relay0.style = null;
            relay1.style = null;
            relay2.style = null;

            motor_init.style = null;
        };


        function pingRover() {
            // Send a GET request to the controller server root
            var xhr = new XMLHttpRequest();
            // Make the get request asynchronously
            xhr.open('GET', './api/ping', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send();

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log("Server responded to that API token!")
                    valid_api_token = true;
                } else if (xhr.readyState === 4 && xhr.status != 200) {
                    console.log("Could not access API with that token");
                    valid_api_token = false;
                    alert("Invalid API token!")
                }
            }
        };


        // Execute a function when the user presses a key on the keyboard
        token_input.addEventListener("keypress", function(event) {
            // If the user presses the "Enter" key on the keyboard
            if (event.key === "Enter") {
                // Cancel the default action
                event.preventDefault();

                api_token = token_input.value;
                pingRover();
            }
        });


        // I periodically get the system state from the server
        setInterval(function() {
            // If I'm streaming, set the button text to reflect that
            if (isStreaming) {
                stream_toggle.textContent = "Stop Streaming";
                stream_toggle.style.backgroundColor = "red";
            } else {
                stream_toggle.textContent = "Start Streaming";
                stream_toggle.style.backgroundColor = "black";
            }

            // All API requests need to authenticated with a bearer token in the header
            if (!valid_api_token) {
                clear_button_styles();
                return;
            }

            // Send a GET request to the controller server for the system state
            var xhr = new XMLHttpRequest();
            // Make the get request asynchronously
            xhr.open('GET', './api/system_info', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send();

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);

                    var relayStates = response.relay_data.relay_states;

                    // Update the color of the relays
                    var relays = [relay0, relay1, relay2];
                    for (var i = 0; i < relays.length; i++) {
                        var relay = relays[i];

                        var mystate = -1;
                        for (var j = 0; j < relayStates.length; j++) {
                            if (parseInt(relayStates[j][0]) === i) {
                                mystate = parseInt(relayStates[j][1]);
                                break;
                            }
                        }

                        relay.setAttribute('data-state', mystate);

                        if (mystate === 1) {
                            relay.style.backgroundColor = 'red';
                        } else if (mystate === 0) {
                            relay.style.backgroundColor = 'black';
                        } else {
                            relay.style.backgroundColor = 'gray';
                        }
                    }

                } else if (xhr.readyState === 4 && xhr.status === 403) {
                    clear_button_styles()
                    return;
                };
            }
        }, 100);

        //
        // Relay Functions
        //

        function toggleRelay() {
            // I need to send a toggle message to the server. First, get the state of the relay
            var state = this.getAttribute('data-state');
            state = parseInt(state);

            // the relay index is the last character of the id
            var relayIndex = this.id[this.id.length - 1];
            relayIndex = parseInt(relayIndex);

            var newState = state === 1 ? 0 : 1;
            console.log("relay " + relayIndex + ". Old state: " + state + ", new state: " + newState);

            // The json payload is of the form {"states": [[1, newstate]]}
            var payload = JSON.stringify({
                "states": [
                    [relayIndex, newState]
                ]
            });
            console.log("Sending payload: " + payload);

            // All API requests need to authenticated with a bearer token in the header
            if (!valid_api_token) {
                clear_button_styles();
                return;
            }

            // Send a command POST request with a JSON payload to the controller server
            var xhr = new XMLHttpRequest();

            // Make the post request asynchronously
            xhr.open('POST', './api/relay_control', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send(payload);
        }

        relay0.addEventListener('click', toggleRelay, false);
        relay1.addEventListener('click', toggleRelay, false);
        relay2.addEventListener('click', toggleRelay, false);

        //
        // Video streaming functions
        //

        stream_toggle.addEventListener('click', function(e) {
            // This is the IP of the server running the camera stream.
            var address = location.hostname + location.pathname + '/video';
            var protocol = location.protocol === "https:" ? "wss:" : "ws:";
            var wsurl = protocol + '//' + address;
            //var wsurl = stream_uri;

            if (!isStreaming) {
                // Change the canvas color to white
                canvas.style.backgroundColor = 'var(--tyrian-purple)';
                canvas.style.cursor = 'progress';

                signalObj = new signal(wsurl,
                    function(stream) {
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
                    function(error) {
                        canvas.style.cursor = "default";
                        alert(error);
                    },
                    function() {
                        console.log('websocket closed. bye bye!');
                        video.srcObject = null;
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        isStreaming = false;
                        canvas.style.cursor = "default";
                    },
                    function(message) {
                        canvas.style.cursor = "default";
                        alert(message);
                    }
                );
            } else {
                canvas.style.backgroundColor = 'var(--midnight-green-eagle-green)';
                if (signalObj) {
                    signalObj.hangup();
                    signalObj = null;
                }
            }
        }, false);

        // Wait until the video stream can play
        video.addEventListener('canplay', function(e) {
            if (!isStreaming) {
                canvas.setAttribute('width', video.videoWidth);
                canvas.setAttribute('height', video.videoHeight);
                isStreaming = true;
                canvas.style.cursor = "default";
            }
        }, false);

        // Wait for the video to start to play
        video.addEventListener('play', function() {
            // Every 33 milliseconds copy the video image to the canvas
            setInterval(function() {
                if (video.paused || video.ended) {
                    return;
                }
                var w = canvas.getAttribute('width');
                var h = canvas.getAttribute('height');
                ctx.fillRect(0, 0, w, h);
                ctx.drawImage(video, 0, 0, w, h);
            }, 33);
        }, false);

        //
        // Motor Functions
        //

        motor_init.addEventListener('click', function(e) {
            // I need to send a toggle message to the server. First, get the state of the motor
            var state = this.getAttribute('data-state');
            state = parseInt(state);

            // All API requests need to authenticated with a bearer token in the header
            if (!valid_api_token) {
                clear_button_styles();
                return;
            }

            var xhr = new XMLHttpRequest();
            var payload = {
                "command": "",
            };

            if (state == 0) {
                console.log("Sending init");
                payload.command = "init_motors";

                this.setAttribute("data-state", 1);
            } else {
                console.log("Sending close");
                payload.command = "close_motors";

                this.setAttribute("data-state", 0);
            }

            var sendme = JSON.stringify(payload);

            console.log("Sending motor command: " + sendme);

            xhr.open('POST', './api/motor_command', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send(sendme);

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log(xhr.responseText);
                }
            };
        });

        function setMotorState(fr, fl) {
            // Make a POST request to the controller server
            var payload = JSON.stringify({
                "command": "set_speed",
                "payload": {
                    "fl": fl,
                    "fr": fr,
                }
            });
            console.log("Throttle sending payload: " + payload);

            // All API requests need to authenticated with a bearer token in the header
            if (!valid_api_token) {
                clear_button_styles();
                return;
            }

            var xhr = new XMLHttpRequest();

            xhr.open('POST', './api/motor_command', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send(payload);

            // print the response to the console
            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log("Response: " + xhr.responseText);
                } else if (xhr.readyState === 4 && xhr.status === 403) {
                    clear_button_styles()
                    return;
                };
            }
        }

        //
        // Gamepad functions
        //

        // Should detect gamepad connection and disconnection
        const gamepads = {};

        function gamepadHandler(event, connecting) {
            const gamepad = event.gamepad;

            if (connecting) {
                gamepads[gamepad.index] = gamepad;
            } else {
                delete gamepads[gamepad.index];
            }
        }

        function pollGamepads() {
            // Get controller
            const [gp] = navigator.getGamepads();
            if (!gp) {
                return;
            }

            var left_speed = (gp.axes[1] * -200.0);
            if ((left_speed < 20) && (left_speed > -20)) {
                left_speed = 0;
            }

            var right_speed = (gp.axes[3] * -200.0);
            if ((right_speed < 20) && (right_speed > -20)) {
                right_speed = 0;
            }

            setMotorState(Math.round(right_speed), Math.round(left_speed));
        }

        setInterval(pollGamepads, 50);

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