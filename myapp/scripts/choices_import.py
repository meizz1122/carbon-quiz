# tbd to auto load question/choices from google sheets into model
# create __init__.py file in directory as well to be able to later import functions writtens here as a python package

import os
from pathlib import Path
from django.conf import settings


def test1():
    BASE_DIR = settings.BASE_DIR
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
    print(BASE_DIR)
    print(STATIC_ROOT)