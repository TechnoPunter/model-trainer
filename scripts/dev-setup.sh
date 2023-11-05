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
cd trainer || exit 1
ln -sf "$STRATS_PATH" .

mkdir logs
mkdir generated
mkdir generated/summary
mkdir tv-data
mkdir tv-data/low-tf-data
mkdir tv-data/base-data
read -p "Please Enter Dropbox Path: E.g. /Users/user/Dropbox: " -r dropbox

if [[ -d $dropbox ]]; then
  sleep 1
else
  echo "Please check $dropbox directory!"
  exit 1
fi

ln -sf "$dropbox"/Trader .
echo "Done!"