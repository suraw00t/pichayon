#!/usr/bin/bash


if [ ! -d venv ]
then
    echo "create python virtual env"
    python3 -m venv venv
else
    echo "python virtual env found"
fi


echo "install package"
sudo apt install -y rustc libssl-dev libffi-dev

source $(pwd)/venv/bin/activate
# export PYTHON=$(pwd)/venv/bin/python

echo "install poetry"
# $PYTHON -m pip install poetry
python -m pip install poetry

echo "install door controller"
cd door-controller
# $PYTHON -m poetry install 
python -m poetry install
cd ..



echo "copy service file"
sudo cp scripts/pichayon-door.service /lib/systemd/system

if [ ! -d /var/log/pichayon ]
then
    echo "create log directory"
    sudo mkdir /var/log/pichayon
    sudo chown -R $USER: /var/log/pichayon
else
    echo "pichayon log found"
fi



echo "enable service"
sudo systemctl daemon-reload
sudo systemctl enable pichayon-door.service

export CFLAGS="-fcommon"
