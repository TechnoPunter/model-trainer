#!/bin/sh
cd /var/www/model-trainer/
. /var/www/model-trainer/.venv/bin/activate

python /var/www/model-trainer/model-train.py 1> logs/exec-model-train.log 2> logs/exec-model-train.err

# Backup the files now
today="$(date -I)"
mkdir logs/archive/${today} 2> /dev/null

cp -r generated logs/archive/${today}/

month="$(date +"%Y%m")"
mkdir Trader/tv-data/low-tf-data/"${month}" 2> /dev/null
cp tv-data/low-tf-data/* Trader/tv-data/low-tf-data/"${month}"/

mv logs/model-train.log logs/archive/${today}/model-train.log.${today}
mv logs/exec-model-train.* logs/archive/${today}/
