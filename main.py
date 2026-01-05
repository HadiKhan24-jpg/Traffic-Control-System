import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

# The goal of this script is to launch the native Android WebView 
# and load our TrafficSystem3D.html.

class TrafficMobileApp(App):
    def build(self):
        # We start with a blank layout. The native WebView will overlap this.
        layout = FloatLayout()
        
        # Schedule the WebView launch after the app starts
        Clock.schedule_once(self.create_webview, 0.5)
        return layout

    def create_webview(self, *args):
        from kivy.utils import platform
        
        # If we are not on Android, show the descriptive message
        if platform != 'android':
            from kivy.uix.label import Label
            self.root.add_widget(Label(text=f"This simulation requires Android Hardware.\n(Current: {platform})", halign='center'))
            return

        try:
            from jnius import autoclass
            from android.runnable import run_on_main_thread

            @run_on_main_thread
            def setup_webview():
                try:
                    WebView = autoclass('android.webkit.WebView')
                    WebViewClient = autoclass('android.webkit.WebViewClient')
                    WebChromeClient = autoclass('android.webkit.WebChromeClient')
                    Activity = autoclass('org.kivy.android.PythonActivity').mActivity
                    View = autoclass('android.view.View')
                    
                    import os
                    base_path = os.path.join(Activity.getFilesDir().getAbsolutePath(), 'app')
                    file_path = os.path.join(base_path, 'TrafficSystem3D.html')
                    
                    webview = WebView(Activity)
                    settings = webview.getSettings()
                    settings.setJavaScriptEnabled(True)
                    settings.setDomStorageEnabled(True)
                    settings.setAllowFileAccess(True)
                    settings.setAllowFileAccessFromFileURLs(True)
                    settings.setAllowUniversalAccessFromFileURLs(True)
                    
                    # Force hardware acceleration
                    webview.setLayerType(View.LAYER_TYPE_HARDWARE, None)
                    
                    webview.setWebViewClient(WebViewClient())
                    webview.setWebChromeClient(WebChromeClient())
                    
                    webview.loadUrl('file://' + file_path)
                    Activity.setContentView(webview)
                except Exception as inner_e:
                    from kivy.uix.label import Label
                    self.root.add_widget(Label(text=f"WebView Setup Error:\n{str(inner_e)}", halign='center'))

            setup_webview()
        except Exception as e:
            from kivy.uix.label import Label
            self.root.add_widget(Label(text=f"Android Boot Error:\n{str(e)}", halign='center'))

if __name__ == '__main__':
    TrafficMobileApp().run()
