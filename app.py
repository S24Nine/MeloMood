import os
import csv
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "melomood-secret-key-2025")

# Questions for mood detection
questions = [
    {
        "id": "physical",
        "text": "How are you feeling physically right now?",
        "options": ["Energetic", "Tired", "Sick", "Restless", "Calm"]
    },
    {
        "id": "vibe",
        "text": "What's the overall vibe of your day?",
        "options": ["Peaceful", "Hectic", "Lazy", "Productive", "Chaotic"]
    },
    {
        "id": "social",
        "text": "How social do you feel?",
        "options": ["Talkative", "Avoiding people", "Lonely", "Neutral"]
    },
    {
        "id": "control",
        "text": "Do you feel in control today?",
        "options": ["Yes, totally", "Not at all", "Somewhat", "IDK"]
    },
    {
        "id": "emotion",
        "text": "Pick the feeling that best describes you right now:",
        "options": ["Happy", "Anxious", "Heartbroken", "Motivated", "Overwhelmed"]
    },
    {
        "id": "focus",
        "text": "How focused do you feel?",
        "options": ["Laser sharp", "Distracted", "Bored", "All over the place"]
    },
    {
        "id": "inspiration",
        "text": "Are you feeling inspired?",
        "options": ["Yes!", "A little", "Not at all", "Lost", "Hopeless"]
    },
    {
        "id": "stress",
        "text": "What's your stress level? (1-10)",
        "options": [str(i) for i in range(1, 11)]
    },
    {
        "id": "connection",
        "text": "How connected do you feel to others today?",
        "options": ["Loved", "Alone", "Appreciated", "Isolated"]
    },
    {
        "id": "pace",
        "text": "How fast is your day moving?",
        "options": ["Super fast", "Slow", "Average", "Feels frozen in time"]
    },
    {
        "id": "confidence",
        "text": "How confident do you feel?",
        "options": ["Super confident", "Insecure", "Trying my best", "Neutral"]
    },
    {
        "id": "weather",
        "text": "Pick your ideal weather right now:",
        "options": ["Sunny", "Cloudy", "Rainy", "Snowy", "Stormy"]
    },
    {
        "id": "energy",
        "text": "How would you describe your energy?",
        "options": ["Hype", "Calm", "Neutral", "Drained"]
    },
    {
        "id": "creativity",
        "text": "How creative do you feel today?",
        "options": ["Bursting with ideas", "Blank canvas", "A little spark", "Zero inspiration"]
    },
    {
        "id": "gratitude",
        "text": "Do you feel grateful right now?",
        "options": ["Yes, very", "A bit", "Not really", "Can't say"]
    }
]

# Mood mapping for scoring
mood_weights = {
    # Physical
    "Energetic": 2, "Tired": -1, "Sick": -2, "Restless": -1, "Calm": 1,
    
    # Vibe
    "Peaceful": 2, "Hectic": -1, "Lazy": 0, "Productive": 2, "Chaotic": -2,
    
    # Social
    "Talkative": 1, "Avoiding people": -1, "Lonely": -2, "Neutral": 0,
    
    # Control
    "Yes, totally": 2, "Not at all": -2, "Somewhat": 0, "IDK": -1,
    
    # Emotion
    "Happy": 2, "Anxious": -1, "Heartbroken": -3, "Motivated": 2, "Overwhelmed": -2,
    
    # Focus
    "Laser sharp": 2, "Distracted": -1, "Bored": -1, "All over the place": -2,
    
    # Inspiration
    "Yes!": 2, "A little": 1, "Not at all": -1, "Lost": -2, "Hopeless": -3,
    
    # Connection
    "Loved": 2, "Alone": -2, "Appreciated": 1, "Isolated": -2,
    
    # Pace
    "Super fast": 0, "Slow": -1, "Average": 0, "Feels frozen in time": -2,
    
    # Confidence
    "Super confident": 2, "Insecure": -2, "Trying my best": 1, "Neutral": 0,
    
    # Weather
    "Sunny": 1, "Cloudy": 0, "Rainy": -1, "Snowy": 0, "Stormy": -1,
    
    # Energy
    "Hype": 2, "Calm": 1, "Neutral": 0, "Drained": -2,
    
    # Creativity
    "Bursting with ideas": 2, "Blank canvas": -1, "A little spark": 1, "Zero inspiration": -2,
    
    # Gratitude
    "Yes, very": 2, "A bit": 1, "Not really": -1, "Can't say": 0
}

# Stress mapping (1-10 scale)
for i in range(1, 11):
    if i <= 3:
        mood_weights[str(i)] = 2  # Low stress = positive
    elif i <= 5:
        mood_weights[str(i)] = 0  # Medium stress = neutral
    elif i <= 7:
        mood_weights[str(i)] = -1  # High stress = negative
    else:
        mood_weights[str(i)] = -2  # Very high stress = very negative

def determine_mood(score):
    """Determine mood based on total score"""
    if score >= 3:
        return "excited"
    elif score >= 1:
        return "happy"
    elif score >= 0:
        return "peaceful"
    elif score >= -2:
        return "anxious"
    elif score >= -4:
        return "sad"
    elif score >= -6:
        return "frustrated"
    else:
        return "hopeless"

def load_users():
    """Load users from CSV file"""
    try:
        return pd.read_csv('users.csv')
    except FileNotFoundError:
        # Create empty users file if it doesn't exist
        df = pd.DataFrame({'email': [], 'password_hash': []})
        df.to_csv('users.csv', index=False)
        return df

def save_user(email, password):
    """Save new user to CSV"""
    users_df = load_users()
    password_hash = generate_password_hash(password)
    new_user = pd.DataFrame({'email': [email], 'password_hash': [password_hash]})
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    users_df.to_csv('users.csv', index=False)

def verify_user(email, password):
    """Verify user credentials"""
    users_df = load_users()
    user_row = users_df[users_df['email'] == email]
    if not user_row.empty:
        stored_hash = user_row.iloc[0]['password_hash']
        return check_password_hash(stored_hash, password)
    return False

def log_mood(email, mood):
    """Log mood to CSV file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if mood_log.csv exists, if not create it
    try:
        mood_df = pd.read_csv('mood_log.csv')
    except FileNotFoundError:
        mood_df = pd.DataFrame({'user': [], 'timestamp': [], 'mood': []})
    
    new_log = pd.DataFrame({
        'user': [email],
        'timestamp': [timestamp],
        'mood': [mood]
    })
    
    mood_df = pd.concat([mood_df, new_log], ignore_index=True)
    mood_df.to_csv('mood_log.csv', index=False)

def get_playlist_for_mood(mood):
    """Get Spotify playlist for detected mood"""
    try:
        songs_df = pd.read_csv('songs.csv')
        mood_playlists = songs_df[songs_df['mood'] == mood]
        if not mood_playlists.empty:
            return mood_playlists.iloc[0].to_dict()
        else:
            # Return a default playlist if mood not found
            return {
                'mood': mood,
                'link': 'https://open.spotify.com/playlist/default',
                'cover': '/static/default_cover.svg'
            }
    except FileNotFoundError:
        return {
            'mood': mood,
            'link': 'https://open.spotify.com/playlist/default',
            'cover': '/static/default_cover.svg'
        }

@app.route('/')
def welcome():
    """Welcome page"""
    logged_in = 'user_email' in session
    return render_template('welcome.html', logged_in=logged_in)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if verify_user(email, password):
            session['user_email'] = email
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        users_df = load_users()
        if email in users_df['email'].values:
            return render_template('signup.html', error="Email already exists")
        
        save_user(email, password)
        session['user_email'] = email
        return redirect(url_for('chat'))
    
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user_email', None)
    session.pop('current_question', None)
    session.pop('answers', None)
    session.pop('mood_score', None)
    return redirect(url_for('welcome'))

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat interface for mood detection"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    # Reset chat session if POST request
    if request.method == 'POST':
        session.pop('current_question', None)
        session.pop('answers', None)
        session.pop('mood_score', None)
        session.pop('detected_mood', None)
        session.pop('playlist', None)
        session.pop('meme_image', None)
        session.pop('final_score', None)
    
    # Initialize chat session
    if 'current_question' not in session:
        session['current_question'] = 0
        session['answers'] = {}
        session['mood_score'] = 0
    
    return render_template('chat.html', 
                         questions=questions,
                         current_question=session.get('current_question', 0))

@app.route('/next', methods=['POST'])
def next_question():
    """Process answer and move to next question"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    current_q = session.get('current_question', 0)
    answer = request.form.get('answer')
    
    if current_q < len(questions):
        # Store answer and update score
        question_id = questions[current_q]['id']
        session['answers'][question_id] = answer
        
        # Add to mood score
        weight = mood_weights.get(answer or '', 0)
        session['mood_score'] = session.get('mood_score', 0) + weight
        
        # Move to next question
        session['current_question'] = current_q + 1
        
        # Check if we've finished all questions
        if session['current_question'] >= len(questions):
            # Determine final mood
            final_score = session['mood_score']
            detected_mood = determine_mood(final_score)
            
            # Log the mood
            log_mood(session['user_email'], detected_mood)
            
            # Get playlist and meme
            playlist = get_playlist_for_mood(detected_mood)
            meme_image = f"/static/{detected_mood}.svg"
            
            # Store results in session for display
            session['detected_mood'] = detected_mood
            session['playlist'] = playlist
            session['meme_image'] = meme_image
            session['final_score'] = final_score
    
    return redirect(url_for('chat'))

@app.route('/mood-graph')
def mood_graph():
    """Mood analytics page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    return render_template('mood_graph.html')

@app.route('/mood-data')
def mood_data():
    """Return mood data as JSON for charts"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        mood_df = pd.read_csv('mood_log.csv')
        user_moods = mood_df[mood_df['user'] == session['user_email']]
        
        if user_moods.empty:
            return jsonify({
                'weekly': {},
                'monthly': {},
                'yearly': {}
            })
        
        # Convert to format needed for Chart.js
        user_moods = user_moods.copy()
        user_moods['timestamp'] = pd.to_datetime(user_moods['timestamp'])
        user_moods = user_moods.sort_values('timestamp')
        
        # Weekly data (last 7 days with day names)
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        weekly_moods = user_moods[user_moods['timestamp'] >= week_ago]
        weekly_data = {}
        for _, row in weekly_moods.iterrows():
            day_name = row['timestamp'].strftime('%a %m/%d')  # Mon 03/15
            if day_name not in weekly_data:
                weekly_data[day_name] = {}
            mood = row['mood']
            weekly_data[day_name][mood] = weekly_data[day_name].get(mood, 0) + 1
        
        # Flatten weekly data for chart
        weekly_chart_data = {}
        for day, moods in weekly_data.items():
            for mood, count in moods.items():
                if mood not in weekly_chart_data:
                    weekly_chart_data[mood] = 0
                weekly_chart_data[mood] += count
        
        # Monthly data (last 4 weeks with week names)
        month_ago = now - timedelta(days=30)
        monthly_moods = user_moods[user_moods['timestamp'] >= month_ago]
        monthly_data = {}
        for _, row in monthly_moods.iterrows():
            week_start = row['timestamp'] - timedelta(days=row['timestamp'].weekday())
            week_name = f"Week of {week_start.strftime('%m/%d')}"
            if week_name not in monthly_data:
                monthly_data[week_name] = {}
            mood = row['mood']
            monthly_data[week_name][mood] = monthly_data[week_name].get(mood, 0) + 1
        
        # Flatten monthly data for chart
        monthly_chart_data = {}
        for week, moods in monthly_data.items():
            for mood, count in moods.items():
                if mood not in monthly_chart_data:
                    monthly_chart_data[mood] = 0
                monthly_chart_data[mood] += count
        
        # Yearly data (by month names)
        year_ago = now - timedelta(days=365)
        yearly_moods = user_moods[user_moods['timestamp'] >= year_ago]
        yearly_data = {}
        for _, row in yearly_moods.iterrows():
            month_name = row['timestamp'].strftime('%B %Y')  # January 2024
            if month_name not in yearly_data:
                yearly_data[month_name] = {}
            mood = row['mood']
            yearly_data[month_name][mood] = yearly_data[month_name].get(mood, 0) + 1
        
        # Flatten yearly data for chart
        yearly_chart_data = {}
        for month, moods in yearly_data.items():
            for mood, count in moods.items():
                if mood not in yearly_chart_data:
                    yearly_chart_data[mood] = 0
                yearly_chart_data[mood] += count
        
        return jsonify({
            'weekly': weekly_chart_data,
            'monthly': monthly_chart_data,
            'yearly': yearly_chart_data
        })
        
    except FileNotFoundError:
        return jsonify({
            'weekly': {},
            'monthly': {},
            'yearly': {}
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
