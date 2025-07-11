# VoteNow - Real-Time Live Polling App

A full-stack real-time polling application built with Flask, Socket.IO, and Firebase Firestore.



## Features

- ✅ Real-time live polling with WebSocket updates
- ✅ Create polls with custom questions and multiple options
- ✅ One vote per user (prevents duplicate voting)
- ✅ Beautiful live-updating charts (bar and pie charts)
- ✅ Responsive design with Tailwind CSS
- ✅ Firebase Firestore for data persistence
- ✅ Modern glassmorphism UI design



## Technology Stack

- **Frontend**: HTML, CSS, Tailwind CSS, JavaScript, Chart.js
- **Backend**: Python Flask with Flask-SocketIO
- **Database**: Firebase Firestore (NoSQL)
- **Real-time**: WebSockets (Socket.IO)


## Project Structure

```
votenow/
├── app.py                 # Flask backend with SocketIO
├── firestore_service.py   # Firebase Firestore integration
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html        # Create/view poll landing page
│   ├── vote.html         # Voting interface
│   ├── results.html      # Real-time results with charts
│   └── error.html        # Error page
└── README.md             # This file


```

## Setup Instructions



### 1. Prerequisites


- Python 3.8+
- Firebase project with Firestore enabled
- Firebase service account key (JSON file)



### 2. Firebase Setup


1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing project
3. Enable Firestore Database
4. Go to Project Settings → Service Accounts
5. Generate a new private key (JSON file)
6. Download the JSON file and save it as `serviceAccountKey.json` in the project root


### 3. Installation


```bash
# Clone or create the project directory
mkdir votenow
cd votenow

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```


### 4. Configuration


1. Update `firestore_service.py` with your Firebase service account key path:
```python
# Replace this line:
cred = credentials.Certificate('path/to/your/serviceAccountKey.json')
# With the actual path to your service account key file
```

2. Update the Flask secret key in `app.py`:
```python
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Replace with a secure secret key
```


### 5. Run the Application


```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Creating a Poll

1. Go to the home page (`/`)
2. Enter your poll question
3. Add at least 2 options (you can add up to 10)
4. Click "Create Poll"
5. Share the voting and results links with your audience

### Voting

1. Users visit the voting link
2. Select their preferred option
3. Submit their vote
4. Each user can only vote once per poll

### Viewing Results

1. Visit the results link to see live updates
2. Results include:
   - Total vote count
   - Interactive bar chart
   - Pie chart showing distribution
   - Detailed breakdown with percentages
   - Real-time updates as votes come in

## API Endpoints

- `GET /` - Landing page for creating polls
- `POST /create_poll` - Create a new poll
- `GET /vote/<poll_id>` - Voting page for a specific poll
- `GET /results/<poll_id>` - Results page with live charts
- `POST /cast_vote` - Submit a vote
- `GET /get_poll/<poll_id>` - Get poll data (JSON)

## WebSocket Events

- `join_poll` - Join a poll room for real-time updates
- `leave_poll` - Leave a poll room
- `vote_update` - Real-time vote count updates

## Database Structure

### Polls Collection
```json
{
  "id": "poll_uuid",
  "question": "What's your favorite programming language?",
  "options": ["Python", "JavaScript", "Java", "C++"],
  "votes": {
    "Python": 5,
    "JavaScript": 3,
    "Java": 2,
    "C++": 1
  },
  "created_at": "2024-01-01T12:00:00",
  "active": true
}
```

### Votes Collection
```json
{
  "user_id": "user_uuid",
  "poll_id": "poll_uuid",
  "option": "Python",
  "timestamp": "2024-01-01T12:05:00"
}
```

## Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 app:app
```

### Environment Variables for Production

Set these environment variables:
- `FLASK_ENV=production`
- `SECRET_KEY=your-secure-secret-key`
- Firebase credentials via environment variables or service account

## Security Features

- Session-based user identification
- Duplicate vote prevention
- Input validation and sanitization
- CORS protection with Flask-SocketIO
- Secure Firebase authentication

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the Firebase console for database connectivity
2. Verify all dependencies are installed
3. Ensure WebSocket connections are working
4. Check browser console for JavaScript errors

## Future Enhancements

- [ ] User authentication and poll management
- [ ] Poll expiration and scheduling
- [ ] Multiple poll types (single choice, multiple choice, ranking)
- [ ] Export results to CSV/PDF
- [ ] Admin dashboard for poll management
- [ ] Custom themes and branding
- [ ] Poll analytics and insights#   R e a l - T i m e - D a t a - S y n c - T o o l - F i r e s t o r e - W e b S o c k e t s - 
 
 #   R e a l - T i m e - D a t a - S y n c - T o o l - F i r e s t o r e - W e b S o c k e t s - 
 
 #   R e a l - T i m e - D a t a - S y n c - T o o l - F i r e s t o r e - W e b S o c k e t s - 
 
 
