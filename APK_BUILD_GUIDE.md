# 📱 Professional APK Build Guide (Android)

If you are using **Google Colab**, the standard download button often fails with a "Failed to fetch" error. Please use this **Ultimate Automation Script** to build and download your APK safely.

## 🚀 The "One-Click" Colab Script
Copy and paste this entire block into a single cell in Google Colab and run it:

```python
# 1. Install System Dependencies
!sudo apt update
!sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
!pip3 install --user --upgrade buildozer

# 2. Reset the build environment (Fixes "webview" and cache errors)
!buildozer distclean

# 3. Start the build
# This will take 15-20 minutes the first time.
!buildozer android debug

# 4. Safe Download (Fixes "Failed to fetch" errors)
import os
from google.colab import files
import glob

# Search for the generated APK
apk_files = glob.glob("bin/*.apk")
if apk_files:
    latest_apk = max(apk_files, key=os.path.getctime)
    print(f"Build Success! Downloading: {latest_apk}")
    files.download(latest_apk)
else:
    print("Error: APK was not created. Please check the logs above.")
```

## 🛠️ Why did my download fail?
- **Small Files vs APKs**: Colab sometimes struggles with the large size of an APK directly through the file browser.
- **The Fix**: The `files.download()` command in the script above uses a more robust browser socket than the manual "Right-click > Download" method.

## 📁 Important: Before You Build
Ensure you have uploaded these files to your Colab root directory (`/content`):
1. `main.py`
2. `TrafficSystem3D.html`
3. `buildozer.spec`
4. `libs/` (The folder containing `three.min.js` and `OrbitControls.js`)

**Your APK will be ready in the `bin/` folder once the script finishes!**
