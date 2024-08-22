import hashlib
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import firebase_admin
from firebase_admin import credentials, firestore
from scapy.all import sniff, get_if_list
import warnings

# Ignorer les avertissements spécifiques
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Initialiser Firebase Admin SDK
cred = credentials.Certificate('fingerprinting-fb811-firebase-adminsdk-625eq-33245b9c8d.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialiser ChromeDriver avec Selenium
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# URL pour tester la connexion
url = 'https://www.optimize-matter.com/'
driver.get(url)

# Récupérer diverses propriétés pour le fingerprint
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

# Empreinte Canvas
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

# Obtenir l'adresse IP publique
ip_response = requests.get('https://api.ipify.org?format=json')
ip_address = ip_response.json()['ip']

# Identifier automatiquement l'interface réseau active
def find_active_interface():
    interfaces = get_if_list()
    for iface in interfaces:
        if "Loopback" in iface:
            return iface
        if "Ethernet" in iface or "Wi-Fi" in iface or "Local Area" in iface:
            return iface
    return interfaces[0]  # Si aucune correspondance spécifique, retourner la première interface

# Debug: Afficher les interfaces disponibles
print("Available interfaces:", get_if_list())

active_interface = find_active_interface()
print("Using interface:", active_interface)

# Capture des paquets sur le port 443 avec Scapy
def capture_https_packets(interface=active_interface, count=10):
    packets = sniff(iface=interface, filter='tcp port 443', count=count)
    return packets

# Appeler la fonction pour capturer les paquets HTTPS
tls_packets = capture_https_packets()

# Placeholder pour l'analyse TLS
tls_versions = ["TLS packet captured"] * len(tls_packets)
cipher_suites = ["Not analyzed"] * len(tls_packets)

# Générer les données de l'empreinte
fingerprint_data = {
    'user_agent': user_agent,
    'screen_resolution': f"{screen_width}x{screen_height}",
    'color_depth': color_depth,
    'timezone': timezone,
    'language': language,
    'webgl_renderer': webgl_renderer,
    'cookies_enabled': cookies_enabled,
    'canvas_fingerprint': canvas_fingerprint,
    'ip_address': ip_address,
    'tls_versions': tls_versions,
    'cipher_suites': cipher_suites,
}

# Générer un identifiant utilisateur unique
user_id = hashlib.sha256(str(fingerprint_data).encode('utf-8')).hexdigest()

# Vérifier si la clé existe déjà dans Firestore
doc_ref = db.collection('user_fingerprints').document(user_id)
doc = doc_ref.get()

if doc.exists:
    print("present")
else:
    doc_ref.set(fingerprint_data)
    print("new")

# Fermer le navigateur
driver.quit()
