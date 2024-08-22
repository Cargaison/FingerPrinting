import hashlib
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

url = 'https://www.optimize-matter.com/'
driver.get(url)

user_agent = driver.execute_script("return navigator.userAgent;")
screen_width = driver.execute_script("return window.screen.width;")
screen_height = driver.execute_script("return window.screen.height;")
color_depth = driver.execute_script("return window.screen.colorDepth;")
timezone = driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone;")
language = driver.execute_script("return navigator.language || navigator.userLanguage;")
webgl_renderer = driver.execute_script("""
    var canvas = document.createElement('canvas');
    var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (gl) {
        var debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        return gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
    }
    return '';
""")
cookies_enabled = driver.execute_script("return navigator.cookieEnabled;")

fingerprint_data = (
    f"user_agent={user_agent};"
    f"screen={screen_width}x{screen_height};"
    f"color_depth={color_depth};"
    f"timezone={timezone};"
    f"language={language};"
    f"webgl_renderer={webgl_renderer};"
    f"cookies_enabled={cookies_enabled}"
)

user_id = hashlib.sha256(fingerprint_data.encode('utf-8')).hexdigest()

print(f"User ID: {user_id}")
driver.quit()
