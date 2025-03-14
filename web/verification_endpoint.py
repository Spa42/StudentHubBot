"""
Flask endpoint to handle Discord account verification.

This would be implemented as part of the StudentHub web application.
"""

from flask import Flask, request, redirect, render_template, url_for, flash, session
import logging
import os
import sys
import asyncio

# Add the root directory to the Python path so we can import from bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.verification_handler import verify_discord_link

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")  # Change in production

@app.route('/link-discord')
def link_discord():
    """
    Endpoint to handle Discord account verification.
    Expected query parameters:
    - token: The verification token
    """
    token = request.args.get('token')
    
    if not token:
        logger.error("No token provided")
        flash("No verification token provided.", "error")
        return render_template('verification_failed.html', 
                               error_message="No verification token provided.")
    
    # Check if user is logged in
    if not is_logged_in():
        # Store the token in the session and redirect to login
        session['pending_discord_token'] = token
        logger.info("User not logged in, redirecting to login page")
        return redirect(url_for('login', next=url_for('link_discord')))
    
    # Get the user's StudentHub ID from the session
    studenthub_user_id = get_user_id_from_session()
    
    try:
        # Run the async verification function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        discord_user_id = loop.run_until_complete(
            verify_discord_link(token, studenthub_user_id)
        )
        loop.close()
        
        if discord_user_id:
            logger.info(f"Successfully linked Discord user {discord_user_id} to StudentHub user {studenthub_user_id}")
            flash("Your Discord account has been successfully linked!", "success")
            return render_template('verification_success.html')
        else:
            logger.error(f"Failed to link Discord account: Invalid token")
            flash("The verification token is invalid or has expired.", "error")
            return render_template('verification_failed.html', 
                                   error_message="The verification token is invalid or has expired.")
    except Exception as e:
        logger.error(f"Error linking Discord account: {e}")
        flash("An error occurred while linking your Discord account.", "error")
        return render_template('verification_failed.html', 
                               error_message="An error occurred during verification.")

@app.route('/login')
def login():
    """
    Mock login endpoint.
    This would be replaced with a real login system in the actual StudentHub application.
    """
    next_url = request.args.get('next', url_for('dashboard'))
    # In a real implementation, this would handle user login
    # For this demo, we'll simulate a successful login
    session['logged_in'] = True
    session['user_id'] = "student123"  # Mock user ID
    return redirect(next_url)

@app.route('/dashboard')
def dashboard():
    """
    Mock dashboard endpoint.
    This would be the user's dashboard in the actual StudentHub application.
    """
    if not is_logged_in():
        return redirect(url_for('login'))
    
    # Check if there's a pending Discord token in the session
    token = session.pop('pending_discord_token', None)
    if token:
        return redirect(url_for('link_discord', token=token))
    
    return "StudentHub Dashboard"

def is_logged_in():
    """Check if the user is logged in."""
    return session.get('logged_in', False)

def get_user_id_from_session():
    """Get the user's StudentHub ID from the session."""
    return session.get('user_id')

if __name__ == "__main__":
    app.run(debug=True, port=5000) 