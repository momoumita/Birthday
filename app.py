import os
import uuid
from flask import Flask, render_template, request, url_for, jsonify

app = Flask(__name__)

# --- Configuration ---
# This tells Flask where to save the uploaded pictures
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure the upload folder exists when the app starts
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# We will use a simple Python dictionary as our "database" for now. 
# (In a real production app, this would be SQLite or PostgreSQL)
database = {}

# --- Routes ---

@app.route('/')
def home():
    """This serves the main page for the Creator."""
    return render_template('index.html', friend_mode=False)


@app.route('/create_surprise', methods=['POST'])
def create_surprise():
    """This handles the file uploads and generates the unique link."""
    # 1. Get the text data from the form
    secret_message = request.form.get('secret_message')
    
    # 2. Get the files uploaded by the user
    uploaded_files = request.files.getlist('friend_pics')
    
    # 3. Generate a random, unique ID (e.g., 'a1b2c3d4')
    surprise_id = str(uuid.uuid4())[:8]
    
    # 4. Save the files to the static/uploads folder
    saved_image_paths = []
    for file in uploaded_files:
        if file.filename != '':
            # Add the unique ID to the filename so files don't overwrite each other
            filename = f"{surprise_id}_{file.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            saved_image_paths.append(filename)
            
    # 5. Save everything to our temporary database
    database[surprise_id] = {
        'secret_message': secret_message,
        'images': saved_image_paths
    }
    
    # 6. Generate the custom link to send to the friend
    unique_link = url_for('friend_entrance', surprise_id=surprise_id, _external=True)
    
    # For now, we return a simple success message with the link
    # Later, we can make this look like a beautiful comic-book popup!
    return f"<h3>Success! Share this link with your friend:</h3> <a href='{unique_link}'>{unique_link}</a>"


@app.route('/surprise/<surprise_id>')
def friend_entrance(surprise_id):
    """This is where the unique link takes the friend."""
    # 1. Look up the surprise ID in our database
    surprise_data = database.get(surprise_id)
    
    # 2. If the ID doesn't exist, show an error
    if not surprise_data:
        return "Oops! We couldn't find that surprise in Meowland.", 404
        
    # 3. If it exists, serve the HTML page but pass the specific data to it
    # We also pass 'friend_mode=True' so the frontend knows to skip the home page
    return render_template('index.html', friend_mode=True, surprise_data=surprise_data)


if __name__ == '__main__':
    # Starts the server!
    app.run(debug=True)
