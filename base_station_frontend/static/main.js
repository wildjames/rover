(function () {
    window.addEventListener('DOMContentLoaded', function () {
        var token_input = document.getElementById("api-token");
        var rover_address = document.getElementById("rover-address");
        var wake_status = document.getElementById("wake-status");
        var rover_waypoint_url = "https://wildjames.com/rover/";
        var wake_signal = false;
        var wake_interval;
        var api_token = "";


        function pingRover() {
            console.log("Pinging rover...");
            // Get the API token from the input field
            api_token = token_input.value;

            // Send a GET request to the controller ping endpoint
            var xhr = new XMLHttpRequest();
            // Make the get request asynchronously
            xhr.open('GET', rover_waypoint_url, true);
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

        rover_address.addEventListener("onchange", function () {
            rover_waypoint_url = rover_address.value + "/api/ping";
            console.log("Rover address changed to: " + rover_waypoint_url);
        });

        // Execute a function when the user presses a key on the keyboard
        token_input.addEventListener("keypress", function (event) {
            // If the user presses the "Enter" key on the keyboard
            if (event.key === "Enter") {
                // Cancel the default action
                event.preventDefault();
                console.log("Enter key pressed");

                if (wake_signal) {
                    // set an interval function that pings the rover every 5 seconds
                    wake_interval = setInterval(pingRover, 5000);
                    wake_signal = true;
                } else {
                    // stop the timer
                    clearInterval(wake_interval);
                    wake_signal = false;
                }
            }
        });
    });
})();