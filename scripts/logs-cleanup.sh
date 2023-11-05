#!/bin/bash

cd /var/www/model-trainer/logs/archive

DAYS_TO_KEEP=5

# Find and delete logs older than the specified number of days
find . -maxdepth 1 -type d -mtime +$DAYS_TO_KEEP -exec rm -r {} \;
