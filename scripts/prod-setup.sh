#!/bin/zsh

# Need to reach Project Root
MODULE_NAME=model-trainer
CURR_PATH=$(pwd)

if [[ $CURR_PATH == *$MODULE_NAME* ]]; then
  sleep 1
else
  echo "Need to run from $MODULE_NAME location"
  exit 1
fi

if [[ $CURR_PATH == *scripts* ]]; then
  CURR_PATH="${CURR_PATH%%scripts*}"
fi

cd "$CURR_PATH" || exit 1


# Install & create venv
sudo apt-get install python-virtualenv
virtualenv --python=/usr/bin/python3.10 .venv

source .venv/bin/activate
pip install -r requirements.txt

mkdir logs
mkdir generated
mkdir generated/summary
mkdir tv-data
mkdir tv-data/low-tf-data
mkdir tv-data/base-data
read -p "Please Enter Dropbox Path: E.g. /Users/user/Dropbox: " -r dropbox
ln -sf "$dropbox"/Trader .
ln -sf "$dropbox"/Trader/secret .
cd logs || exit 1
ln -sf "$dropbox"/Trader/model-trainer-V1/logs/archive .

echo "Please create / check secrets-local.yaml file in resources/config directory!"
echo "Done!"