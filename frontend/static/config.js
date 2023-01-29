(function () {

    window.addEventListener('DOMContentLoaded', function () {
        var form = document.getElementById("config-form");
        var token_input = document.getElementById("api-token");

        var sleep_toggle = document.getElementById("enable-shutdown");
        var sleep_time = document.getElementById("inactivity-timeout");

        var save_button = document.getElementById("save-button");

        
        function handleForm(event) { 
            event.preventDefault();
            save();
        } 
        
        form.addEventListener('submit', handleForm);
        

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