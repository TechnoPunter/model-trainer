#!/usr/bin/env sh
cd /var/www/model-trainer
. .venv/bin/activate
pip uninstall -y TechnoPunter-Commons
pip install -r requirements.txt