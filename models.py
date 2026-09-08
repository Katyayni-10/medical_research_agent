from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(150),unique=True,nullable=False)
    password_hash=db.Column(db.String(255),nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    profile=db.relationship("Profile", backref="user", uselist=False, cascade="all,delete-orphan")
    chat_history=db.relationship("ChatHistory", backref="user", lazy=True, cascade="all,delete-orphan")
    reports = db.relationship("Report",backref="user",lazy=True,cascade="all, delete-orphan")
    scans=db.relationship("Scan", backref="user", lazy=True, cascade="all,delete-orphan")
    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

class Profile(db.Model):
    __tablename__="profiles"
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),unique=True,nullable=False)
    age=db.Column(db.Integer, nullable=True)
    gender=db.Column(db.String(30), nullable=True)

class ChatHistory(db.Model):
    __tablename__="chat_history"
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"), nullable=False)
    query=db.Column(db.Text, nullable=False)
    analysis=db.Column(db.Text, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Report(db.Model):
    __tablename__="reports"
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"), nullable=False)
    report_name=db.Column(db.String(200), nullable=True)
    analysis=db.Column(db.Text,nullable=True)
    report_date=db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    values=db.relationship("ReportValue", backref="report", lazy=True, cascade="all,delete-orphan")

class ReportValue(db.Model):
    __tablename__="report_values"
    id=db.Column(db.Integer, primary_key=True)
    report_id=db.Column(db.Integer, db.ForeignKey("reports.id"),nullable=False)
    parameter=db.Column(db.String(100),nullable=False)
    value=db.Column(db.Float, nullable=True)
    unit=db.Column(db.String(50), nullable=True)
    reference_range=db.Column(db.String(100), nullable=True)

class Scan(db.Model):
    __tablename__="scans"
    id=db.Column(db.Integer, primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"), nullable=False)
    scan_name=db.Column(db.String(200),nullable=True)
    scan_type=db.Column(db.String(100),nullable=True)
    analysis=db.Column(db.Text, nullable=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow,nullable=False)