(function () {

    window.addEventListener('DOMContentLoaded', function () {
        var form = document.getElementById("config-form");
        var token_input = document.getElementById("api-token");

        var sleep_toggle = document.getElementById("enable-shutdown");
        var sleep_time = document.getElementById("inactivity-timeout");

        var save_button = document.getElementById("save-button");

        
        function handleForm(event) { 
            event.preventDefault();
        } 
        
        form.addEventListener('submit', handleForm);
        
        // I periodically get the system state from the server
        function get_current_config() {
            var api_token = token_input.value;

            // Send a GET request to the controller server for the system state
            var xhr = new XMLHttpRequest();
            // Make the get request asynchronously
            xhr.open('GET', './api/system_info', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader("Authorization", "Bearer " + api_token);
            xhr.send();

            xhr.onreadystatechange = function () {
                if (xhr.readyState === 4 && xhr.status === 200) {
                    var response = JSON.parse(xhr.responseText);

                    console.log("Got this response:");
                    console.log(response);

                    // update the sleep_enable state
                    var sleep_enable = response.sleep_data.enable_sleep;
                    console.log("Sleep enable: " + sleep_enable);
                    sleep_enable = parseInt(sleep_enable);
                    sleep_toggle.checked = sleep_enable;

                    // update the sleep time
                    var sleep_time_val = response.sleep_data.sleep_time;
                    console.log("Sleep time: " + sleep_time_val);
                    sleep_time.value = sleep_time_val;

                    alert("Updated!");

                } else if (xhr.readyState === 4) {
                    alert("Error: " + xhr.status);
                    return;
                };
            }
        }

        token_input.addEventListener("keypress", function (event) {
            // If the user presses the "Enter" key on the keyboard
            if (event.key === "Enter") {
                // Cancel the default action
                event.preventDefault();

                get_current_config();
            }
        });

        function save() {
            console.log("Saving...");

            var token = token_input.value;
            var sleep = sleep_toggle.checked;
            var sleep_time_val = sleep_time.value;

            var data = {
                "sleep_enable": sleep,
                "sleep_time": sleep_time_val
            };

            console.log("Sending data");
            console.log(data);
            console.log("Token: " + token);

            var xhr = new XMLHttpRequest();
            xhr.open("POST", "./api/config", true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('Authorization', 'Bearer ' + token);
            xhr.send(JSON.stringify(data));

            xhr.onloadend = function () {
                if (xhr.status == 200) {
                    console.log("Response JSON: " + xhr.responseText);
                    alert("Saved!");
                } else {
                    console.log("Response JSON: " + xhr.responseText);
                    alert("Error: " + xhr.status);
                }
            }
        }

        save_button.addEventListener("click", save);

    });
})();