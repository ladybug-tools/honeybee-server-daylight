#!/usr/bin/env python
import os
import config
from app import app

if not os.path.isdir(config.UPLOAD_FOLDER):
    os.mkdir(config.UPLOAD_FOLDER)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
