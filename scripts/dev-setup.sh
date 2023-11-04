#!/bin/zsh

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

STRATS_PATH="$CURR_PATH"/../prediction-models/strategies
unlink trainer/strategies
ln -sf "$STRATS_PATH" trainer/strategies

mkdir logs
mkdir generated
mkdir tv-data
mkdir tv-data/low-tf-data
mkdir tv-data/base-data
read -p "Please Enter Dropbox Path: E.g. /Users/user/Dropbox: " -r dropbox
ln -sf "$dropbox"/Trader .

echo "Done!"