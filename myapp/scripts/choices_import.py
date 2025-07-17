# tbd to auto load question/choices from google sheets into model
# create __init__.py file in directory as well to be able to later import functions writtens here as a python package

import os
from pathlib import Path

def test1():
    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 
    print(STATIC_ROOT)