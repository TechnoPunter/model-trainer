#!/usr/bin/env sh
cd /var/www/model-trainer
. .venv/bin/activate
pip install --upgrade pip
pip uninstall -y TechnoPunter-Commons
pip install -r requirements.txt