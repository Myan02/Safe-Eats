from flask import Flask
from app.data import Inspections

inspection_data = Inspections()
app = Flask(__name__)

from app import routes



