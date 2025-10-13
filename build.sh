#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python init_db.py         # <-- Add this line
python clean_empty_student_id.py
