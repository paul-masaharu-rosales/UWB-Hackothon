from flask import json, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, date
from app import app, db
from models import User, MedicalJournal, AthleticActivity, FoodAllergy, RecoveryPlan, Recommendation
from forms import LoginForm, RegistrationForm, ProfileForm, MedicalJournalForm, AthleticActivityForm, FoodAllergyForm, AnonymousSymptomForm
from ai_helper import generate_recovery_plan, generate_nutrition_plan, generate_sports_recovery_plan, generate_anonymous_recovery
from utils import create_pdf_report
from sqlalchemy import asc


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/anonymous-symptom', methods=['GET', 'POST'])
def anonymous_symptom():
    """Route for anonymous users to get recovery suggestions without creating an account"""
    name =  request.form.get('name')
    form = AnonymousSymptomForm()
    recovery_data = None

    if form.validate_on_submit():
        try:
            # Generate recovery plan using AI
            recovery_data = generate_anonymous_recovery(
                symptom=form.symptom.data,
                severity=form.severity.data,
                description=form.description.data,
                age=form.age.data,
                gender=form.gender.data)

            if not recovery_data:
                flash(
                    'Failed to generate recovery suggestions. Please try again.',
                    'danger')

        except Exception as e:
            # Display a user-friendly error message
            error_msg = str(e)
            if "quota" in error_msg.lower() or "api" in error_msg.lower():
                flash(
                    'Our AI service is temporarily unavailable. Please try again later.',
                    'warning')
            else:
                flash(f'An error occurred: {error_msg}', 'danger')

    return render_template('anonymous_symptom.html',
                           form=form,
                           recovery_data=recovery_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))

        flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    # Get recent journal entries
    recent_journals = MedicalJournal.query.filter_by(
        user_id=current_user.id).order_by(
            MedicalJournal.date_experienced.desc()).limit(5).all()

    # Get recent recovery plans
    recovery_plans = RecoveryPlan.query.filter_by(
        user_id=current_user.id).order_by(
            RecoveryPlan.created_at.desc()).limit(3).all()

    return render_template('dashboard.html',
                           recent_journals=recent_journals,
                           recovery_plans=recovery_plans)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.age = form.age.data
        current_user.gender = form.gender.data
        current_user.weight = form.weight.data
        current_user.height = form.height.data

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    # Get user's activities
    activities = AthleticActivity.query.filter_by(
        user_id=current_user.id).all()

    # Get user's allergies
    allergies = FoodAllergy.query.filter_by(user_id=current_user.id).all()

    # Activity form
    activity_form = AthleticActivityForm()

    # Allergy form
    allergy_form = FoodAllergyForm()

    return render_template('profile.html',
                           form=form,
                           activities=activities,
                           allergies=allergies,
                           activity_form=activity_form,
                           allergy_form=allergy_form)


@app.route('/add_activity', methods=['POST'])
@login_required
def add_activity():
    form = AthleticActivityForm()

    if form.validate_on_submit():
        activity = AthleticActivity(user_id=current_user.id,
                                    name=form.name.data,
                                    frequency=form.frequency.data,
                                    intensity=form.intensity.data,
                                    notes=form.notes.data)

        db.session.add(activity)
        db.session.commit()

        flash('Activity added successfully!', 'success')

    return redirect(url_for('profile'))


@app.route('/delete_activity/<int:id>', methods=['POST'])
@login_required
def delete_activity(id):
    activity = AthleticActivity.query.get_or_404(id)

    if activity.user_id != current_user.id:
        flash('You do not have permission to delete this activity.', 'danger')
        return redirect(url_for('profile'))

    db.session.delete(activity)
    db.session.commit()

    flash('Activity deleted successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/add_allergy', methods=['POST'])
@login_required
def add_allergy():
    form = FoodAllergyForm()

    if form.validate_on_submit():
        allergy = FoodAllergy(user_id=current_user.id,
                              food_item=form.food_item.data,
                              severity=form.severity.data,
                              notes=form.notes.data)

        db.session.add(allergy)
        db.session.commit()

        flash('Food allergy added successfully!', 'success')

    return redirect(url_for('profile'))


@app.route('/delete_allergy/<int:id>', methods=['POST'])
@login_required
def delete_allergy(id):
    allergy = FoodAllergy.query.get_or_404(id)

    if allergy.user_id != current_user.id:
        flash('You do not have permission to delete this allergy.', 'danger')
        return redirect(url_for('profile'))

    db.session.delete(allergy)
    db.session.commit()

    flash('Allergy deleted successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/journal', methods=['GET', 'POST'])
@login_required
def journal():
    form = MedicalJournalForm()

    if form.validate_on_submit():
        journal_entry = MedicalJournal(
            user_id=current_user.id,
            symptom=form.symptom.data,
            description=form.description.data,
            severity=form.severity.data,
            date_experienced=form.date_experienced.data)

        db.session.add(journal_entry)
        db.session.commit()

        flash('Journal entry added successfully!', 'success')
        return redirect(url_for('journal'))

    # Get all journal entries for the current user
    entries = MedicalJournal.query.filter_by(user_id=current_user.id).order_by(
        MedicalJournal.date_experienced.desc()).all()

    return render_template('journal.html', form=form, entries=entries)


@app.route('/journal/data')
@login_required
def journal_data():
    # This route will return JSON data for the chart
    entries = MedicalJournal.query.filter_by(user_id=current_user.id).order_by(
        MedicalJournal.date_experienced.asc()).all()

    data = {'labels': [], 'datasets': []}

    # Group by symptom
    symptoms = set([entry.symptom for entry in entries])
    symptom_data = {
        symptom: {
            'dates': [],
            'severities': []
        }
        for symptom in symptoms
    }

    for entry in entries:
        date_str = entry.date_experienced.strftime('%Y-%m-%d')
        symptom_data[entry.symptom]['dates'].append(date_str)
        symptom_data[entry.symptom]['severities'].append(entry.severity)

    # Prepare datasets for Chart.js
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
    color_index = 0

    for symptom, data_points in symptom_data.items():
        color = colors[color_index % len(colors)]
        color_index += 1

        dataset = {
            'label': symptom,
            'data': data_points['severities'],
            'backgroundColor': color,
            'borderColor': color,
            'borderWidth': 2,
            'fill': False,
            'tension': 0.3,
            'dates': data_points['dates']
        }

        data['datasets'].append(dataset)

        # Add dates to labels if not already there
        for date_str in data_points['dates']:
            if date_str not in data['labels']:
                data['labels'].append(date_str)

    # Sort labels (dates) chronologically
    data['labels'].sort()

    return jsonify(data)


@app.route('/journal/delete/<int:id>', methods=['POST'])
@login_required
def delete_journal(id):
    entry = MedicalJournal.query.get_or_404(id)

    if entry.user_id != current_user.id:
        flash('You do not have permission to delete this entry.', 'danger')
        return redirect(url_for('journal'))

    db.session.delete(entry)
    db.session.commit()

    flash('Journal entry deleted successfully!', 'success')
    return redirect(url_for('journal'))


@app.route('/preventative_actions')
@login_required
def preventative_actions():
    # Get the user's journal entries to analyze
    entries = MedicalJournal.query.filter_by(user_id=current_user.id).order_by(
        MedicalJournal.date_experienced.desc()).all()

    # Get existing recovery plans
    recovery_plans = RecoveryPlan.query.filter_by(
        user_id=current_user.id,
        plan_type='general').order_by(RecoveryPlan.created_at.desc()).all()

    return render_template('preventative_actions.html',
                           entries=entries,
                           recovery_plans=recovery_plans)


@app.route('/generate_recovery_plan', methods=['POST'])
@login_required
def create_recovery_plan():
    # Get selected symptom IDs from form
    symptom_ids = request.form.getlist('symptom_ids')

    if not symptom_ids:
        flash(
            'Please select at least one symptom to generate a recovery plan.',
            'warning')
        return redirect(url_for('preventative_actions'))

    # Get the selected journal entries
    selected_entries = MedicalJournal.query.filter(
        MedicalJournal.id.in_(symptom_ids),
        MedicalJournal.user_id == current_user.id).all()

    # Generate a recovery plan using AI
    plan_data = generate_recovery_plan(current_user, selected_entries)

    if plan_data:
        # Create a new recovery plan
        #model = db.Model(
        #    user_id=current_user.id,
         #   title=plan_data['title'],
          #  description=plan_data['description'],
           # plan_type='general',
            #ai_generated=True
            #)
        
        plan = RecoveryPlan(
            user_id=current_user.id,
            title=plan_data['title'],
            description=plan_data['description'],
            plan_type='general',
            ai_generated=True)

        db.session.add(plan)
        db.session.flush()  # Get the plan ID before committing

        # Add recommendations
        for rec in plan_data['recommendations']:
            recommendation = Recommendation(recovery_plan_id=plan.id,
                                            title=rec['title'],
                                            description=rec['description'],
                                            recommendation_type=rec['type'],
                                            priority=rec['priority'])
            db.session.add(recommendation)

        db.session.commit()

        flash('Recovery plan generated successfully!', 'success')
    else:
        flash('Failed to generate recovery plan. Please try again.', 'danger')

    return redirect(url_for('preventative_actions'))


@app.route('/view_plan/<int:id>')
@login_required
def view_plan(id):
    plan = RecoveryPlan.query.get_or_404(id)

    if plan.user_id != current_user.id:
        flash('You do not have permission to view this plan.', 'danger')
        return redirect(url_for('preventative_actions'))

    recommendations = Recommendation.query.filter_by(
        recovery_plan_id=plan.id
    ).order_by(asc(Recommendation.priority)).all()

    return render_template('view_plan.html',
                           plan=plan,
                           recommendations=recommendations)


@app.route('/nutrition')
@login_required
def nutrition():
    # Get the user's food allergies
    allergies = FoodAllergy.query.filter_by(user_id=current_user.id).all()

    # Get the user's recent symptoms
    recent_symptoms = MedicalJournal.query.filter_by(
        user_id=current_user.id).order_by(
            MedicalJournal.date_experienced.desc()).limit(10).all()

    # Get existing nutrition plans
    nutrition_plans = RecoveryPlan.query.filter_by(
        user_id=current_user.id,
        plan_type='nutrition').order_by(RecoveryPlan.created_at.desc()).all()

    return render_template('nutrition.html',
                           allergies=allergies,
                           recent_symptoms=recent_symptoms,
                           nutrition_plans=nutrition_plans)


@app.route('/generate_nutrition_plan', methods=['POST'])
@login_required
def create_nutrition_plan():
    # Get selected symptom IDs from form
    symptom_ids = request.form.getlist('symptom_ids')

    if not symptom_ids:
        flash(
            'Please select at least one symptom to generate a nutrition plan.',
            'warning')
        return redirect(url_for('nutrition'))

    # Get the selected journal entries
    selected_entries = MedicalJournal.query.filter(
        MedicalJournal.id.in_(symptom_ids),
        MedicalJournal.user_id == current_user.id).all()

    # Get the user's food allergies
    allergies = FoodAllergy.query.filter_by(user_id=current_user.id).all()

    # Generate a nutrition plan using AI
    plan_data = generate_nutrition_plan(current_user, selected_entries,
                                        allergies)

    if plan_data:
        # Create a new nutrition plan
        plan = RecoveryPlan(user_id=current_user.id,
                            title=plan_data['title'],
                            description=plan_data['description'],
                            plan_type='nutrition',
                            ai_generated=True)

        db.session.add(plan)
        db.session.flush()  # Get the plan ID before committing

        # Add recommendations
        for rec in plan_data['recommendations']:
            recommendation = Recommendation(recovery_plan_id=plan.id,
                                            title=rec['title'],
                                            description=rec['description'],
                                            recommendation_type='nutrition',
                                            priority=rec['priority'])
            db.session.add(recommendation)

        db.session.commit()

        flash('Nutrition plan generated successfully!', 'success')
    else:
        flash('Failed to generate nutrition plan. Please try again.', 'danger')

    return redirect(url_for('nutrition'))


@app.route('/sports_recovery')
@login_required
def sports_recovery():
    # Get the user's athletic activities
    activities = AthleticActivity.query.filter_by(
        user_id=current_user.id).all()

    # Get the user's recent symptoms
    recent_symptoms = MedicalJournal.query.filter_by(
        user_id=current_user.id).order_by(
            MedicalJournal.date_experienced.desc()).limit(10).all()

    # Get existing sports recovery plans
    sports_plans = RecoveryPlan.query.filter_by(
        user_id=current_user.id,
        plan_type='sports').order_by(RecoveryPlan.created_at.desc()).all()

    return render_template('sports_recovery.html',
                           activities=activities,
                           recent_symptoms=recent_symptoms,
                           sports_plans=sports_plans)


@app.route('/generate_sports_plan', methods=['POST'])
@login_required
def create_sports_plan():
    # Get selected symptom IDs and activity IDs from form
    symptom_ids = request.form.getlist('symptom_ids')
    activity_ids = request.form.getlist('activity_ids')

    if not symptom_ids:
        flash(
            'Please select at least one symptom to generate a sports recovery plan.',
            'warning')
        return redirect(url_for('sports_recovery'))

    if not activity_ids:
        flash(
            'Please select at least one athletic activity to generate a sports recovery plan.',
            'warning')
        return redirect(url_for('sports_recovery'))

    # Get the selected journal entries
    selected_entries = MedicalJournal.query.filter(
        MedicalJournal.id.in_(symptom_ids),
        MedicalJournal.user_id == current_user.id).all()

    # Get the selected activities
    selected_activities = AthleticActivity.query.filter(
        AthleticActivity.id.in_(activity_ids),
        AthleticActivity.user_id == current_user.id).all()

    # Generate a sports recovery plan using AI
    plan_data = generate_sports_recovery_plan(current_user, selected_entries,
                                              selected_activities)

    if plan_data:
        # Create a new sports recovery plan
        plan = RecoveryPlan(user_id=current_user.id,
                            title=plan_data['title'],
                            description=plan_data['description'],
                            plan_type='sports',
                            ai_generated=True)

        db.session.add(plan)
        db.session.flush()  # Get the plan ID before committing

        # Add recommendations
        for rec in plan_data['recommendations']:
            recommendation = Recommendation(recovery_plan_id=plan.id,
                                            title=rec['title'],
                                            description=rec['description'],
                                            recommendation_type='sports',
                                            priority=rec['priority'])
            db.session.add(recommendation)

        db.session.commit()

        flash('Sports recovery plan generated successfully!', 'success')
    else:
        flash('Failed to generate sports recovery plan. Please try again.',
              'danger')

    return redirect(url_for('sports_recovery'))


@app.route('/reports')
@login_required
def reports():
    # Get all journal entries
    entries = MedicalJournal.query.filter_by(user_id=current_user.id).order_by(
        MedicalJournal.date_experienced.desc()).all()

    # Get all recovery plans
    plans = RecoveryPlan.query.filter_by(user_id=current_user.id).order_by(
        RecoveryPlan.created_at.desc()).all()

    return render_template('reports.html', entries=entries, plans=plans)

@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    try:
        # Get selected journal IDs and plan IDs
        journal_ids = request.form.getlist('journal_ids')
        plan_ids = request.form.getlist('plan_ids')
        report_title = request.form.get('report_title', 'Medical Report')

        if not journal_ids and not plan_ids:
            # Return a JSON response with an error message if no journals or plans are selected
            return jsonify({
                'success': False,
                'message': 'Please select at least one journal entry or recovery plan for the report.'
            })

        # Get selected journal entries
        selected_journals = MedicalJournal.query.filter(
            MedicalJournal.id.in_(journal_ids),
            MedicalJournal.user_id == current_user.id).order_by(
                MedicalJournal.date_experienced.desc()).all()

        # Get selected plans with their recommendations
        selected_plans = []
        if plan_ids:
            plans = RecoveryPlan.query.filter(
                RecoveryPlan.id.in_(plan_ids),
                RecoveryPlan.user_id == current_user.id).all()

            for plan in plans:
                recommendations = Recommendation.query.filter_by(
                    recovery_plan_id=plan.id).order_by(
                        Recommendation.priority.asc()).all()
                
                plan_data = {
                    'plan': plan,
                    'recommendations': recommendations
                }
                selected_plans.append(plan_data)

        # Store report data in session for client-side PDF generation
        # Store IDs instead of actual objects to avoid serialization issues
        report_data = {
            'title': report_title,
            'journal_ids': [j.id for j in selected_journals],
            'plan_ids': [p['plan'].id for p in selected_plans],
            'generated_date': datetime.now().strftime('%Y-%m-%d')
        }

        # Store the data in session
        session['report_data'] = report_data

        return jsonify({
            'success': True,
            'message': 'Report data prepared successfully!'
        })
    except Exception as e:
        app.logger.error(f"Error preparing report: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error preparing report: {str(e)}'
        })


@app.route('/get_report_data')
@login_required
def get_report_data():
    try:
        report_data = session.get('report_data')

        if not report_data:
            return jsonify({'success': False, 'message': 'No report data found!'})

        # Fetch journal entries from database using stored IDs
        journals = []
        if 'journal_ids' in report_data and report_data['journal_ids']:
            journals = MedicalJournal.query.filter(
                MedicalJournal.id.in_(report_data['journal_ids']),
                MedicalJournal.user_id == current_user.id
            ).all()

        # Fetch plans and recommendations from database using stored IDs
        plans_data = []
        if 'plan_ids' in report_data and report_data['plan_ids']:
            plans = RecoveryPlan.query.filter(
                RecoveryPlan.id.in_(report_data['plan_ids']),
                RecoveryPlan.user_id == current_user.id
            ).all()
            
            for plan in plans:
                recommendations = Recommendation.query.filter_by(
                    recovery_plan_id=plan.id
                ).order_by(Recommendation.priority.asc()).all()
                
                plans_data.append({
                    'plan': plan,
                    'recommendations': recommendations
                })

        # Convert data to JSON-serializable format
        processed_data = {
            'success': True,
            'title': report_data['title'],
            'user': {
                'first_name': current_user.first_name,
                'last_name': current_user.last_name,
                'email': current_user.email,
                'age': current_user.age,
                'gender': current_user.gender,
                'weight': current_user.weight,
                'height': current_user.height,
                'bmi': current_user.calculate_bmi()
            },
            'journals': [journal.serialize() for journal in journals],
            'plans': [],
            'generated_date': report_data['generated_date']
        }

        # Process plan data
        for plan_data in plans_data:
            plan = {
                'id': plan_data['plan'].id,
                'title': plan_data['plan'].title,
                'description': plan_data['plan'].description,
                'plan_type': plan_data['plan'].plan_type,
                'created_at': plan_data['plan'].created_at.strftime('%Y-%m-%d'),
                'recommendations': []
            }

            for rec in plan_data['recommendations']:
                plan['recommendations'].append({
                    'title': rec.title,
                    'description': rec.description,
                    'type': rec.recommendation_type,
                    'priority': rec.priority
                })

            processed_data['plans'].append(plan)

        # Clear session data
        session.pop('report_data', None)

        return jsonify(processed_data)
    except Exception as e:
        # Log the error
        app.logger.error(f"Error generating report data: {str(e)}")
        # Return a proper JSON response even in case of errors
        return jsonify({'success': False, 'message': f"Error generating report: {str(e)}"})
