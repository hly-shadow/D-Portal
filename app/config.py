#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

APP_NAME = "D-Portal"

SHELF_WIDTH = 300
SHELF_HEIGHT = 600

BASE_DIR = Path(__file__).resolve().parent.parent

ICON_PATH = os.path.join(BASE_DIR, "resources", "icon", "favicon.ico")