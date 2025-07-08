from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import json
from datetime import datetime
from firestore_service import FirestoreService
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Firestore service
db_service = FirestoreService()

# --- Admin static credentials ---
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'  # In production, use env vars or config

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/customer_register', methods=['GET', 'POST'])
def customer_register():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            flash('Email and password required', 'danger')
            return render_template('customer_register.html')
        # Check if user exists
        if db_service.get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('customer_register.html')
        # Store user
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': 'customer',
            'created_at': datetime.now().isoformat()
        }
        db_service.create_user(user_id, user_data)
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('customer_login'))
    return render_template('customer_register.html')

@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')
        user = db_service.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['role'] = 'customer'
            session['email'] = user['email']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('list_polls'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('customer_login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['role'] = 'admin'
            session['admin'] = True
            flash('Admin logged in.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    polls = db_service.get_all_polls()
    return render_template('admin_dashboard.html', polls=polls)

@app.route('/create_poll', methods=['GET', 'POST'])
def create_poll():
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        question = request.form.get('question')
        options = request.form.getlist('options')
        options = [opt for opt in options if opt.strip()]
        active = True if request.form.get('active') == 'on' else False
        if not question or len(options) < 2:
            flash('Question and at least 2 options are required', 'danger')
            return render_template('create_poll.html')
        poll_id = str(uuid.uuid4())
        poll_data = {
            'id': poll_id,
            'question': question,
            'options': options,
            'votes': {option: 0 for option in options},
            'created_at': datetime.now().isoformat(),
            'active': active
        }
        db_service.create_poll(poll_id, poll_data)
        flash('Poll created successfully.', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('create_poll.html')

@app.route('/toggle_poll_status/<poll_id>', methods=['POST'])
def toggle_poll_status(poll_id):
    if session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    poll = db_service.get_poll(poll_id)
    if poll:
        db_service.update_poll_status(poll_id, not poll.get('active', True))
        flash('Poll status updated.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/polls')
def list_polls():
    if session.get('role') != 'customer':
        return redirect(url_for('customer_login'))
    polls = [p for p in db_service.get_all_polls() if p.get('active', True)]
    return render_template('polls.html', polls=polls)

@app.route('/vote/<poll_id>', methods=['GET', 'POST'])
def vote_page(poll_id):
    if session.get('role') != 'customer':
        return redirect(url_for('customer_login'))
    poll_data = db_service.get_poll(poll_id)
    if not poll_data:
        return render_template('error.html', message='Poll not found'), 404
    if not poll_data.get('active', True):
        return render_template('vote.html', poll=poll_data, has_voted=False, poll_closed=True)
    user_id = session['user_id']
    has_voted = db_service.has_user_voted(poll_id, user_id)
    if request.method == 'POST' and not has_voted:
        selected_option = request.form.get('option')
        if has_voted:
            flash('You have already voted in this poll.', 'danger')
        elif selected_option:
            success = db_service.cast_vote(poll_id, selected_option, user_id)
            if success:
                flash('Vote cast successfully.', 'success')
                # Real-time update
                poll_data = db_service.get_poll(poll_id)
                socketio.emit('vote_update', {
                    'poll_id': poll_id,
                    'votes': poll_data['votes'],
                    'total_votes': sum(poll_data['votes'].values())
                }, room=f'poll_{poll_id}')
                return redirect(url_for('results_page', poll_id=poll_id))
            else:
                flash('Failed to cast vote.', 'danger')
        else:
            flash('Please select an option.', 'danger')
    return render_template('vote.html', poll=poll_data, has_voted=has_voted, poll_closed=False)

@app.route('/results/<poll_id>')
def results_page(poll_id):
    try:
        poll_data = db_service.get_poll(poll_id)
        if not poll_data:
            return render_template('error.html', message='Poll not found'), 404
        return render_template('results.html', poll=poll_data)
    except Exception as e:
        return render_template('error.html', message=str(e)), 500

@app.route('/get_poll/<poll_id>')
def get_poll(poll_id):
    try:
        poll_data = db_service.get_poll(poll_id)
        if not poll_data:
            return jsonify({'error': 'Poll not found'}), 404
        return jsonify(poll_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile')
def profile():
    if session.get('role') != 'customer':
        return redirect(url_for('customer_login'))
    user_id = session['user_id']
    votes = db_service.get_user_votes(user_id)
    # Get poll details for each vote
    poll_map = {}
    for vote in votes:
        poll_id = vote.get('poll_id')
        if poll_id and poll_id not in poll_map:
            poll_map[poll_id] = db_service.get_poll(poll_id)
    return render_template('profile.html', votes=votes, poll_map=poll_map)

# WebSocket events
@socketio.on('join_poll')
def on_join_poll(data):
    poll_id = data['poll_id']
    join_room(f'poll_{poll_id}')
    emit('joined_poll', {'poll_id': poll_id})

@socketio.on('leave_poll')
def on_leave_poll(data):
    poll_id = data['poll_id']
    leave_room(f'poll_{poll_id}')
    emit('left_poll', {'poll_id': poll_id})

@socketio.on('connect')
def on_connect():
    print('Client connected')

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message='Page not found (404).'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', message='Internal server error (500).'), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)