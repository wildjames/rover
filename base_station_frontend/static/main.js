(function () {
    window.addEventListener('DOMContentLoaded', function () {
        var wake_button = document.getElementById("send-wakeup");
        var token_input = document.getElementById("api-token");
        var api_token = "";

        function pingRover() {
            // Send a GET request to the controller server root
            var xhr = new XMLHttpRequest();
            // Make the get request asynchronously
            xhr.open('GET', './api/ping', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send();

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    console.log("Server responded to that API token!")
                    valid_api_token = true;
                } else if (xhr.readyState === 4 && xhr.status != 200) {
                    console.log("Could not access API with that token");
                    valid_api_token = false;
                }
            }
        }

        wake_button.addEventListener('click', function () {
            api_token = token_input.value;
            pingRover()
        });

        // Execute a function when the user presses a key on the keyboard
        token_input.addEventListener("keypress", function (event) {
            // If the user presses the "Enter" key on the keyboard
            if (event.key === "Enter") {
                // Cancel the default action
                event.preventDefault();

                api_token = token_input.value;
                pingRover();
            }
        });
    });
})();