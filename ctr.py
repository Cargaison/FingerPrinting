from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))



url = 'https://www.google.com'
driver.get(url)

canvas_fingerprint = driver.execute_script("""
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText('Hello, world!', 2, 15);
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.fillText('Hello, world!', 4, 17);
    return canvas.toDataURL();
""")

ip_response = requests.get('https://api.ipify.org?format=json')
ip_address = ip_response.json()['ip']

# Combiner l'empreinte Canvas avec l'adresse IP
unique_string = f"{canvas_fingerprint}_{ip_address}"

print(f"Unique String: {unique_string}")


driver.quit()