#!/bin/sh
cd /var/www/model-trainer/
. /var/www/model-trainer/.venv/bin/activate

python /var/www/model-trainer/portfolio-analysis.py 1> logs/exec-portfolio-analysis.log 2> logs/exec-portfolio-analysis.err

# Backup the files now
today="$(date -I)"
mkdir logs/archive/${today} 2> /dev/null

cp -r generated logs/archive/${today}/

mv logs/portfolio-analysis.log logs/archive/${today}/portfolio-analysis.log.${today}
mv logs/exec-portfolio-analysis.* logs/archive/${today}/
