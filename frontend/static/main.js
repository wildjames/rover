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

        var led0 = document.getElementById('led0');
        var led1 = document.getElementById('led1');
        var led2 = document.getElementById('led2');

        var throttle_slider = document.getElementById("throttle_slider");
        var throttle_text = document.getElementById("throttle_value");
        var motor_init = document.getElementById("motor_toggle");

        throttle_text.innerHTML = throttle_slider.value; // Display the default slider value

        // Update the current slider value (each time you drag the slider handle)
        throttle_slider.oninput = function() {
            throttle_text.innerHTML = this.value;
        }

        function clear_button_styles() {
            // Sets the buttons to their default styles
            led0.style = null;
            led1.style = null;
            led2.style = null;

            motor_init.style = null;
            throttle_slider.value = 0
            throttle_text.innerHTML = 0
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

                    // By default, assume the motor is not initialized
                    motor_init.style.backgroundColor = 'black';
                    motor_init.textContent = 'Enable Motor';
                    motor_init.setAttribute('data-state', 0);

                    // Update the motor init button
                    var num_motors = response.motor_data.num_motors;
                    if (num_motors > 0) {
                        var motor = response.motor_data.motor_states[0];

                        if (motor.started) {
                            motor_init.style.backgroundColor = 'red';
                            motor_init.textContent = 'Disable Motor';
                            motor_init.setAttribute('data-state', motor.started ? 1 : 0);
                        }
                    } else {
                        throttle_slider.value = 0
                        throttle_text.innerHTML = 0
                    }

                } else if (xhr.readyState === 4 && xhr.status === 403) {
                    clear_button_styles()
                    return;
                };
            }

        }, 100);

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
            if (state == 0) {
                console.log("Sending init");
                xhr.open('POST', './api/motor_init', true);
            } else {
                console.log("Sending close");
                xhr.open('POST', './api/motor_close', true);
            }
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send();

            // TODO: When I get a response, I should update the throttle slider

        });

        // When a click is released from the slider, I need to send a message to the control server
        throttle_slider.addEventListener('mouseup', function(e) {
            // If the motor is not initialized, do nothing
            var state = motor_init.getAttribute('data-state');
            state = parseInt(state);
            if (state === 0) {
                return;
            }

            var value = parseFloat(this.value) / 100.0;
            console.log("Sending throttle value: " + value);

            // Make a POST request to the controller server
            var payload = JSON.stringify({
                "targets": [
                    [0, value]
                ]
            });
            console.log("Sending payload: " + payload);

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

            // The json payload is of the form {"states": [[1, newstate]]}
            var payload = JSON.stringify({
                "states": [
                    [ledIndex, newState]
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
            xhr.open('POST', './api/led_control', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send(payload);
        }

        led0.addEventListener('click', toggleLed, false);
        led1.addEventListener('click', toggleLed, false);
        led2.addEventListener('click', toggleLed, false);

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

        function submit_sleep_config() {
            if (!valid_api_token) {
                clear_button_styles();
                return;
            }

            var packet = JSON.stringify({
                "enable_sleep": sleep_toggle.getAttribute("data-state"),
                "sleep_threshold": sleep_time.value
            });
            console.log("sending json:");
            console.log(packet);

            // Send a POST request to the controller server /api/configure_sleep endpoint
            var xhr = new XMLHttpRequest();
            xhr.open('POST', './api/configure_sleep', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send(packet);

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log("Server responded to that API token!")
                    var response = JSON.parse(xhr.responseText);
                    console.log("Response: " + response);
                    valid_api_token = true;
                } else if (xhr.readyState === 4 && xhr.status != 200) {
                    console.log("Could not access API with that token");
                    valid_api_token = false;
                }
            }
        }

        // // Should detect gamepad connection and disconnection
        // const gamepads = {};

        // function gamepadHandler(event, connecting) {
        //     const gamepad = event.gamepad;
        //     // Note:
        //     // gamepad === navigator.getGamepads()[gamepad.index]

        //     if (connecting) {
        //         gamepads[gamepad.index] = gamepad;
        //     } else {
        //         delete gamepads[gamepad.index];
        //     }
        // }

        // window.addEventListener("gamepadconnected", (e) => { gamepadHandler(e, true); }, false);
        // window.addEventListener("gamepaddisconnected", (e) => { gamepadHandler(e, false); }, false);

        // window.addEventListener("gamepadconnected", (e) => {
        //     const gp = navigator.getGamepads()[e.gamepad.index];
        //     console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
        //         gp.index, gp.id,
        //         gp.buttons.length, gp.axes.length);
        // });
    });
})();