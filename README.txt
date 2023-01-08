So the basic communication via Flask works ok, and can easily parse out JSON messages. However, to get pin control (which I'll probably need), the process has to be running as root. 
It's probably best to have the Flask portion handle the server stuff, and simply pass the JSON out to another python process that does tha actual GPIO/reaction stuff. 
Call them the communicatior, and the controller respectively. For getting data to the controller, rabbitmq is apparently quite good for interprocess communication.
https://www.rabbitmq.com/tutorials/tutorial-one-python.html

I will have the Flask interface in the top directory, and keep hardware interfaces in the controller directory.
