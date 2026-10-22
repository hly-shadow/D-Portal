#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from pathlib import Path

APP_NAME = "D-Portal"

SHELF_WIDTH = 500
SHELF_HEIGHT = 440

BASE_DIR = Path(__file__).resolve().parent.parent

ICON_PATH = os.path.join(BASE_DIR, "resources", "icon", "favicon.ico")