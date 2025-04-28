from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import os
import smtplib
import mysql.connector
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
import random
from django.views.decorators.csrf import csrf_exempt

from phishshield import settings

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
            email VARCHAR(255) NOT NULL UNIQUE,
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
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if email exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return render(request, 'auth/register.html', {'error': 'email already exists'})
            
            # Insert new user with 0 points
            cursor.execute(
                "INSERT INTO users (email, password, points) VALUES (%s, %s, 0)",
                (email, password)
            )
            conn.commit()
            
            # Log the user in immediately after registration
            cursor.execute(
                "SELECT id, email, points FROM users WHERE email = %s",
                (email,)
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
    if is_authenticated(request):
        return redirect('dashboard')  # Redirect to the regular dashboard if already authenticated

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, email, points FROM users WHERE email = %s AND password = %s",
                (email, password)
            )
            user = cursor.fetchone()

            if user:
                request.session['user'] = user
                if user['email'] == 'admin@phishing.com':
                    return redirect('admin_dashboard')  # Redirect to admin dashboard if it's the admin
                return redirect('dashboard')  # Redirect to the regular dashboard for non-admins
            else:
                return render(request, 'auth/login.html', {'error': 'Invalid email or password'})
        except Exception as e:
            return render(request, 'auth/login.html', {'error': str(e)})
        finally:
            if 'conn' in locals():
                conn.close()

    return render(request, 'auth/login.html')


def admin_dashboard(request):
    if not is_authenticated(request):
        return redirect('login')

    user = request.session['user']
    if user['email'] != 'admin@phishing.com':
        return redirect('dashboard')

    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # Get recent users
        cursor.execute("SELECT id, email, points, level, created_at AS last_login FROM users ORDER BY created_at DESC LIMIT 10")
        users = cursor.fetchall()

        # Admin stats
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()['total_users']

        cursor.execute("SELECT COUNT(*) AS tests_taken FROM user_attempts")
        tests_taken = cursor.fetchone()['tests_taken']

        cursor.execute("SELECT COUNT(*) AS detected_attempts FROM user_attempts WHERE was_correct = TRUE")
        detected_attempts = cursor.fetchone()['detected_attempts']

        # Placeholder for logs
        logs = [
            "Admin logged in",
            "Fetched user data",
            "Rendered dashboard"
        ]

        # Get all available users for the dropdown
        cursor.execute("SELECT email FROM users")
        available_users = cursor.fetchall()

        # Load the phishing test data
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests.json')
        with open(json_file_path, 'r') as file:
            tests = json.load(file)

        return render(request, 'admin/dashboard.html', {
            'admin': user,
            'recent_users': users,
            'stats': {
                'total_users': total_users,
                'tests_taken': tests_taken,
                'detected_attempts': detected_attempts,
                'reports': 0  # Placeholder
            },
            'system_logs': logs,
            'available_users': available_users,
            'tests': tests  # Pass tests data for frontend
        })

    except Exception as e:
        return JsonResponse({'error': str(e)})
    finally:
        if 'conn' in locals():
            conn.close()

def update_test_emails(request):
    if not is_authenticated(request):
        return redirect('login')

    if request.method == 'POST':
        action = request.POST.get('action')
        test_index = int(request.POST.get('test_index'))
        email = request.POST.get('email')

        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests.json')

        try:
            with open(json_file_path, 'r+') as file:
                tests = json.load(file)
                test = tests[test_index]

                if action == 'add':
                    if email not in test['allowed_emails']:
                        test['allowed_emails'].append(email)
                elif action == 'remove':
                    if email in test['allowed_emails']:
                        test['allowed_emails'].remove(email)

                # Save the updated data back to the file
                file.seek(0)
                json.dump(tests, file, indent=4)
                file.truncate()

            return JsonResponse({'message': 'Test emails updated successfully!'})

        except Exception as e:
            return JsonResponse({'error': str(e)})

def manage_user(request):
    if not is_authenticated(request):
        return JsonResponse({'success': False, 'error': 'Not authenticated'})

    if request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')

        try:
            conn = get_db()
            cursor = conn.cursor()

            # User management actions
            if action in ['delete', 'edit', 'create']:
                user_id = data.get('user_id')
                
                if action == 'delete':
                    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                    conn.commit()
                    return JsonResponse({'success': True, 'message': 'User deleted successfully'})

                if action == 'edit':
                    new_email = data.get('new_email')
                    new_points = data.get('new_points')
                    new_level = data.get('new_level')
                    cursor.execute("""
                        UPDATE users
                        SET email = %s, points = %s, level = %s
                        WHERE id = %s
                    """, (new_email, new_points, new_level, user_id))
                    conn.commit()
                    return JsonResponse({'success': True, 'message': 'User updated successfully'})

                if action == 'create':
                    new_email = data.get('new_email')
                    password = data.get('password')
                    cursor.execute("""
                        INSERT INTO users (email, password, points)
                        VALUES (%s, %s, 0)
                    """, (new_email, password))
                    conn.commit()
                    return JsonResponse({'success': True, 'message': 'User created successfully'})

            # JSON management actions
            elif action in ['get_json', 'add_json_email', 'remove_json_email']:
                # Updated path to point to simulator/tests.json
                json_path = os.path.join(settings.BASE_DIR, 'simulator', 'tests.json')
                
                if action == 'get_json':
                    with open(json_path, 'r') as f:
                        json_data = json.load(f)
                    return JsonResponse({'success': True, 'data': json_data})
                
                elif action in ['add_json_email', 'remove_json_email']:
                    file_name = data.get('file_name')
                    email = data.get('email')
                    
                    with open(json_path, 'r') as f:
                        json_data = json.load(f)
                    
                    for item in json_data:
                        if item['file'] == file_name:
                            if action == 'add_json_email' and email not in item['allowed_emails']:
                                item['allowed_emails'].append(email)
                            elif action == 'remove_json_email' and email in item['allowed_emails']:
                                item['allowed_emails'].remove(email)
                    
                    with open(json_path, 'w') as f:
                        json.dump(json_data, f, indent=2)
                    
                    return JsonResponse({'success': True, 'message': 'JSON updated successfully'})

            return JsonResponse({'success': False, 'error': 'Invalid action'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

        finally:
            if 'conn' in locals():
                conn.close()

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

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

    try:
        # Load the tests from the JSON file
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests.json')
        with open(json_file_path, 'r') as file:
            tests = json.load(file)

        # Get the current user's email
        user_email = request.session['user']['email']

        # Filter the tests to include only the ones the user has access to
        accessible_tests = [test for test in tests if user_email in test['allowed_emails']]

        if not accessible_tests:
            return render(request, 'access_denied.html', {
                'message': "You do not have access to any tests."
            })

        # Randomly select a test from the accessible tests
        selected_test = random.choice(accessible_tests)

        website = os.path.splitext(os.path.basename(selected_test['file']))[0]
        request.session['website'] = website
        request.session.modified = True

        # Render the selected test
        return render(request, selected_test['file'], {
            'user_id': request.session['user']['id'],
            'email': user_email
        })
    
    except Exception as e:
        # Handle any errors, such as file not being found or json parse errors
        return JsonResponse({'error': str(e)})


def leaderboard(request):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.email, u.points 
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

def sendmail(email, code):
    username = "5de44d001@smtp-brevo.com"
    password = "a5IkKV9cCpvsfXEM"
    smtp_server = "smtp-relay.brevo.com"
    smtp_port = 587
    recipient_email = email
    subject = "PhishShield Password Reset Code"

    html_body = f"""
    <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    padding: 20px;
                }}
                .container {{
                    background-color: white;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }}
                .code {{
                    font-size: 22px;
                    font-weight: bold;
                    color: #4CAF50;
                }}
                .footer {{
                    font-size: 12px;
                    color: #777;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>PhishShield Password Reset</h2>
                <p>We received a request to reset your password.</p>
                <p>Your verification code is:</p>
                <p class="code">{code}</p>
                <p>Enter this code in the app to proceed with password reset.</p>
                <div class="footer">
                    <p>If you did not request this, you can ignore this email.</p>
                </div>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = f"PhishShield <{username}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, recipient_email, msg.as_string())

    print("Email sent successfully!")

# Step 1: Request email
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return render(request, 'auth/forgot_password.html', {'error': 'Email is not registered.'})

            code = random.randint(100000, 999999)
            request.session['reset_email'] = email
            request.session['reset_code'] = str(code)

            sendmail(email, code)

            return redirect('verify_code')

        except Exception as e:
            return render(request, 'auth/forgot_password.html', {'error': str(e)})
        finally:
            if 'conn' in locals():
                conn.close()

    return render(request, 'auth/forgot_password.html')


# Step 2: Enter verification code
def verify_code(request):
    if request.method == 'POST':
        input_code = request.POST['code']
        actual_code = request.session.get('reset_code')

        if input_code == actual_code:
            return redirect('reset_password')
        else:
            return render(request, 'auth/verify_code.html', {'error': 'Invalid verification code.'})

    return render(request, 'auth/verify_code.html')


# Step 3: Set new password
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        email = request.session.get('reset_email')

        if password != confirm_password:
            return render(request, 'auth/reset_password.html', {'error': 'Passwords do not match.'})

        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (password, email))
            conn.commit()

            request.session.pop('reset_email', None)
            request.session.pop('reset_code', None)

            return redirect('login')

        except Exception as e:
            return render(request, 'auth/reset_password.html', {'error': str(e)})
        finally:
            if 'conn' in locals():
                conn.close()

    return render(request, 'auth/reset_password.html')


def updatePoints(email, website, points):
    # File path for the ranks.json file
    json_file_path = os.path.join(os.path.dirname(__file__), 'ranks.json')

    # Load existing data
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as file:
            user_data = json.load(file)
    else:
        user_data = {}

    # Initialize website entry if needed
    if website not in user_data:
        user_data[website] = []

    # Find user or create new
    user_found = False
    for user in user_data[website]:
        if user['email'] == email:
            user['points'] += points
            user_found = True
            break

    if not user_found:
        user_data[website].append({'email': email, 'points': points})

    # Save updated data
    with open(json_file_path, 'w') as file:
        json.dump(user_data, file, indent=4)

    return user_data[website]  # Return the updated user data for the website


def report(request):
    if not is_authenticated(request):
        return JsonResponse({'success': False, 'error': 'Not logged in'})
    
    # This is where the website name and the user email are stored
    website = request.session.get('website')
    user_email = request.session['user']['email']

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

            # Call the updatePoints function to update the ranks.json file
            updated_data = updatePoints(user_email, website, points)

            return JsonResponse({
                'success': True, 
                'points': points,
                'total_points': request.session['user']['points'],
                'updated_data': updated_data  # Return the updated data for the website
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        finally:
            if 'conn' in locals():
                conn.close()
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Helper function to load the data from the JSON file
def get_ranks():

    json_file_path = os.path.join(os.path.dirname(__file__), 'ranks.json')
    
    # Open the ranks.json file and load its data
    with open(json_file_path, 'r') as f:
        return json.load(f)

# New endpoint for the rankings page
def rankings_view(request):
    # Get the ranks data from the JSON file
    data = get_ranks()

    # Extract the rankings for each website
    website_rankings = []
    for website, users in data.items():
        website_rankings.append({
            "website": website,
            "users": sorted(users, key=lambda x: x["points"], reverse=True)  # Sort by points descending
        })

    # Render the rankings page with the data
    return render(request, 'rankings.html', {'website_rankings': website_rankings})


def show_test_page(request, folder_name, page_name):
    try:
        # Dynamically render the requested page from either fake_sites or real_sites
        return render(request, f'tests/{folder_name}/{page_name}.html')
    except Exception as e:
        # If the template doesn't exist, raise a 404 error
        raise Http404(f"Page '{page_name}' not found in the '{folder_name}' folder.")
