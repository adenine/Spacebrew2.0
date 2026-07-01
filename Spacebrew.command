#!/bin/bash
# Double-click this in Finder to launch the Spacebrew tray app.
cd "$(dirname "$0")"
exec python3 tray_app.py
