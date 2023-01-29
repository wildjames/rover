(function () {
    window.addEventListener('DOMContentLoaded', function () {
        var token_input = document.getElementById("api-token");
        var rover_address = document.getElementById("rover-address");
        var wake_status = document.getElementById("wake-status");
        var go_to_rover_button = document.getElementById("go-to-rover");

        var rover_waypoint_url = "https://wildjames.com/rover";
        var waypoint_ping_suffix = "/api/ping";
        var wake_signal = false;
        var wake_interval;
        var api_token = "";

        rover_address.value = rover_waypoint_url;

        function pingRover() {
            console.log("Pinging rover at " + rover_waypoint_url + waypoint_ping_suffix);
            // Get the API token from the input field
            api_token = token_input.value;

            // Send a GET request to the controller ping endpoint
            var xhr = new XMLHttpRequest();
            // Make the get request asynchronously
            xhr.open('GET', rover_waypoint_url + waypoint_ping_suffix, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send();

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log("Server responded to that API token!")
                    valid_api_token = true;
                    wake_status.textContent = "🟢";
                } else if (xhr.readyState === 4 && xhr.status != 200) {
                    console.log("Could not access API with that token");
                    valid_api_token = false;
                    wake_status.textContent = "🔴";
                }
            }
        }

        function wakeRover() {
            if (!wake_signal) {
                console.log("Creating a wake signal");
                pingRover();
                // set an interval function that pings the rover every second
                wake_interval = setInterval(pingRover, 1000);
                wake_signal = true;
            } else {
                console.log("Stopping the wake signal");
                // stop the timer
                clearInterval(wake_interval);
                wake_signal = false;
                wake_status.textContent = "⚪";
            }
        }

        go_to_rover_button.addEventListener("click", function () {
            console.log("Going to rover");
            window.open(rover_waypoint_url, '_blank').focus();
            if (wake_signal) {
                wakeRover();
            }
        });

        rover_address.addEventListener("onchange", function () {
            console.log("Rover address changed to: " + rover_waypoint_url);
            rover_waypoint_url = rover_address.value;
        });

        // Execute a function when the user presses a key on the keyboard
        token_input.addEventListener("keypress", function (event) {
            // If the user presses the "Enter" key on the keyboard
            if (event.key === "Enter") {
                // Cancel the default action
                event.preventDefault();
                console.log("Enter key pressed");

                wakeRover();
            }
        });

        wake_status.addEventListener("click", function () {
            wakeRover();
        });
    });
})();