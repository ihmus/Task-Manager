from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

#Note employes
class Note(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    data= db.Column(db.String(30000))
    date= db.Column(db.DateTime(timezone=True),default=func.now())
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
#User employes
class User(db.Model,UserMixin):
    id= db.Column(db.Integer, primary_key=True)
    password= db.Column(db.String(150))
    gmail= db.Column(db.String(75),unique=True)
    username=db.Column(db.String(150))
    lastname=db.Column(db.String(150))
    name=db.Column(db.String(150))
    notes= db.relationship('Note')