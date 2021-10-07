sudo apt install rustc libssl-dev libffi-dev
sudo cp scripts/pichayon-door.service /lib/systemd/system
sudo mkdir /var/log/pichayon
sudo chown -R $USER: /var/log/pichayon
sudo systemctl daemon-reload
sudo systemctl enable pichayon-door.service
