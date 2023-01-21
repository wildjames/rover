git pull
sudo systemctl restart flask_middleware.service
sudo systemctl restart hardware_controller.service
sudo systemctl reload nginx.service
echo "Done"