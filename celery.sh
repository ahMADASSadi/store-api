#! /bin/bash

celery -A config worker --beat -l INFO
