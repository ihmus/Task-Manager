import os

DB_NAME="md.db"
DB_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static",'db')
# os.makedirs(DB_DIR, exist_ok=True) # klasör yoksa oluşturmaya yarar ama şimdilik ihtiyaç yok
DB_PATH = os.path.join(DB_DIR, DB_NAME)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

