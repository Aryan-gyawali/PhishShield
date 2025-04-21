import json
import mysql.connector
from django.shortcuts import render, redirect
from django.http import JsonResponse
import random

# Database connection helper
def get_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='routes'  # Use the 'routes' database directly
    )
    return conn

# Database initialization to create routes database and tables if they do not exist
def init_db():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=''
    )
    cursor = conn.cursor()

    # Check if the 'routes' database exists, if not, create it
    cursor.execute("CREATE DATABASE IF NOT EXISTS routes")
    conn.database = 'routes'

    # Create users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            points INT DEFAULT 0,
            level INT DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create user_attempts table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            scenario_id INT,
            was_correct BOOLEAN,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (scenario_id) REFERENCES phishing_scenarios(id)
        )
    """)

    # Create phishing_scenarios table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phishing_scenarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            url VARCHAR(255) NOT NULL,
            is_real BOOLEAN NOT NULL,
            difficulty INT DEFAULT 1
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# Initialize the database when the server starts
init_db()

# Helper function to check authentication
def is_authenticated(request):
    return 'user' in request.session

# Auth Views
def register(request):
    # Redirect to dashboard if already logged in
    if is_authenticated(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if username exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return render(request, 'auth/register.html', {'error': 'Username already exists'})
            
            # Insert new user with 0 points
            cursor.execute(
                "INSERT INTO users (username, password, points) VALUES (%s, %s, 0)",
                (username, password)
            )
            conn.commit()
            
            # Log the user in immediately after registration
            cursor.execute(
                "SELECT id, username, points FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()
            request.session['user'] = user
            return redirect('dashboard')
            
        except Exception as e:
            return render(request, 'auth/register.html', {'error': str(e)})
        finally:
            if 'conn' in locals():
                conn.close()
    
    return render(request, 'auth/register.html')

def login(request):
    # Redirect to dashboard if already logged in
    if is_authenticated(request):
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, points FROM users WHERE username = %s AND password = %s",
                (username, password)
            )
            user = cursor.fetchone()
            
            if user:
                request.session['user'] = user
                return redirect('dashboard')
            else:
                return render(request, 'auth/login.html', {'error': 'Invalid username or password'})
        except Exception as e:
            return render(request, 'auth/login.html', {'error': str(e)})
        finally:
            if 'conn' in locals():
                conn.close()
    
    return render(request, 'auth/login.html')

def logout(request):
    if 'user' in request.session:
        del request.session['user']
    return redirect('login')

def dashboard(request):
    # Check if the user is authenticated
    if not is_authenticated(request):
        # Redirect to login if not authenticated
        return redirect('login')
    
    # If authenticated, render the dashboard with the user info
    return render(request, 'dashboard.html', {
        'user': request.session['user']  # Pass user info to the template
    })

def test(request):
    if not is_authenticated(request):
        return redirect('login')
    
    # List of tests with their file paths
    tests = [
        {'file': 'tests/fake_gmail.html'},  # Fake test
        {'file': 'tests/real_gmail.html'},  # Real test
        {'file': 'tests/fake_facebook.html'},
        {'file': 'tests/real_facebook.html'},
        {'file': 'tests/fake_netflix.html'},
        {'file': 'tests/real_netflix.html'},
        {'file': 'tests/fake_github.html'},
        {'file': 'tests/real_github.html'},

    ]
    
    # Randomly select a test from the list
    selected_test = random.choice(tests)
    
    # Pass only the file to the template (frontend will handle is_real)
    return render(request, selected_test['file'], {
        'user_id': request.session['user']['id']
    })

def report(request):
    if not is_authenticated(request):
        return JsonResponse({'success': False, 'error': 'Not logged in'})
    
    if request.method == 'POST':
        # Parse the request body (JSON format)
        data = json.loads(request.body)
        user_id = request.session['user']['id']
        is_correct = data.get('is_correct')
        is_real = data.get('is_real')  # This flag is passed from the frontend

        points = 0  # Default points for incorrect reporting

        try:
            # Points logic based on is_real flag
            if not is_real:  # Fake test (reporting phishing is correct)
                if is_correct:
                    points = 5  # Correctly identifying fake phishing earns 5 points
                else:
                    points = -5  # Penalize for incorrectly identifying phishing (Doing login)

            # For real phishing tests, the user should get 0 points for reporting phishing
            else:  # Real test
                points = 0  # No points for reporting a legitimate site
            
            # Update user points in the database
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET points = points + %s WHERE id = %s", (points, user_id))
            conn.commit()
            
            # Update session with new points
            request.session['user']['points'] += points
            request.session.modified = True
            
            return JsonResponse({
                'success': True, 
                'points': points,
                'total_points': request.session['user']['points']
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        finally:
            if 'conn' in locals():
                conn.close()
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def leaderboard(request):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.username, u.points 
            FROM users u
            ORDER BY u.points DESC
            LIMIT 10
        """)
        top_users = cursor.fetchall()
        return render(request, 'leaderboard.html', {
            'top_users': top_users,
            'current_user': request.session.get('user')
        })
    except Exception as e:
        return render(request, 'leaderboard.html', {'error': str(e)})
    finally:
        if 'conn' in locals():
            conn.close()