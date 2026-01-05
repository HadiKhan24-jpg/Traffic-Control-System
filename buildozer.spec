[app]
title = Traffic Control System
package.name = traffic_control_system
package.domain = org.ai.traffic
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,html,js,css
source.include_patterns = libs/*
version = 1.0.2
requirements = python3,kivy,android,pyjnius

orientation = landscape
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Required for local HTML file loading
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# This is the important part for WebView apps
android.minapi = 21
android.api = 31

[buildozer]
log_level = 2
warn_on_root = 1
