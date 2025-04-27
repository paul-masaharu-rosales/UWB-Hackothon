from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, FloatField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange
from datetime import date

class AnonymousSymptomForm(FlaskForm):
    symptom = StringField('Symptom', validators=[DataRequired(), Length(max=100)])
    severity = IntegerField('Severity (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    age = IntegerField('Age (Optional)', validators=[Optional(), NumberRange(min=1, max=120)])
    gender = SelectField('Gender (Optional)', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[Optional()])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[Optional(), Length(max=64)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=64)])
    age = IntegerField('Age', validators=[Optional(), NumberRange(min=1, max=120)])
    gender = SelectField('Gender', choices=[
        ('', 'Select Gender'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[Optional()])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=10, max=500)])
    height = FloatField('Height (cm)', validators=[Optional(), NumberRange(min=50, max=300)])

class MedicalJournalForm(FlaskForm):
    symptom = StringField('Symptom', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    severity = IntegerField('Severity (1-10)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    date_experienced = DateField('Date Experienced', validators=[DataRequired()], default=date.today)

class AthleticActivityForm(FlaskForm):
    name = StringField('Activity Name', validators=[DataRequired(), Length(max=100)])
    frequency = StringField('Frequency (e.g., "3 times a week")', validators=[Optional(), Length(max=50)])
    intensity = SelectField('Intensity', choices=[
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])

class FoodAllergyForm(FlaskForm):
    food_item = StringField('Food Item', validators=[DataRequired(), Length(max=100)])
    severity = SelectField('Severity', choices=[
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
