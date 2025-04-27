from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    weight = db.Column(db.Float)  # in kg
    height = db.Column(db.Float)  # in cm
    
    # Relationships
    journals = db.relationship('MedicalJournal', backref='user', lazy=True, cascade="all, delete-orphan")
    activities = db.relationship('AthleticActivity', backref='user', lazy=True, cascade="all, delete-orphan")
    allergies = db.relationship('FoodAllergy', backref='user', lazy=True, cascade="all, delete-orphan")
    recovery_plans = db.relationship('RecoveryPlan', backref='user', lazy=True, cascade="all, delete-orphan")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def calculate_bmi(self):
        if self.height and self.weight:
            # BMI formula: weight(kg) / height(m)^2
            height_in_meters = self.height / 100
            return round(self.weight / (height_in_meters * height_in_meters), 2)
        return None


class MedicalJournal(db.Model):
    __tablename__ = 'medical_journals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symptom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.Integer, nullable=False)  # 1-10 scale
    date_experienced = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def serialize(self):
        return {
            'id': self.id,
            'symptom': self.symptom,
            'description': self.description,
            'severity': self.severity,
            'date_experienced': self.date_experienced.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


class AthleticActivity(db.Model):
    __tablename__ = 'athletic_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(50))  # e.g., "3 times a week"
    intensity = db.Column(db.String(50))  # e.g., "high", "moderate", "low"
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FoodAllergy(db.Model):
    __tablename__ = 'food_allergies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_item = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(50))  # e.g., "mild", "moderate", "severe"
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RecoveryPlan(db.Model):
    __tablename__ = 'recovery_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    plan_type = db.Column(db.String(50))  # e.g., "general", "sports", "nutrition"
    ai_generated = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recommendations = db.relationship('Recommendation', backref='recovery_plan', lazy=True, cascade="all, delete-orphan")
    def __init__(
        self,
        user_id: int,
        title: str,
        description: str = "",
        plan_type: str = "general",
        ai_generated: bool = True,
    ) -> None:
        self.user_id = user_id
        self.title = title
        self.description = description
        self.plan_type = plan_type
        self.ai_generated = ai_generated


class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    recovery_plan_id = db.Column(db.Integer, db.ForeignKey('recovery_plans.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    recommendation_type = db.Column(db.String(50))  # e.g., "exercise", "nutrition", "lifestyle"
    priority = db.Column(db.Integer)  # 1 = highest priority
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def __init__(
        self,
        recovery_plan_id: int,
        title: str,
        description: str = "",
        recommendation_type: str = "",
        priority: int = 1,
    ) -> None:
        self.recovery_plan_id = recovery_plan_id
        self.title = title
        self.description = description
        self.recommendation_type = recommendation_type
        self.priority = priority
