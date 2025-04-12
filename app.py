from flask import Flask, render_template, request, jsonify, redirect, url_for, session, render_template_string
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'incredible_explorer_secret_key'  # Change this in production

# In-memory data storage (replace with a database in production)
users = {}
cultural_spots = [
    {
        "id": 1,
        "name": "Taj Mahal",
        "location": "Agra, Uttar Pradesh",
        "description": "An ivory-white marble mausoleum on the right bank of the river Yamuna.",
        "category": "Monument",
        "image_url": "https://placehold.co/600x400/e2e8f0/475569?text=Taj+Mahal",
        "coordinates": {"lat": 27.1751, "lng": 78.0421}
    },
    {
        "id": 2,
        "name": "Jaipur City Palace",
        "location": "Jaipur, Rajasthan",
        "description": "A palace complex in Jaipur, the capital of the Rajasthan state, India.",
        "category": "Palace",
        "image_url": "https://placehold.co/600x400/e2e8f0/475569?text=Jaipur+Palace",
        "coordinates": {"lat": 26.9255, "lng": 75.8236}
    },
    {
        "id": 3,
        "name": "Meenakshi Temple",
        "location": "Madurai, Tamil Nadu",
        "description": "A historic Hindu temple located on the southern bank of the Vaigai River.",
        "category": "Temple",
        "image_url": "https://placehold.co/600x400/e2e8f0/475569?text=Meenakshi+Temple",
        "coordinates": {"lat": 9.9195, "lng": 78.1193}
    }
]
quests = [
    {
        "id": 1,
        "title": "Temple Explorer",
        "description": "Discover the architectural marvels of ancient temples",
        "tasks": ["Visit 3 temples", "Learn about architecture", "Participate in a ritual"],
        "progress": 70,
        "icon": "om"
    },
    {
        "id": 2,
        "title": "Culinary Connoisseur",
        "description": "Experience the diverse flavors of Indian cuisine",
        "tasks": ["Try 5 local dishes", "Visit a spice market", "Cook with a local chef"],
        "progress": 40,
        "icon": "utensils"
    },
    {
        "id": 3,
        "title": "Artisan Apprentice",
        "description": "Learn traditional crafts from skilled artisans",
        "tasks": ["Watch pottery making", "Try block printing", "Buy directly from artisans"],
        "progress": 20,
        "icon": "hands"
    }
]
artisans = [
    {
        "id": 1,
        "name": "Rajesh Kumar",
        "craft": "Madhubani Painting",
        "location": "Bihar",
        "description": "Third-generation Madhubani artist specializing in natural dyes and traditional motifs",
        "image": "https://placehold.co/400x500/e2e8f0/475569?text=Artisan"
    },
    {
        "id": 2,
        "name": "Lakshmi Devi",
        "craft": "Patola Weaving",
        "location": "Gujarat",
        "description": "Master weaver creating intricate double ikat Patola sarees using ancient techniques",
        "image": "https://placehold.co/400x500/e2e8f0/475569?text=Artisan"
    },
    {
        "id": 3,
        "name": "Mohammed Ismail",
        "craft": "Bidri Metalwork",
        "location": "Karnataka",
        "description": "Award-winning Bidri craftsman known for his innovative designs and traditional methods",
        "image": "https://placehold.co/400x500/e2e8f0/475569?text=Artisan"
    }
]

# Routes
@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE, 
                                 cultural_spots=cultural_spots[:3],
                                 quests=quests,
                                 artisans=artisans)  # Pass the artisans list directly

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and check_password_hash(users[email]['password'], password):
            session['user'] = email
            session['user_data'] = users[email]  # Store user data in session
            return redirect(url_for('dashboard'))
        
        return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials")
    
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users:
            return render_template_string(SIGNUP_TEMPLATE, error="Email already exists")
        
        # Create new user with complete profile data
        users[email] = {
            'name': name,
            'password': generate_password_hash(password),
            'profile': {
                'bio': '',
                'country': 'India',  # Default country
                'favorite_spots': [],
                'level': 1,
                'experience': 0,
                'badges': []
            },
            'created_at': datetime.now()
        }
        
        # Store user data in session
        session['user'] = email
        session['user_data'] = users[email]
        
        # Redirect to dashboard instead of profile
        return redirect(url_for('dashboard'))
    
    return render_template_string(SIGNUP_TEMPLATE)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user = users[session['user']]
    
    if request.method == 'POST':
        user['profile']['bio'] = request.form.get('bio')
        user['profile']['country'] = request.form.get('country')
        user['profile']['favorite_spots'] = request.form.getlist('favorite_spots')
        
        return redirect(url_for('dashboard'))
    
    return render_template_string(PROFILE_TEMPLATE, user=user)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get user data from session
    user_data = session.get('user_data')
    if not user_data:
        # If session data is missing, try to get it from users dictionary
        if session['user'] in users:
            user_data = users[session['user']]
            session['user_data'] = user_data
        else:
            # If user not found, clear session and redirect to login
            session.clear()
            return redirect(url_for('login'))
    
    # Ensure user_data has the required profile structure
    if 'profile' not in user_data:
        user_data['profile'] = {
            'level': 1,
            'experience': 0,
            'badges': []
        }
        # Update the users dictionary and session
        users[session['user']] = user_data
        session['user_data'] = user_data
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                user=user_data,
                                cultural_spots=cultural_spots,
                                quests=quests)

@app.route('/admin')
def admin():
    if 'user' not in session or session['user'] != 'admin@incredibleexplorer.com':
        return redirect(url_for('login'))
    
    return render_template_string(ADMIN_TEMPLATE, 
                                 cultural_spots=cultural_spots,
                                 quests=quests,
                                 artisans=artisans,
                                 user_count=len(users))

@app.route('/api/cultural_spots', methods=['GET', 'POST'])
def api_cultural_spots():
    if request.method == 'POST':
        if 'user' not in session or session['user'] != 'admin@incredibleexplorer.com':
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.json
        new_id = max([spot['id'] for spot in cultural_spots]) + 1 if cultural_spots else 1
        data['id'] = new_id
        cultural_spots.append(data)
        return jsonify(data), 201
    
    return jsonify(cultural_spots)

@app.route('/api/cultural_spots/<int:spot_id>', methods=['PUT', 'DELETE'])
def api_cultural_spot(spot_id):
    if 'user' not in session or session['user'] != 'admin@incredibleexplorer.com':
        return jsonify({"error": "Unauthorized"}), 401
    
    spot_index = next((i for i, spot in enumerate(cultural_spots) if spot['id'] == spot_id), None)
    
    if spot_index is None:
        return jsonify({"error": "Spot not found"}), 404
    
    if request.method == 'DELETE':
        deleted_spot = cultural_spots.pop(spot_index)
        return jsonify(deleted_spot)
    
    data = request.json
    data['id'] = spot_id
    cultural_spots[spot_index] = data
    return jsonify(data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/scan-monument')
def scan_monument():
    return render_template_string(SCAN_TEMPLATE)

# Add this new route after the dashboard route
@app.route('/map-view')
def map_view():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template_string(MAP_VIEW_TEMPLATE, 
                                user=session.get('user_data'),
                                cultural_spots=cultural_spots)

@app.route('/artisans')
def show_artisans():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template_string(ARTISANS_TEMPLATE, artisans=artisans)

# Add these new routes after the existing routes
@app.route('/api/artisans/<int:artisan_id>')
def get_artisan(artisan_id):
    artisan = next((a for a in artisans if a['id'] == artisan_id), None)
    if artisan:
        return jsonify(artisan)
    return jsonify({'error': 'Artisan not found'}), 404

@app.route('/api/artisans/<int:artisan_id>/crafts')
def get_artisan_crafts(artisan_id):
    # This is a placeholder - in a real app, you would fetch crafts from a database
    crafts = [
        {
            'id': 1,
            'name': 'Traditional Painting',
            'description': 'Hand-painted artwork using natural dyes',
            'price': 2500
        },
        {
            'id': 2,
            'name': 'Handwoven Scarf',
            'description': 'Beautifully crafted scarf using traditional techniques',
            'price': 1500
        }
    ]
    return jsonify(crafts)

@app.route('/api/messages', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    artisan_id = data.get('artisan_id')
    message = data.get('message')
    
    if not artisan_id or not message:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # In a real app, you would save the message to a database
    return jsonify({'success': True, 'message': 'Message sent successfully'})

@app.route('/api/schedule', methods=['POST'])
def schedule_meeting():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    artisan_id = data.get('artisan_id')
    date = data.get('date')
    time = data.get('time')
    meeting_type = data.get('meeting_type')
    
    if not all([artisan_id, date, time, meeting_type]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # In a real app, you would save the meeting to a database
    return jsonify({'success': True, 'message': 'Meeting scheduled successfully'})

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    craft_id = data.get('craft_id')
    
    if not craft_id:
        return jsonify({'error': 'Missing craft ID'}), 400
    
    # In a real app, you would add the item to the user's cart in a database
    return jsonify({'success': True, 'message': 'Item added to cart'})

@app.route('/api/checkout', methods=['POST'])
def checkout():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # In a real app, you would process the payment and create an order
    return jsonify({'success': True, 'message': 'Order placed successfully'})

# HTML Templates
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Incredible Explorer - Culture Comes Alive</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        @keyframes sway {
            0%, 100% { transform: rotate(-5deg); }
            50% { transform: rotate(5deg); }
        }
        
        .animate-float {
            animation: float 6s ease-in-out infinite;
        }
        
        .animate-float-delay {
            animation: float 6s ease-in-out 2s infinite;
        }
        
        .animate-float-slow {
            animation: float 8s ease-in-out infinite;
        }
        
        .animate-sway {
            animation: sway 4s ease-in-out infinite;
        }
        
        .animate-sway-delay {
            animation: sway 4s ease-in-out 1s infinite;
        }
        
        .animation-delay-200 {
            animation-delay: 0.2s;
        }
        
        .animation-delay-400 {
            animation-delay: 0.4s;
        }

        .map-container {
            position: relative;
            cursor: pointer;
            transition: transform 0.3s ease;
        }

        .map-container:hover {
            transform: scale(1.02);
        }

        .map-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .map-container:hover .map-overlay {
            opacity: 1;
        }

        .map-overlay-text {
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
    </style>
</head>
<body class="font-sans bg-amber-50 text-gray-900 min-h-screen">
    <!-- Navbar -->
    <nav class="bg-white shadow-md px-6 py-4">
        <div class="container mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <div class="w-10 h-10 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 rounded-lg flex items-center justify-center transform rotate-45">
                    <i class="fas fa-compass text-white text-xl transform -rotate-45"></i>
                </div>
                <span class="ml-2 text-xl font-bold text-gray-800">Incredible Explorer</span>
            </div>
            
            <div class="hidden md:flex space-x-8">
                <a href="#features" class="hover:text-yellow-600 transition">Features</a>
                <a href="#map" class="hover:text-yellow-600 transition">Explore</a>
                <a href="#quests" class="hover:text-yellow-600 transition">Quests</a>
                <a href="#artisans" class="hover:text-yellow-600 transition">Artisans</a>
            </div>
            
            <div class="flex items-center space-x-4">
                <button 
                    id="audioToggle"
                    class="p-2 rounded-full bg-amber-100 hover:bg-amber-200 transition"
                >
                    <i class="fas fa-volume-mute text-yellow-700"></i>
                </button>
                <a href="/login" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
                    Sign In
                </a>
            </div>
        </div>
    </nav>
    
    <!-- Hero Section -->
    <section class="relative py-20 overflow-hidden">
        <div class="absolute inset-0 z-0 opacity-10">
            <div class="absolute top-10 left-10 w-20 h-20 bg-yellow-500 rounded-full animate-float"></div>
            <div class="absolute top-40 right-20 w-16 h-16 bg-red-500 rounded-full animate-float-delay"></div>
            <div class="absolute bottom-20 left-1/4 w-24 h-24 bg-indigo-500 rounded-full animate-float-slow"></div>
            <!-- Decorative elements that look like diyas or temple bells -->
            <div class="absolute top-1/3 right-1/3 w-8 h-12 bg-orange-400 rounded-t-full animate-sway"></div>
            <div class="absolute bottom-1/4 right-1/4 w-8 h-12 bg-orange-400 rounded-t-full animate-sway-delay"></div>
        </div>
        
        <div class="container mx-auto px-6 relative z-10">
            <div class="flex flex-col md:flex-row items-center">
                <div class="md:w-1/2 mb-10 md:mb-0">
                    <h1 class="text-4xl md:text-6xl font-bold text-indigo-900 mb-4">
                        Explore India Like Never Before
                    </h1>
                    <p class="text-xl md:text-2xl text-yellow-700 mb-8">
                        Scan monuments. Talk to AI guides. Unlock hidden stories.
                    </p>
                    <div class="flex space-x-4">
                        <a href="/dashboard" class="bg-yellow-600 hover:bg-yellow-700 text-white font-bold py-3 px-6 rounded-lg transition transform hover:scale-105">
                            Start Exploring
                        </a>
                        <a href="/scan-monument" class="border-2 border-indigo-600 text-indigo-600 font-bold py-3 px-6 rounded-lg hover:bg-indigo-50 transition">
                            Scan Your First Monument
                        </a>
                    </div>
                </div>
                    
                <div class="md:w-1/2">
                    <div class="relative">
                        <div class="w-full h-96 bg-gradient-to-r from-indigo-100 to-amber-100 rounded-xl overflow-hidden shadow-lg">
                            <div class="absolute inset-0 flex items-center justify-center">
                                <img 
                                    src="https://images.unsplash.com/photo-1566438480900-0609be27a4be?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80" 
                                    alt="Taj Mahal AR Scan" 
                                    class="object-cover h-full w-full"
                                />
                                <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 border-4 border-yellow-400 border-dashed rounded-lg animate-pulse"></div>
                            </div>
                        </div>
                        <div class="absolute -bottom-6 -right-6 bg-white p-4 rounded-lg shadow-lg">
                            <div class="text-sm font-medium text-indigo-600">AI Guide Says:</div>
                            <div class="text-gray-700">"The Taj Mahal was built in 1632 by Emperor Shah Jahan..."</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Features Section -->
    <section id="features" class="py-16 bg-white">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl font-bold text-center text-indigo-900 mb-12">What You Can Do</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {% set features = [
                    {
                        "title": "Scan Monuments in AR",
                        "icon": "monument",
                        "description": "Point your camera at monuments to reveal their stories and hidden details in augmented reality."
                    },
                    {
                        "title": "Chat with an AI Tour Guide",
                        "icon": "comments",
                        "description": "Ask questions and get personalized insights from your AI companion who knows local history and culture."
                    },
                    {
                        "title": "Find Hidden Cultural Gems",
                        "icon": "gem",
                        "description": "Discover off-the-beaten-path locations that only locals know about."
                    },
                    {
                        "title": "Complete Cultural Quests",
                        "icon": "tasks",
                        "description": "Earn badges and rewards by completing challenges that deepen your cultural understanding."
                    },
                    {
                        "title": "Meet Local Artists",
                        "icon": "paint-brush",
                        "description": "Connect with artisans and creators to learn about traditional crafts and support local culture."
                    },
                    {
                        "title": "Create Your Cultural Journey",
                        "icon": "route",
                        "description": "Build personalized itineraries based on your interests and available time."
                    }
                ] %}
                
                {% for feature in features %}
                <div class="bg-amber-50 rounded-xl p-6 shadow-md hover:shadow-lg transition transform hover:-translate-y-1">
                    <div class="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
                        <i class="fas fa-{{ feature.icon }} text-2xl text-yellow-600"></i>
                    </div>
                    <h3 class="text-xl font-bold text-indigo-800 mb-2">{{ feature.title }}</h3>
                    <p class="text-gray-600">{{ feature.description }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>
    
    <!-- Map Section -->
    <section id="map" class="py-16 bg-indigo-50">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl font-bold text-center text-indigo-900 mb-4">Discover Cultural Hotspots</h2>
            <p class="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
                Explore hidden gems, historical monuments, and local experiences across India
            </p>
            
            <a href="/map-view" class="block">
                <div class="bg-white rounded-xl shadow-lg overflow-hidden map-container">
                <div class="h-96 bg-gray-200 relative">
                    <img 
                            src="https://images.unsplash.com/photo-1526778548025-fa2f459cd5ce?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1000&q=80" 
                        alt="Interactive Cultural Map" 
                        class="w-full h-full object-cover"
                    />
                        <div class="map-overlay">
                            <div class="map-overlay-text">
                                Click to Explore the Map
                            </div>
                        </div>
                    
                    <!-- Map pins -->
                    <div class="absolute top-1/4 left-1/3 animate-bounce">
                        <div class="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                            <i class="fas fa-landmark text-white text-xs"></i>
                        </div>
                    </div>
                    <div class="absolute top-1/2 right-1/4 animate-bounce animation-delay-200">
                        <div class="w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center">
                            <i class="fas fa-store text-white text-xs"></i>
                        </div>
                    </div>
                    <div class="absolute bottom-1/3 left-1/2 animate-bounce animation-delay-400">
                        <div class="w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center">
                            <i class="fas fa-landmark text-white text-xs"></i>
                        </div>
                    </div>
                </div>
                
                <div class="p-6 bg-white">
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm">Temples</span>
                        <span class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">Markets</span>
                        <span class="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm">Monuments</span>
                        <span class="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">Workshops</span>
                    </div>
                    
                    <div class="flex justify-between items-center">
                        <button class="text-indigo-600 hover:text-indigo-800 transition">
                            <i class="fas fa-location-arrow mr-2"></i> Find Nearby
                        </button>
                        <button class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
                            View Full Map
                        </button>
                    </div>
                </div>
            </div>
            </a>
        </div>
    </section>
    
    <!-- Quests Section -->
    <section id="quests" class="py-16 bg-white">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl font-bold text-center text-indigo-900 mb-4">Cultural Challenge Quests</h2>
            <p class="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
                Earn badges for discovering, learning, and exploring India's rich cultural heritage
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {% for quest in quests %}
                <div class="bg-amber-50 rounded-xl overflow-hidden shadow-md">
                    <div class="bg-gradient-to-r from-yellow-600 to-red-600 p-4 text-white">
                        <div class="flex justify-between items-center">
                            <h3 class="text-xl font-bold">{{ quest.title }}</h3>
                            <div class="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                                <i class="fas fa-{{ quest.icon }} text-xl"></i>
                            </div>
                        </div>
                    </div>
                    
                    <div class="p-6">
                        <div class="mb-4">
                            <div class="flex justify-between text-sm mb-1">
                                <span>Progress</span>
                                <span>{{ quest.progress }}%</span>
                            </div>
                            <div class="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                    class="bg-yellow-600 h-2 rounded-full" 
                                    style="width: {{ quest.progress }}%"
                                ></div>
                            </div>
                        </div>
                        
                        <ul class="space-y-2 mb-4">
                            {% for task in quest.tasks %}
                            <li class="flex items-start">
                                <div class="w-5 h-5 rounded-full border-2 border-yellow-600 flex-shrink-0 mt-0.5 mr-2">
                                    {% if loop.index0 == 0 %}
                                    <div class="w-3 h-3 bg-yellow-600 rounded-full m-0.5"></div>
                                    {% endif %}
                                </div>
                                <span class="{{ 'text-gray-900' if loop.index0 == 0 else 'text-gray-500' }}">
                                    {{ task }}
                                </span>
                            </li>
                            {% endfor %}
                        </ul>
                        
                        <button class="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition">
                            Continue Quest
                        </button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>
    
    <!-- AI Tour Guide Section -->
    <section class="py-16 bg-indigo-900 text-white">
        <div class="container mx-auto px-6">
            <div class="flex flex-col md:flex-row items-center">
                <div class="md:w-1/2 mb-10 md:mb-0">
                    <h2 class="text-3xl font-bold mb-4">Meet Your AI Tour Guide</h2>
                    <p class="text-indigo-200 mb-6">
                        Your personal storytelling companion who knows the history, culture, and hidden stories of every location.
                    </p>
                    
                    <div class="bg-indigo-800 p-4 rounded-lg mb-6">
                        <div class="flex items-start mb-4">
                            <div class="w-10 h-10 bg-yellow-500 rounded-full flex-shrink-0 mr-3"></div>
                            <div class="bg-indigo-700 rounded-lg p-3">
                                <p class="text-white">Tell me about the significance of these carvings on the temple wall.</p>
                            </div>
                        </div>
                        
                        <div class="flex items-start">
                            <div class="w-10 h-10 bg-indigo-500 rounded-full flex-shrink-0 mr-3 flex items-center justify-center">
                                <i class="fas fa-robot text-white"></i>
                            </div>
                            <div class="bg-white rounded-lg p-3">
                                <p class="text-gray-800">These carvings depict the story of Ramayana. This particular scene shows Lord Rama's coronation after returning from exile. Notice how the artisans used the local stone to create such intricate details...</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex flex-wrap gap-2">
                        <span class="px-3 py-1 bg-indigo-700 rounded-full text-sm">Supports 12+ Languages</span>
                        <span class="px-3 py-1 bg-indigo-700 rounded-full text-sm">Voice & Text</span>
                        <span class="px-3 py-1 bg-indigo-700 rounded-full text-sm">Works Offline</span>
                    </div>
                </div>
                
                <div class="md:w-1/2">
                    <div class="relative">
                        <div class="w-full h-96 bg-gradient-to-r from-indigo-800 to-purple-900 rounded-xl overflow-hidden shadow-lg">
                            <img 
                                src="https://placehold.co/600x400/312e81/a5b4fc?text=AI+Tour+Guide" 
                                alt="AI Tour Guide Interface" 
                                class="object-cover h-full w-full opacity-75"
                            />
                            
                            <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-indigo-900 p-6">
                                <div class="flex items-center justify-between">
                                    <div class="flex items-center">
                                        <div class="w-10 h-10 bg-indigo-500 rounded-full flex items-center justify-center mr-3">
                                            <i class="fas fa-microphone text-white"></i>
                                        </div>
                                        <span class="text-white">Ask me anything...</span>
                                    </div>
                                    <div class="flex space-x-2">
                                        <button class="w-10 h-10 bg-indigo-700 rounded-full flex items-center justify-center">
                                            <i class="fas fa-camera text-white"></i>
                                        </button>
                                        <button class="w-10 h-10 bg-yellow-500 rounded-full flex items-center justify-center">
                                            <i class="fas fa-paper-plane text-white"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
    
    <!-- Artisan Connect Section -->
    <section id="artisans" class="py-16 bg-amber-50">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl font-bold text-center text-indigo-900 mb-4">Connect with Local Artisans</h2>
            <p class="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
                Support traditional crafts and meet the people keeping cultural heritage alive
            </p>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {% for artisan in artisans %}
                <div class="bg-white rounded-xl overflow-hidden shadow-md">
                    <div class="h-64 overflow-hidden">
                        <img 
                            src="{{ artisan.image }}" 
                            alt="{{ artisan.name }}" 
                            class="w-full h-full object-cover transition transform hover:scale-105"
                        />
                    </div>
                    
                    <div class="p-6">
                        <h3 class="text-xl font-bold text-indigo-900 mb-1">{{ artisan.name }}</h3>
                        <div class="text-yellow-600 mb-2">{{ artisan.craft }}</div>
                        <div class="text-gray-500 text-sm mb-4">
                            <i class="fas fa-map-marker-alt mr-2"></i>
                            {{ artisan.location }}
                        </div>
                        
                        <div class="flex space-x-2">
                            <button class="flex-1 bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition">
                                Book Workshop
                            </button>
                            <button class="flex-1 border border-yellow-600 text-yellow-600 py-2 rounded-lg hover:bg-yellow-50 transition">
                                Shop Crafts
                            </button>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="mt-10 text-center">
                <button class="bg-white border-2 border-indigo-600 text-indigo-600 px-6 py-3 rounded-lg hover:bg-indigo-50 transition">
                    View All Artisans
                </button>
            </div>
        </div>
    </section>
    
    <!-- Tech Section -->
    <section class="py-16 bg-white">
        <div class="container mx-auto px-6">
            <h2 class="text-3xl font-bold text-center text-indigo-900 mb-12">Powered By</h2>
            
            <div class="grid grid-cols-2 md:grid-cols-6 gap-8">
                {% set technologies = [
                    { "name": "React", "icon": "react" },
                    { "name": "Tailwind CSS", "icon": "wind" },
                    { "name": "Google Maps", "icon": "map-marked-alt" },
                    { "name": "GPT-4", "icon": "robot" },
                    { "name": "WebAR", "icon": "vr-cardboard" },
                    { "name": "Firebase", "icon": "database" }
                ] %}
                
                {% for tech in technologies %}
                <div class="flex flex-col items-center">
                    <div class="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-3">
                        <i class="fab fa-{{ tech.icon }} text-2xl text-indigo-600"></i>
                    </div>
                    <span class="text-gray-700">{{ tech.name }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>
    
    <!-- CTA Section -->
    <section class="py-16 bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div class="container mx-auto px-6 text-center">
            <h2 class="text-3xl font-bold mb-4">Ready to Explore India's Cultural Wonders?</h2>
            <p class="mb-8 max-w-2xl mx-auto">
                Download the app now and start your immersive cultural journey
            </p>
            
            <div class="flex flex-col sm:flex-row justify-center space-y-4 sm:space-y-0 sm:space-x-4">
                <button class="bg-white text-indigo-600 px-6 py-3 rounded-lg hover:bg-gray-100 transition flex items-center justify-center">
                    <i class="fab fa-google-play mr-2 text-xl"></i>
                    <span>Google Play</span>
                </button>
                <button class="bg-white text-indigo-600 px-6 py-3 rounded-lg hover:bg-gray-100 transition flex items-center justify-center">
                    <i class="fab fa-apple mr-2 text-xl"></i>
                    <span>App Store</span>
                </button>
            </div>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="bg-indigo-900 text-white py-12">
        <div class="container mx-auto px-6">
            <div class="flex flex-col md:flex-row justify-between">
                <div class="mb-8 md:mb-0">
                    <div class="flex items-center space-x-2 mb-4">
                        <div class="w-10 h-10 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 rounded-lg flex items-center justify-center transform rotate-45">
                            <i class="fas fa-compass text-white text-xl transform -rotate-45"></i>
                        </div>
                        <span class="ml-2 text-xl font-bold text-gray-800">Incredible Explorer</span>
                    </div>
                    <p class="text-indigo-200 max-w-xs">
                        Reviving India's heritage using AR, AI, and gamification
                    </p>
                </div>
                
                <div class="grid grid-cols-2 md:grid-cols-3 gap-8">
                    <div>
                        <h3 class="font-bold mb-4">Explore</h3>
                        <ul class="space-y-2 text-indigo-200">
                            <li><a href="#" class="hover:text-white transition">Monuments</a></li>
                            <li><a href="#" class="hover:text-white transition">Cultural Sites</a></li>
                            <li><a href="#" class="hover:text-white transition">Hidden Gems</a></li>
                            <li><a href="#" class="hover:text-white transition">Artisan Workshops</a></li>
                        </ul>
                    </div>
                    
                    <div>
                        <h3 class="font-bold mb-4">Company</h3>
                        <ul class="space-y-2 text-indigo-200">
                            <li><a href="#" class="hover:text-white transition">About Us</a></li>
                            <li><a href="#" class="hover:text-white transition">Our Team</a></li>
                            <li><a href="#" class="hover:text-white transition">Careers</a></li>
                            <li><a href="#" class="hover:text-white transition">Contact</a></li>
                        </ul>
                    </div>
                    
                    <div>
                        <h3 class="font-bold mb-4">Legal</h3>
                        <ul class="space-y-2 text-indigo-200">
                            <li><a href="#" class="hover:text-white transition">Privacy Policy</a></li>
                            <li><a href="#" class="hover:text-white transition">Terms of Service</a></li>
                            <li><a href="#" class="hover:text-white transition">Cookie Policy</a></li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="border-t border-indigo-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
                <div class="mb-4 md:mb-0">
                    <div class="flex space-x-4">
                        <a href="#" class="text-indigo-200 hover:text-white transition">
                            <i class="fab fa-facebook-f"></i>
                        </a>
                        <a href="#" class="text-indigo-200 hover:text-white transition">
                            <i class="fab fa-twitter"></i>
                        </a>
                        <a href="#" class="text-indigo-200 hover:text-white transition">
                            <i class="fab fa-instagram"></i>
                        </a>
                        <a href="#" class="text-indigo-200 hover:text-white transition">
                            <i class="fab fa-youtube"></i>
                        </a>
                    </div>
                </div>
                
                <div class="text-indigo-300 text-sm">
                    <span>Built for Culture Hackathon 2025</span>
                    <span class="mx-2">|</span>
                    <span>&copy; 2025 Incredible Explorer. All rights reserved.</span>
                </div>
            </div>
        </div>
    </footer>
    
    <!-- Audio element -->
    <audio id="backgroundMusic" loop>
        <source src="https://example.com/traditional-music.mp3" type="audio/mpeg">
    </audio>
    
    <script>
        // Audio toggle functionality
        const audioToggle = document.getElementById('audioToggle');
        const backgroundMusic = document.getElementById('backgroundMusic');
        let isPlaying = false;
        
        audioToggle.addEventListener('click', function() {
            if (isPlaying) {
                backgroundMusic.pause();
                audioToggle.innerHTML = '<i class="fas fa-volume-mute text-yellow-700"></i>';
            } else {
                backgroundMusic.play().catch(e => {
                    console.log('Audio playback failed:', e);
                });
                audioToggle.innerHTML = '<i class="fas fa-volume-up text-yellow-700"></i>';
            }
            isPlaying = !isPlaying;
        });
        
        // Mobile menu toggle
        const mobileMenuButton = document.createElement('button');
        mobileMenuButton.className = 'md:hidden p-2';
        mobileMenuButton.innerHTML = '<i class="fas fa-bars text-indigo-900 text-xl"></i>';
        
        const navContainer = document.querySelector('nav .container');
        const navLinks = document.querySelector('nav .hidden.md\\:flex');
        
        navContainer.insertBefore(mobileMenuButton, navContainer.querySelector('.flex.items-center.space-x-4'));
        
        mobileMenuButton.addEventListener('click', function() {
            navLinks.classList.toggle('hidden');
            navLinks.classList.toggle('flex');
            navLinks.classList.toggle('flex-col');
            navLinks.classList.toggle('absolute');
            navLinks.classList.toggle('top-16');
            navLinks.classList.toggle('left-0');
            navLinks.classList.toggle('right-0');
            navLinks.classList.toggle('bg-white');
            navLinks.classList.toggle('p-4');
            navLinks.classList.toggle('shadow-md');
            navLinks.classList.toggle('z-50');
        });
    </script>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Incredible Explorer</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body class="bg-amber-50 min-h-screen flex items-center justify-center">
    <div class="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <div class="text-center mb-8">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-yellow-600 rounded-full mb-4">
                <span class="text-white text-2xl font-bold">IE</span>
            </div>
            <h1 class="text-2xl font-bold text-indigo-900">Welcome Back to Incredible Explorer</h1>
            <p class="text-gray-600">Sign in to continue your cultural journey</p>
        </div>
        
        {% if error %}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {{ error }}
        </div>
        {% endif %}
        
        <form action="/login" method="post" class="space-y-6">
            <div>
                <label for="email" class="block text-gray-700 mb-2">Email Address</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-envelope text-gray-400"></i>
                    </div>
                    <input 
                        type="email" 
                        id="email" 
                        name="email" 
                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="your@email.com"
                        required
                    >
                </div>
            </div>
            
            <div>
                <div class="flex justify-between mb-2">
                    <label for="password" class="block text-gray-700">Password</label>
                    <a href="/forgot-password" class="text-sm text-indigo-600 hover:text-indigo-800">Forgot Password?</a>
                </div>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-lock text-gray-400"></i>
                    </div>
                    <input 
                        type="password" 
                        id="password" 
                        name="password" 
                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="••••••••"
                        required
                    >
                </div>
            </div>
            
            <div class="flex items-center">
                <input 
                    type="checkbox" 
                    id="remember" 
                    name="remember" 
                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                >
                <label for="remember" class="ml-2 block text-gray-700">Remember me</label>
            </div>
            
            <button 
                type="submit" 
                class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
                Sign In
            </button>
        </form>
        
        <div class="mt-6 text-center">
            <p class="text-gray-600">
                Don't have an account? 
                <a href="/signup" class="text-indigo-600 hover:text-indigo-800 font-medium">Sign up</a>
            </p>
        </div>
        
        <div class="mt-8 pt-6 border-t border-gray-200">
            <p class="text-center text-gray-600 mb-4">Or continue with</p>
            <div class="flex space-x-4">
                <button class="flex-1 flex items-center justify-center py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                    <i class="fab fa-google text-red-500 mr-2"></i>
                    <span>Google</span>
                </button>
                <button class="flex-1 flex items-center justify-center py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                    <i class="fab fa-facebook-f text-blue-600 mr-2"></i>
                    <span>Facebook</span>
                </button>
            </div>
        </div>
    </div>
</body>
</html>
'''

SIGNUP_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up - Incredible Explorer</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body class="bg-amber-50 min-h-screen flex items-center justify-center py-12">
    <div class="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <div class="text-center mb-8">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-yellow-600 rounded-full mb-4">
                <span class="text-white text-2xl font-bold">IE</span>
            </div>
            <h1 class="text-2xl font-bold text-indigo-900">Join Incredible Explorer</h1>
            <p class="text-gray-600">Create an account to start your cultural journey</p>
        </div>
        
        {% if error %}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {{ error }}
        </div>
        {% endif %}
        
        <form action="/signup" method="post" class="space-y-6">
            <div>
                <label for="name" class="block text-gray-700 mb-2">Full Name</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-user text-gray-400"></i>
                    </div>
                    <input 
                        type="text" 
                        id="name" 
                        name="name" 
                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="John Doe"
                        required
                    >
                </div>
            </div>
            
            <div>
                <label for="email" class="block text-gray-700 mb-2">Email Address</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-envelope text-gray-400"></i>
                    </div>
                    <input 
                        type="email" 
                        id="email" 
                        name="email" 
                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="your@email.com"
                        required
                    >
                </div>
            </div>
            
            <div>
                <label for="password" class="block text-gray-700 mb-2">Password</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-lock text-gray-400"></i>
                    </div>
                    <input 
                        type="password" 
                        id="password" 
                        name="password" 
                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="••••••••"
                        required
                        minlength="8"
                    >
                </div>
                <p class="text-xs text-gray-500 mt-1">Must be at least 8 characters long</p>
            </div>
            
            <div>
                <label for="confirm_password" class="block text-gray-700 mb-2">Confirm Password</label>
                <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <i class="fas fa-lock text-gray-400"></i>
                    </div>
                    <input 
                        type="password" 
                        id="confirm_password" 
                        name="confirm_password" 
                        class="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        placeholder="••••••••"
                        required
                    >
                </div>
            </div>
            
            <div class="flex items-center">
                <input 
                    type="checkbox" 
                    id="terms" 
                    name="terms" 
                    class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                    required
                >
                <label for="terms" class="ml-2 block text-gray-700 text-sm">
                    I agree to the <a href="#" class="text-indigo-600 hover:text-indigo-800">Terms of Service</a> and <a href="#" class="text-indigo-600 hover:text-indigo-800">Privacy Policy</a>
                </label>
            </div>
            
            <button 
                type="submit" 
                class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
            >
                Create Account
            </button>
        </form>
        
        <div class="mt-6 text-center">
            <p class="text-gray-600">
                Already have an account? 
                <a href="/login" class="text-indigo-600 hover:text-indigo-800 font-medium">Sign in</a>
            </p>
        </div>
        
        <div class="mt-8 pt-6 border-t border-gray-200">
            <p class="text-center text-gray-600 mb-4">Or sign up with</p>
            <div class="flex space-x-4">
                <button class="flex-1 flex items-center justify-center py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                    <i class="fab fa-google text-red-500 mr-2"></i>
                    <span>Google</span>
                </button>
                <button class="flex-1 flex items-center justify-center py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                    <i class="fab fa-facebook-f text-blue-600 mr-2"></i>
                    <span>Facebook</span>
                </button>
            </div>
        </div>
    </div>
    
    <script>
        // Password confirmation validation
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');
        const form = document.querySelector('form');
        
        form.addEventListener('submit', function(event) {
            if (password.value !== confirmPassword.value) {
                event.preventDefault();
                alert('Passwords do not match!');
                confirmPassword.focus();
            }
        });
    </script>
</body>
</html>
'''

PROFILE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Your Profile - Incredible Explorer</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body class="bg-amber-50 min-h-screen">
    <nav class="bg-white shadow-md px-6 py-4">
        <div class="container mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <div class="w-10 h-10 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 rounded-lg flex items-center justify-center transform rotate-45">
                    <i class="fas fa-compass text-white text-xl transform -rotate-45"></i>
                </div>
                <span class="ml-2 text-xl font-bold text-gray-800">Incredible Explorer</span>
            </div>
            
            <div class="flex items-center space-x-4">
                <a href="/logout" class="text-indigo-600 hover:text-indigo-800">
                    <i class="fas fa-sign-out-alt mr-1"></i> Logout
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container mx-auto px-6 py-12">
        <div class="max-w-3xl mx-auto">
            <div class="bg-white rounded-xl shadow-lg p-8">
                <div class="text-center mb-8">
                    <h1 class="text-2xl font-bold text-indigo-900">Complete Your Traveler Profile</h1>
                    <p class="text-gray-600">Tell us a bit about yourself to personalize your experience</p>
                </div>
                
                <form action="/profile" method="post" class="space-y-6">
                    <div class="flex flex-col md:flex-row gap-6">
                        <div class="md:w-1/3">
                            <div class="bg-gray-100 rounded-xl p-6 text-center">
                                <div class="w-32 h-32 bg-gray-300 rounded-full mx-auto mb-4 overflow-hidden">
                                    <img 
                                        id="profile-preview" 
                                        src="https://placehold.co/400x400/e2e8f0/475569?text=Profile" 
                                        alt="Profile Picture" 
                                        class="w-full h-full object-cover"
                                    >
                                </div>
                                <label for="profile-upload" class="block w-full text-center px-4 py-2 bg-indigo-600 text-white rounded-lg cursor-pointer hover:bg-indigo-700 transition">
                                    <i class="fas fa-camera mr-2"></i> Upload Photo
                                </label>
                                <input id="profile-upload" type="file" accept="image/*" class="hidden">
                                <p class="text-xs text-gray-500 mt-2">JPG, PNG or GIF, max 5MB</p>
                            </div>
                        </div>
                        
                        <div class="md:w-2/3 space-y-6">
                            <div>
                                <label for="name" class="block text-gray-700 mb-2">Full Name</label>
                                <input 
                                    type="text" 
                                    id="name" 
                                    name="name" 
                                    value="{{ user.name }}"
                                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    required
                                >
                            </div>
                            
                            <div>
                                <label for="bio" class="block text-gray-700 mb-2">Bio</label>
                                <textarea 
                                    id="bio" 
                                    name="bio" 
                                    rows="3" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                    placeholder="Tell us about yourself and your travel interests..."
                                >{{ user.profile.bio }}</textarea>
                            </div>
                            
                            <div>
                                <label for="country" class="block text-gray-700 mb-2">Country</label>
                                <select 
                                    id="country" 
                                    name="country" 
                                    class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                >
                                    <option value="">Select your country</option>
                                    <option value="USA" {% if user.profile.country == 'USA' %}selected{% endif %}>United States</option>
                                    <option value="UK" {% if user.profile.country == 'UK' %}selected{% endif %}>United Kingdom</option>
                                    <option value="Canada" {% if user.profile.country == 'Canada' %}selected{% endif %}>Canada</option>
                                    <option value="Australia" {% if user.profile.country == 'Australia' %}selected{% endif %}>Australia</option>
                                    <option value="India" {% if user.profile.country == 'India' %}selected{% endif %}>India</option>
                                    <option value="Japan" {% if user.profile.country == 'Japan' %}selected{% endif %}>Japan</option>
                                    <option value="Germany" {% if user.profile.country == 'Germany' %}selected{% endif %}>Germany</option>
                                    <option value="France" {% if user.profile.country == 'France' %}selected{% endif %}>France</option>
                                </select>
                            </div>
                            
                            <div>
                                <label class="block text-gray-700 mb-2">Favorite Travel Spots</label>
                                <div class="grid grid-cols-2 gap-2">
                                    <label class="flex items-center space-x-2">
                                        <input 
                                            type="checkbox" 
                                            name="favorite_spots" 
                                            value="temples" 
                                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                            {% if 'temples' in user.profile.favorite_spots %}checked{% endif %}
                                        >
                                        <span>Temples & Religious Sites</span>
                                    </label>
                                    <label class="flex items-center space-x-2">
                                        <input 
                                            type="checkbox" 
                                            name="favorite_spots" 
                                            value="monuments" 
                                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                            {% if 'monuments' in user.profile.favorite_spots %}checked{% endif %}
                                        >
                                        <span>Monuments & Historic Sites</span>
                                    </label>
                                    <label class="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            name="favorite_spots"
                                            value="markets"
                                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                            {% if 'markets' in user.profile.favorite_spots %}checked{% endif %}
                                        >
                                        <span>Markets & Bazaars</span>
                                    </label>
                                    <label class="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            name="favorite_spots"
                                            value="food"
                                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                            {% if 'food' in user.profile.favorite_spots %}checked{% endif %}
                                        >
                                        <span>Food & Culinary Experiences</span>
                                    </label>
                                    <label class="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            name="favorite_spots"
                                            value="nature"
                                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                            {% if 'nature' in user.profile.favorite_spots %}checked{% endif %}
                                        >
                                        <span>Nature & Landscapes</span>
                                    </label>
                                    <label class="flex items-center space-x-2">
                                        <input
                                            type="checkbox"
                                            name="favorite_spots"
                                            value="crafts"
                                            class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                                            {% if 'crafts' in user.profile.favorite_spots %}checked{% endif %}
                                        >
                                        <span>Arts & Crafts</span>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
                        <a href="/dashboard" class="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition">
                            Skip for Now
                        </a>
                        <button
                            type="submit"
                            class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                        >
                            Save Profile
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <script>
        // Profile picture preview
        const profileUpload = document.getElementById('profile-upload');
        const profilePreview = document.getElementById('profile-preview');

        profileUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    profilePreview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Incredible Explorer</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="container mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <a href="/" class="flex items-center">
                        <div class="w-10 h-10 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 rounded-lg flex items-center justify-center transform rotate-45">
                            <i class="fas fa-compass text-white text-xl transform -rotate-45"></i>
                </div>
                        <span class="ml-2 text-xl font-bold text-gray-800">Incredible Explorer</span>
                    </a>
            </div>
            <div class="flex items-center space-x-4">
                    <a href="/profile" class="text-gray-600 hover:text-gray-800">
                        <i class="fas fa-user-circle text-2xl"></i>
                    </a>
                    <a href="/logout" class="text-gray-600 hover:text-gray-800">
                        <i class="fas fa-sign-out-alt text-2xl"></i>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <div class="container mx-auto px-6 py-8">
        <div class="flex flex-col md:flex-row gap-8">
            <!-- Sidebar -->
            <div class="md:w-1/4">
                <div class="bg-white rounded-xl shadow-md p-6 mb-6">
                    <div class="flex items-center space-x-4 mb-6">
                        <div class="w-16 h-16 bg-indigo-100 rounded-full overflow-hidden">
                            <img
                                src="https://placehold.co/100x100/e2e8f0/475569?text=User"
                                alt="Profile"
                                class="w-full h-full object-cover"
                            >
                        </div>
                        <div>
                            <h2 class="font-bold text-xl">{{ user.name }}</h2>
                            <p class="text-gray-500">Explorer Level {{ user.profile.level }}</p>
                        </div>
                    </div>

                    <div class="mb-4">
                        <div class="flex justify-between text-sm mb-1">
                            <span>Experience</span>
                            <span>{{ user.profile.experience }}/500 XP</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                            <div class="bg-yellow-600 h-2 rounded-full" style="width: {{ (user.profile.experience / 500) * 100 }}%"></div>
                        </div>
                    </div>

                    <div class="flex justify-between text-center">
                        <div>
                            <div class="text-2xl font-bold text-indigo-600">12</div>
                            <div class="text-xs text-gray-500">Places Visited</div>
                        </div>
                        <div>
                            <div class="text-2xl font-bold text-indigo-600">3</div>
                            <div class="text-xs text-gray-500">Quests Completed</div>
                        </div>
                        <div>
                            <div class="text-2xl font-bold text-indigo-600">{{ user.profile.badges|length }}</div>
                            <div class="text-xs text-gray-500">Badges Earned</div>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-xl shadow-md p-6">
                    <h3 class="font-bold text-lg mb-4">My Badges</h3>
                    <div class="grid grid-cols-3 gap-4">
                        {% for badge in user.profile.badges %}
                        <div class="flex flex-col items-center">
                            <div class="w-12 h-12 bg-{{ badge.color }}-100 rounded-full flex items-center justify-center mb-1">
                                <i class="fas fa-{{ badge.icon }} text-{{ badge.color }}-600"></i>
                            </div>
                            <span class="text-xs text-center">{{ badge.name }}</span>
                        </div>
                        {% endfor %}
                        {% for i in range(6 - user.profile.badges|length) %}
                        <div class="flex flex-col items-center opacity-40">
                            <div class="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center mb-1">
                                <i class="fas fa-lock text-gray-400"></i>
                            </div>
                            <span class="text-xs text-center">Locked</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="md:w-3/4">
                <!-- Start Exploring Section -->
                <div class="bg-white rounded-xl shadow-md p-6 mb-6">
                    <div class="flex flex-col md:flex-row items-center justify-between mb-6">
                        <div class="text-center md:text-left mb-4 md:mb-0">
                            <h2 class="font-bold text-2xl text-indigo-900 mb-2">Ready to Explore?</h2>
                            <p class="text-gray-600">Start your journey to discover India's incredible cultural heritage</p>
                        </div>
                        <div class="flex space-x-4">
                            <a href="/scan-monument" class="bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 transition flex items-center">
                                <i class="fas fa-camera mr-2"></i> Scan Monument
                            </a>
                            <a href="/map-view" class="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition flex items-center">
                                <i class="fas fa-map-marked-alt mr-2"></i> View Map
                            </a>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="bg-amber-50 rounded-lg p-4">
                            <div class="flex items-center mb-3">
                                <div class="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center mr-3">
                                    <i class="fas fa-camera text-amber-600"></i>
                                </div>
                                <h3 class="font-bold">Scan Monuments</h3>
                            </div>
                            <p class="text-gray-600 text-sm">Use your camera to scan monuments and discover their stories</p>
                        </div>
                        <div class="bg-indigo-50 rounded-lg p-4">
                            <div class="flex items-center mb-3">
                                <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                                    <i class="fas fa-map-marked-alt text-indigo-600"></i>
                                </div>
                                <h3 class="font-bold">Explore Nearby</h3>
                            </div>
                            <p class="text-gray-600 text-sm">Find cultural spots and heritage sites near your location</p>
                        </div>
                        <div class="bg-green-50 rounded-lg p-4">
                            <div class="flex items-center mb-3">
                                <div class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center mr-3">
                                    <i class="fas fa-tasks text-green-600"></i>
                                </div>
                                <h3 class="font-bold">Complete Quests</h3>
                            </div>
                            <p class="text-gray-600 text-sm">Take on quests to earn rewards and unlock new experiences</p>
                        </div>
                    </div>
                </div>

                <!-- Leaderboard Section -->
                <div class="bg-white rounded-xl shadow-md p-6 mb-6">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="font-bold text-xl">Top Explorers</h2>
                        <span class="text-sm text-gray-500">Updated daily</span>
                    </div>

                    <div class="space-y-4">
                        <!-- Top 3 with special styling -->
                        <div class="flex items-center bg-gradient-to-r from-yellow-50 to-amber-50 rounded-lg p-4">
                            <div class="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center text-white font-bold mr-4">
                                1
                                </div>
                                <div class="flex-grow">
                                    <div class="flex justify-between items-center">
                                    <div class="flex items-center">
                                        <img src="https://placehold.co/40x40/e2e8f0/475569?text=User" alt="User" class="w-10 h-10 rounded-full mr-3">
                                        <div>
                                            <h3 class="font-bold">Rahul Sharma</h3>
                                            <p class="text-sm text-gray-500">Mumbai, India</p>
                                            <div class="flex mt-1 space-x-1">
                                                <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">🏆 Explorer</span>
                                                <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">📸 50+ Scans</span>
                                                <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">🎯 10+ Quests</span>
                                        </div>
                                    </div>
                                </div>
                                    <div class="text-right">
                                        <div class="font-bold text-yellow-600">2,500 Points</div>
                                        <div class="text-xs text-gray-500">5 Badges • 3 Rewards</div>
                            </div>
                        </div>
                    </div>
                </div>

                        <div class="flex items-center bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-4">
                            <div class="w-8 h-8 bg-gray-400 rounded-full flex items-center justify-center text-white font-bold mr-4">
                                2
                    </div>
                            <div class="flex-grow">
                                <div class="flex justify-between items-center">
                                    <div class="flex items-center">
                                        <img src="https://placehold.co/40x40/e2e8f0/475569?text=User" alt="User" class="w-10 h-10 rounded-full mr-3">
                                        <div>
                                            <h3 class="font-bold">Priya Patel</h3>
                                            <p class="text-sm text-gray-500">Delhi, India</p>
                                            <div class="flex mt-1 space-x-1">
                                                <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">🏆 Explorer</span>
                                                <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">📸 40+ Scans</span>
                                </div>
                            </div>
                        </div>
                                    <div class="text-right">
                                        <div class="font-bold text-gray-600">1,800 Points</div>
                                        <div class="text-xs text-gray-500">4 Badges • 2 Rewards</div>
                    </div>
                </div>
            </div>
        </div>

                        <div class="flex items-center bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg p-4">
                            <div class="w-8 h-8 bg-amber-600 rounded-full flex items-center justify-center text-white font-bold mr-4">
                                3
                        </div>
                            <div class="flex-grow">
                                <div class="flex justify-between items-center">
                                    <div class="flex items-center">
                                        <img src="https://placehold.co/40x40/e2e8f0/475569?text=User" alt="User" class="w-10 h-10 rounded-full mr-3">
                                <div>
                                            <h3 class="font-bold">Amit Kumar</h3>
                                            <p class="text-sm text-gray-500">Bangalore, India</p>
                                            <div class="flex mt-1 space-x-1">
                                                <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">🏆 Explorer</span>
                                                <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">🎯 5+ Quests</span>
                                </div>
                            </div>
                        </div>
                                    <div class="text-right">
                                        <div class="font-bold text-amber-600">1,500 Points</div>
                                        <div class="text-xs text-gray-500">3 Badges • 2 Rewards</div>
                    </div>
                </div>
                </div>
            </div>

                        <!-- Other top explorers -->
                        <div class="space-y-2">
                            <div class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition">
                        <div class="flex items-center">
                                    <div class="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-gray-600 text-xs font-bold mr-3">
                                        4
                            </div>
                                    <img src="https://placehold.co/32x32/e2e8f0/475569?text=User" alt="User" class="w-8 h-8 rounded-full mr-3">
                            <div>
                                        <h3 class="font-bold text-sm">Neha Gupta</h3>
                                        <p class="text-xs text-gray-500">Kolkata, India</p>
                                        <div class="flex mt-1 space-x-1">
                                            <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">📸 30+ Scans</span>
                            </div>
                        </div>
                                </div>
                                <div class="text-right">
                                    <div class="font-bold text-sm">1,200 Points</div>
                                    <div class="text-xs text-gray-500">2 Badges • 1 Reward</div>
                        </div>
                    </div>

                            <div class="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg transition">
                        <div class="flex items-center">
                                    <div class="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center text-gray-600 text-xs font-bold mr-3">
                                        5
                            </div>
                                    <img src="https://placehold.co/32x32/e2e8f0/475569?text=User" alt="User" class="w-8 h-8 rounded-full mr-3">
                            <div>
                                        <h3 class="font-bold text-sm">Vikram Singh</h3>
                                        <p class="text-xs text-gray-500">Chennai, India</p>
                                        <div class="flex mt-1 space-x-1">
                                            <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">🎯 3+ Quests</span>
                            </div>
                        </div>
                        </div>
                                <div class="text-right">
                                    <div class="font-bold text-sm">1,000 Points</div>
                                    <div class="text-xs text-gray-500">2 Badges • 1 Reward</div>
                    </div>
                            </div>
                        </div>
                    </div>

                    <div class="mt-6 pt-4 border-t border-gray-200">
                        <div class="flex items-center justify-between">
                        <div class="flex items-center">
                                <div class="w-6 h-6 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 text-xs font-bold mr-3">
                                    {{ user.profile.level }}
                            </div>
                            <div>
                                    <h3 class="font-bold text-sm">Your Rank</h3>
                                    <p class="text-xs text-gray-500">{{ user.profile.experience }} Points • {{ user.profile.badges|length }} Badges</p>
                            </div>
                        </div>
                            <a href="#" class="text-indigo-600 hover:text-indigo-800 text-sm">
                                View Full Leaderboard <i class="fas fa-arrow-right ml-1"></i>
                            </a>
                        </div>
                    </div>
                </div>

                <!-- Active Quests -->
                <div class="bg-white rounded-xl shadow-md p-6 mb-6">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="font-bold text-xl">Active Quests</h2>
                        <a href="#" class="text-indigo-600 hover:text-indigo-800 text-sm">View All</a>
                    </div>

                    <div class="space-y-4">
                        {% for quest in quests %}
                        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                            <div class="flex items-start">
                                <div class="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mr-4 flex-shrink-0">
                                    <i class="fas fa-{{ quest.icon }} text-amber-600"></i>
                                            </div>
                                <div class="flex-grow">
                                    <div class="flex justify-between items-start">
                                        <h3 class="font-bold text-lg">{{ quest.title }}</h3>
                                        <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">{{ quest.progress }}% Complete</span>
                                            </div>
                                    <p class="text-gray-600 text-sm mb-2">{{ quest.description }}</p>
                                    <div class="w-full bg-gray-200 rounded-full h-1.5 mb-2">
                                        <div class="bg-yellow-600 h-1.5 rounded-full" style="width: {{ quest.progress }}%"></div>
                                        </div>
                                    <div class="flex justify-between items-center">
                                        <div class="text-xs text-gray-500">
                                            Next task: {{ quest.tasks[0] if quest.tasks else "All tasks completed!" }}
                    </div>
                                        <button class="text-indigo-600 hover:text-indigo-800 text-sm font-medium">
                                            Continue
                        </button>
                    </div>
                                            </div>
                                            </div>
                                        </div>
                                {% endfor %}
                    </div>
                </div>

                <!-- Artisans Section -->
                <div class="bg-white rounded-xl shadow-md p-6 mb-6">
                    <div class="flex justify-between items-center mb-6">
                        <h2 class="font-bold text-xl">Connect with Local Artisans</h2>
                        <a href="/artisans" class="text-indigo-600 hover:text-indigo-800">
                            <i class="fas fa-hands-helping mr-1"></i> Meet Artisans
                        </a>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-amber-50 rounded-lg p-4">
                            <div class="flex items-center mb-3">
                                <div class="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center mr-3">
                                    <i class="fas fa-hands text-amber-600"></i>
                        </div>
                                <h3 class="font-bold">Meet Artisans</h3>
                        </div>
                            <p class="text-gray-600 text-sm">Connect with skilled artisans and learn about traditional crafts</p>
                    </div>
                        <div class="bg-indigo-50 rounded-lg p-4">
                            <div class="flex items-center mb-3">
                                <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center mr-3">
                                    <i class="fas fa-shopping-bag text-indigo-600"></i>
                    </div>
                                <h3 class="font-bold">Purchase Crafts</h3>
                        </div>
                            <p class="text-gray-600 text-sm">Buy authentic handmade products directly from artisans</p>
                        </div>
                    </div>
                        </div>
                        </div>
                    </div>
            </div>
</body>
</html>
'''

SCAN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scan Monument - Incredible Explorer</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        .camera-container {
            position: relative;
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
        }
        .camera-view {
            width: 100%;
            height: 400px;
            background-color: #000;
            border-radius: 1rem;
            overflow: hidden;
        }
        .scan-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            border: 2px solid #f59e0b;
            border-radius: 1rem;
            pointer-events: none;
        }
        .scan-line {
            position: absolute;
            width: 100%;
            height: 2px;
            background-color: #f59e0b;
            animation: scan 2s linear infinite;
        }
        @keyframes scan {
            0% { top: 0; }
            100% { top: 100%; }
        }
        .result-container {
            display: none;
        }
        .loading {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #f59e0b;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-amber-50 min-h-screen">
    <nav class="bg-white shadow-md px-6 py-4">
        <div class="container mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <div class="w-10 h-10 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 rounded-lg flex items-center justify-center transform rotate-45">
                    <i class="fas fa-compass text-white text-xl transform -rotate-45"></i>
                </div>
                <span class="ml-2 text-xl font-bold text-gray-800">Incredible Explorer</span>
            </div>
            <a href="/" class="text-indigo-600 hover:text-indigo-800">
                <i class="fas fa-arrow-left mr-1"></i> Back to Home
            </a>
        </div>
    </nav>

    <div class="container mx-auto px-6 py-12">
        <div class="max-w-2xl mx-auto text-center">
            <h1 class="text-3xl font-bold text-indigo-900 mb-4">Scan a Monument</h1>
            <p class="text-gray-600 mb-8">Point your camera at a monument to discover its history and hidden stories</p>

            <!-- Camera View -->
            <div class="camera-container mb-8">
                <div class="camera-view">
                    <div class="w-full h-full flex items-center justify-center text-white">
                        <div class="text-center">
                            <i class="fas fa-camera text-4xl mb-4"></i>
                            <p>Camera access required</p>
                        </div>
                    </div>
                </div>
                <div class="scan-overlay">
                    <div class="scan-line"></div>
                </div>
            </div>

            <!-- Result View -->
            <div class="result-container bg-white rounded-xl shadow-lg p-6 mb-8">
                <div class="flex justify-between items-start mb-4">
                    <h2 class="text-2xl font-bold text-indigo-900" id="monument-name">Monument Name</h2>
                    <span class="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm" id="monument-category">Category</span>
                </div>
                <div class="mb-4">
                    <img id="captured-image" src="" alt="Captured Monument" class="w-full h-64 object-cover rounded-lg mb-4">
                </div>
                <div class="text-left">
                    <p class="text-gray-600 mb-2"><i class="fas fa-map-marker-alt text-indigo-600 mr-2"></i> <span id="monument-location">Location</span></p>
                    <p class="text-gray-700" id="monument-description">Description will appear here...</p>
                </div>
                <div class="mt-6">
                    <button id="scan-again" class="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition">
                        <i class="fas fa-camera mr-2"></i> Scan Another Monument
                    </button>
                </div>
            </div>

            <div class="flex justify-center space-x-4">
                <button id="startCamera" class="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 transition">
                    <i class="fas fa-camera mr-2"></i> Start Camera
                </button>
                <button id="capture" class="bg-yellow-600 text-white px-6 py-3 rounded-lg hover:bg-yellow-700 transition hidden">
                    <i class="fas fa-camera mr-2"></i> Capture
                </button>
            </div>
        </div>
    </div>

    <!-- Loading Overlay -->
    <div class="loading" id="loading">
        <div class="loading-spinner"></div>
    </div>

    <script>
        let stream = null;
        const cameraView = document.querySelector('.camera-view');
        const startCameraBtn = document.getElementById('startCamera');
        const captureBtn = document.getElementById('capture');
        const resultContainer = document.querySelector('.result-container');
        const loading = document.getElementById('loading');
        const scanAgainBtn = document.getElementById('scan-again');
        const capturedImage = document.getElementById('captured-image');

        // Sample monument data (in a real app, this would come from your backend)
        const monumentData = {
            "Taj Mahal": {
                name: "Taj Mahal",
                category: "Monument",
                location: "Agra, Uttar Pradesh",
                description: "The Taj Mahal is an ivory-white marble mausoleum on the right bank of the river Yamuna in Agra. It was commissioned in 1632 by the Mughal emperor Shah Jahan to house the tomb of his favorite wife, Mumtaz Mahal."
            },
            "Jaipur City Palace": {
                name: "Jaipur City Palace",
                category: "Palace",
                location: "Jaipur, Rajasthan",
                description: "The City Palace, Jaipur was established at the same time as the city of Jaipur, by Maharaja Sawai Jai Singh II, who moved his court to Jaipur from Amber, in 1727."
            },
            "Meenakshi Temple": {
                name: "Meenakshi Temple",
                category: "Temple",
                location: "Madurai, Tamil Nadu",
                description: "Meenakshi Temple is a historic Hindu temple located on the southern bank of the Vaigai River in Madurai. It is dedicated to Meenakshi, a form of Parvati, and her consort, Sundareshwar, a form of Shiva."
            }
        };

        startCameraBtn.addEventListener('click', async () => {
            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                cameraView.innerHTML = '';
                const video = document.createElement('video');
                video.srcObject = stream;
                video.autoplay = true;
                video.playsInline = true;
                cameraView.appendChild(video);
                
                startCameraBtn.classList.add('hidden');
                captureBtn.classList.remove('hidden');
                resultContainer.style.display = 'none';
            } catch (err) {
                console.error('Error accessing camera:', err);
                alert('Could not access camera. Please ensure you have granted camera permissions.');
            }
        });

        captureBtn.addEventListener('click', () => {
            // Show loading overlay
            loading.style.display = 'flex';
            
            // Simulate image processing delay
            setTimeout(() => {
                // Get the video element
                const video = cameraView.querySelector('video');
                
                // Create a canvas to capture the image
                const canvas = document.createElement('canvas');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                // Convert canvas to image
                const imageData = canvas.toDataURL('image/jpeg');
                capturedImage.src = imageData;
                
                // Stop the camera stream
                stream.getTracks().forEach(track => track.stop());
                
                // Hide camera view and show result
                cameraView.style.display = 'none';
                resultContainer.style.display = 'block';
                
                // Simulate monument recognition (in a real app, this would be done by your backend)
                const recognizedMonument = "Taj Mahal"; // This would be determined by your image recognition system
                const monument = monumentData[recognizedMonument];
                
                // Update the result view with monument information
                document.getElementById('monument-name').textContent = monument.name;
                document.getElementById('monument-category').textContent = monument.category;
                document.getElementById('monument-location').textContent = monument.location;
                document.getElementById('monument-description').textContent = monument.description;
                
                // Hide loading overlay
                loading.style.display = 'none';
            }, 2000); // Simulate 2-second processing time
        });

        scanAgainBtn.addEventListener('click', () => {
            // Reset the view
            cameraView.style.display = 'block';
            resultContainer.style.display = 'none';
            startCameraBtn.classList.remove('hidden');
            captureBtn.classList.add('hidden');
            
            // Start camera again
            startCameraBtn.click();
        });
    </script>
</body>
</html>
'''

MAP_VIEW_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Map View - Incredible Explorer</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        #map {
            height: 600px;
            width: 100%;
            border-radius: 1rem;
        }
        .search-container {
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
            width: 300px;
        }
        .travel-modes {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .info-window {
            max-width: 300px;
        }
        .info-window img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .route-info {
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: white;
            padding: 15px;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            max-width: 300px;
        }
    </style>
</head>
<body class="bg-amber-50 min-h-screen">
    <nav class="bg-white shadow-md px-6 py-4">
        <div class="container mx-auto flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <div class="w-10 h-10 bg-gradient-to-r from-amber-500 via-orange-500 to-red-500 rounded-lg flex items-center justify-center transform rotate-45">
                    <i class="fas fa-compass text-white text-xl transform -rotate-45"></i>
                </div>
                <span class="ml-2 text-xl font-bold text-gray-800">Incredible Explorer</span>
            </div>
                <a href="/dashboard" class="text-indigo-600 hover:text-indigo-800">
                    <i class="fas fa-arrow-left mr-1"></i> Back to Dashboard
                </a>
        </div>
    </nav>

    <div class="container mx-auto px-6 py-8">
        <div class="bg-white rounded-xl shadow-lg p-6">
            <h1 class="text-2xl font-bold text-indigo-900 mb-4">Explore Cultural Spots</h1>
            <p class="text-gray-600 mb-6">Discover and navigate to cultural heritage sites across India</p>
            
            <div class="relative">
                <!-- Search Box -->
                <div class="search-container">
                    <div class="bg-white rounded-lg shadow-lg p-4">
                        <div class="relative">
                            <input 
                                type="text" 
                                id="search-box" 
                                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                placeholder="Search for a location..."
                            >
                            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <i class="fas fa-search text-gray-400"></i>
                            </div>
                        </div>
                        <div id="search-results" class="mt-2 max-h-60 overflow-y-auto hidden">
                            <!-- Search results will be populated here -->
                        </div>
                        </div>
                </div>

                <!-- Travel Modes -->
                <div class="travel-modes">
                    <div class="flex space-x-2">
                        <button id="walking-mode" class="p-2 rounded-lg hover:bg-gray-100 transition" title="Walking">
                            <i class="fas fa-walking text-gray-600"></i>
                        </button>
                        <button id="driving-mode" class="p-2 rounded-lg hover:bg-gray-100 transition" title="Driving">
                            <i class="fas fa-car text-gray-600"></i>
                        </button>
                        <button id="transit-mode" class="p-2 rounded-lg hover:bg-gray-100 transition" title="Public Transit">
                            <i class="fas fa-bus text-gray-600"></i>
                        </button>
                        <button id="bicycle-mode" class="p-2 rounded-lg hover:bg-gray-100 transition" title="Bicycle">
                            <i class="fas fa-bicycle text-gray-600"></i>
                        </button>
                    </div>
                </div>

                <!-- Route Info -->
                <div class="route-info hidden" id="route-info">
                    <div class="flex justify-between items-center mb-2">
                        <h3 class="font-bold">Route Information</h3>
                        <button id="close-route" class="text-gray-500 hover:text-gray-700">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    <div id="route-details">
                        <div class="flex items-center mb-2">
                            <i class="fas fa-clock text-gray-500 mr-2"></i>
                            <span id="duration" class="text-sm">--</span>
                                </div>
                                        <div class="flex items-center">
                            <i class="fas fa-road text-gray-500 mr-2"></i>
                            <span id="distance" class="text-sm">--</span>
                                        </div>
                                    </div>
                    <button id="start-navigation" class="mt-3 w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition">
                        <i class="fas fa-directions mr-2"></i> Start Navigation
                            </button>
                    </div>
                    
                    <div id="map"></div>
            </div>
        </div>
    </div>

    <script>
        let map;
        let markers = [];
        let infoWindows = [];
        let searchBox;
        let searchResults = [];
        let directionsService;
        let directionsRenderer;
        let currentTravelMode = google.maps.TravelMode.DRIVING;
        let currentRoute = null;

        // Initialize the map
        function initMap() {
            // Default to India's center
            const indiaCenter = { lat: 20.5937, lng: 78.9629 };
            
            map = new google.maps.Map(document.getElementById('map'), {
                center: indiaCenter,
                zoom: 5,
                styles: [
                    {
                        "featureType": "poi",
                        "elementType": "labels",
                        "stylers": [{ "visibility": "off" }]
                    }
                ]
            });

            // Initialize directions service
            directionsService = new google.maps.DirectionsService();
            directionsRenderer = new google.maps.DirectionsRenderer({
                map: map,
                suppressMarkers: true
            });

            // Create search box
            const searchInput = document.getElementById('search-box');
            searchBox = new google.maps.places.SearchBox(searchInput);
            
            // Add markers for cultural spots
            const spots = {{ cultural_spots | tojson | safe }};
            spots.forEach(spot => {
                const marker = new google.maps.Marker({
                    position: { lat: spot.coordinates.lat, lng: spot.coordinates.lng },
                    map: map,
                    title: spot.name,
                    icon: {
                        url: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png'
                    }
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div class="info-window">
                            <img src="${spot.image_url}" alt="${spot.name}">
                            <h3 class="font-bold text-lg">${spot.name}</h3>
                            <p class="text-gray-600 text-sm">${spot.location}</p>
                            <p class="text-gray-700 mt-2">${spot.description}</p>
                            <div class="mt-2">
                                <span class="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">${spot.category}</span>
                            </div>
                            <div class="mt-4">
                                <button class="text-indigo-600 hover:text-indigo-800 text-sm font-medium get-directions" 
                                        onclick="getDirections(${spot.coordinates.lat}, ${spot.coordinates.lng})">
                                    <i class="fas fa-directions mr-1"></i> Get Directions
                                </button>
                            </div>
                        </div>
                    `
                });

                marker.addListener('click', () => {
                    infoWindows.forEach(iw => iw.close());
                    infoWindow.open(map, marker);
                });

                markers.push(marker);
                infoWindows.push(infoWindow);
            });

            // Set up travel mode buttons
            const travelModes = {
                'walking-mode': google.maps.TravelMode.WALKING,
                'driving-mode': google.maps.TravelMode.DRIVING,
                'transit-mode': google.maps.TravelMode.TRANSIT,
                'bicycle-mode': google.maps.TravelMode.BICYCLING
            };

            Object.keys(travelModes).forEach(modeId => {
                document.getElementById(modeId).addEventListener('click', () => {
                    currentTravelMode = travelModes[modeId];
                    if (currentRoute) {
                        calculateAndDisplayRoute(currentRoute.origin, currentRoute.destination);
                    }
                    // Update active button style
                    document.querySelectorAll('.travel-modes button').forEach(btn => {
                        btn.classList.remove('bg-indigo-100', 'text-indigo-600');
                    });
                    document.getElementById(modeId).classList.add('bg-indigo-100', 'text-indigo-600');
                });
            });

            // Close route info
            document.getElementById('close-route').addEventListener('click', () => {
                document.getElementById('route-info').classList.add('hidden');
                directionsRenderer.setMap(null);
                currentRoute = null;
            });

            // Start navigation
            document.getElementById('start-navigation').addEventListener('click', () => {
                if (currentRoute) {
                    // In a real app, this would open the native navigation app
                    alert('Opening navigation...');
                }
            });
        }

        function getDirections(destLat, destLng) {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(position => {
                    const origin = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };
                    const destination = { lat: destLat, lng: destLng };
                    
                    calculateAndDisplayRoute(origin, destination);
                }, () => {
                    alert('Please enable location services to get directions');
                });
            } else {
                alert('Geolocation is not supported by your browser');
            }
        }

        function calculateAndDisplayRoute(origin, destination) {
            const request = {
                origin: origin,
                destination: destination,
                travelMode: currentTravelMode
            };

            directionsService.route(request, (result, status) => {
                if (status === 'OK') {
                    directionsRenderer.setMap(map);
                    directionsRenderer.setDirections(result);
                    
                    // Update route info
                    const route = result.routes[0];
                    const duration = route.legs[0].duration.text;
                    const distance = route.legs[0].distance.text;
                    
                    document.getElementById('duration').textContent = `Duration: ${duration}`;
                    document.getElementById('distance').textContent = `Distance: ${distance}`;
                    document.getElementById('route-info').classList.remove('hidden');
                    
                    // Store current route
                    currentRoute = { origin, destination };
                }
            });
        }

            // Listen for search box changes
            searchBox.addListener('places_changed', () => {
                const places = searchBox.getPlaces();
                if (places.length === 0) return;

                // Clear previous markers
            markers.forEach(marker => marker.setMap(null));
            markers = [];
            infoWindows.forEach(iw => iw.close());
            infoWindows = [];

                // For each place, get the icon, name and location
                const bounds = new google.maps.LatLngBounds();
                places.forEach(place => {
                    if (!place.geometry) return;

                // Create a marker for each place
                    const marker = new google.maps.Marker({
                        map: map,
                        title: place.name,
                        position: place.geometry.location,
                        icon: {
                        url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                    }
                });

                const infoWindow = new google.maps.InfoWindow({
                    content: `
                        <div class="info-window">
                            <h3 class="font-bold text-lg">${place.name}</h3>
                            <p class="text-gray-600 text-sm">${place.formatted_address}</p>
                            <div class="mt-4">
                                <button class="text-indigo-600 hover:text-indigo-800 text-sm font-medium get-directions" 
                                        onclick="getDirections(${place.geometry.location.lat()}, ${place.geometry.location.lng()})">
                                    <i class="fas fa-directions mr-1"></i> Get Directions
                                </button>
                            </div>
                        </div>
                    `
                });

                    marker.addListener('click', () => {
                    infoWindows.forEach(iw => iw.close());
                    infoWindow.open(map, marker);
                    });

                markers.push(marker);
                infoWindows.push(infoWindow);

                    if (place.geometry.viewport) {
                        bounds.union(place.geometry.viewport);
                    } else {
                        bounds.extend(place.geometry.location);
                    }
                });
                map.fitBounds(bounds);
        });
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places&callback=initMap" async defer></script>
</body>
</html>
'''

ARTISANS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Artisans - Incredible Explorer</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }
        .modal-content {
            position: relative;
            background-color: white;
            margin: 10% auto;
            padding: 20px;
            width: 80%;
            max-width: 600px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .close {
            position: absolute;
            right: 20px;
            top: 10px;
            font-size: 24px;
            cursor: pointer;
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="container mx-auto px-6 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <a href="/" class="flex items-center">
                        <div class="w-10 h-10 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 rounded-lg flex items-center justify-center transform rotate-45">
                            <i class="fas fa-compass text-white text-xl transform -rotate-45"></i>
                        </div>
                        <span class="ml-2 text-xl font-bold text-gray-800">Incredible Explorer</span>
                    </a>
                </div>
                <div class="flex items-center space-x-4">
                    <a href="/profile" class="text-gray-600 hover:text-gray-800">
                        <i class="fas fa-user-circle text-2xl"></i>
                    </a>
                    <a href="/logout" class="text-gray-600 hover:text-gray-800">
                        <i class="fas fa-sign-out-alt text-2xl"></i>
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <div class="container mx-auto px-6 py-8">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-indigo-900 mb-4">Meet Local Artisans</h1>
            <p class="text-gray-600">Connect with skilled artisans, learn about traditional crafts, and purchase authentic handmade products.</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {% for artisan in artisans %}
            <div class="bg-white rounded-xl shadow-md overflow-hidden">
                <div class="h-48 bg-gray-200 relative">
                    <img src="{{ artisan.image }}" alt="{{ artisan.name }}" class="w-full h-full object-cover">
                    <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
                        <h3 class="text-white font-bold text-xl">{{ artisan.name }}</h3>
                        <p class="text-white text-sm">{{ artisan.craft }}</p>
                            </div>
                            </div>
                <div class="p-6">
                    <div class="flex items-center mb-4">
                        <i class="fas fa-map-marker-alt text-gray-400 mr-2"></i>
                        <span class="text-gray-600">{{ artisan.location }}</span>
                        </div>
                    <p class="text-gray-600 mb-4">{{ artisan.description }}</p>
                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">Traditional Craft</span>
                        <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">Workshop Available</span>
                        <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full">Direct Purchase</span>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="openProfileModal('{{ artisan.id }}')" class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition flex items-center justify-center">
                            <i class="fas fa-user mr-2"></i> Profile
                        </button>
                        <button onclick="openMessageModal('{{ artisan.id }}')" class="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition flex items-center justify-center">
                            <i class="fas fa-envelope mr-2"></i> Message
                        </button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- Profile Modal -->
    <div id="profileModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('profileModal')">&times;</span>
            <div id="profileContent">
                <!-- Profile content will be loaded here -->
            </div>
        </div>
    </div>

    <!-- Message Modal -->
    <div id="messageModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('messageModal')">&times;</span>
            <h2 class="text-2xl font-bold mb-4">Send Message</h2>
            <form id="messageForm" class="space-y-4">
                <input type="hidden" id="messageArtisanId">
                <div>
                    <label class="block text-gray-700 mb-2">Message</label>
                    <textarea id="messageText" class="w-full px-3 py-2 border rounded-lg" rows="4" required></textarea>
                </div>
                <button type="submit" class="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition">
                    Send Message
                </button>
            </form>
        </div>
    </div>

    <!-- Purchase Modal -->
    <div id="purchaseModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('purchaseModal')">&times;</span>
            <h2 class="text-2xl font-bold mb-4">Purchase Crafts</h2>
            <div id="craftsList" class="space-y-4">
                <!-- Crafts will be loaded here -->
            </div>
            <div class="mt-6">
                <button onclick="proceedToCheckout()" class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition">
                    Proceed to Checkout
                </button>
            </div>
        </div>
    </div>

    <!-- Schedule Meeting Modal -->
    <div id="scheduleModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('scheduleModal')">&times;</span>
            <h2 class="text-2xl font-bold mb-4">Schedule Meeting</h2>
            <form id="scheduleForm" class="space-y-4">
                <input type="hidden" id="scheduleArtisanId">
                <div>
                    <label class="block text-gray-700 mb-2">Date</label>
                    <input type="date" id="meetingDate" class="w-full px-3 py-2 border rounded-lg" required>
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">Time</label>
                    <input type="time" id="meetingTime" class="w-full px-3 py-2 border rounded-lg" required>
                </div>
                <div>
                    <label class="block text-gray-700 mb-2">Meeting Type</label>
                    <select id="meetingType" class="w-full px-3 py-2 border rounded-lg" required>
                        <option value="workshop">Workshop</option>
                        <option value="consultation">Consultation</option>
                        <option value="demonstration">Demonstration</option>
                    </select>
                </div>
                <button type="submit" class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition">
                    Schedule Meeting
                </button>
            </form>
        </div>
    </div>

    <script>
        let currentArtisanId = null;
        let cart = [];

        function openProfileModal(artisanId) {
            currentArtisanId = artisanId;
            const modal = document.getElementById('profileModal');
            const content = document.getElementById('profileContent');
            
            fetch(`/api/artisans/${artisanId}`)
                .then(response => response.json())
                .then(artisan => {
                    content.innerHTML = `
                        <div class="space-y-6">
                            <div class="flex items-center space-x-4">
                                <img src="${artisan.image}" alt="${artisan.name}" class="w-24 h-24 rounded-full object-cover">
                                <div>
                                    <h3 class="text-2xl font-bold">${artisan.name}</h3>
                                    <p class="text-gray-600">${artisan.craft}</p>
                            </div>
                                    </div>
                            <div>
                                <h4 class="text-lg font-bold mb-2">About</h4>
                                <p class="text-gray-600">${artisan.description}</p>
                                </div>
                            <div>
                                <h4 class="text-lg font-bold mb-2">Location</h4>
                                <p class="text-gray-600">${artisan.location}</p>
                                </div>
                            <div class="flex space-x-2">
                                <button onclick="openMessageModal('${artisan.id}')" class="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
                                    <i class="fas fa-envelope mr-2"></i> Message
                                    </button>
                                <button onclick="openPurchaseModal('${artisan.id}')" class="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition">
                                    <i class="fas fa-shopping-bag mr-2"></i> Purchase
                                    </button>
                            </div>
                        </div>
                    `;
                });
        }

        function openMessageModal(artisanId) {
            document.getElementById('messageModal').classList.remove('hidden');
            document.getElementById('messageModal').classList.add('flex');
        }

        function closeMessageModal() {
            document.getElementById('messageModal').classList.add('hidden');
            document.getElementById('messageModal').classList.remove('flex');
        }

        function openPurchaseModal(artisanId) {
            document.getElementById('purchaseModal').classList.remove('hidden');
            document.getElementById('purchaseModal').classList.add('flex');
        }

        function closePurchaseModal() {
            document.getElementById('purchaseModal').classList.add('hidden');
            document.getElementById('purchaseModal').classList.remove('flex');
        }

        // Handle form submissions
        document.getElementById('messageForm').addEventListener('submit', function(e) {
            e.preventDefault();
            // Add your message sending logic here
            alert('Message sent successfully!');
            closeMessageModal();
        });

        document.getElementById('purchaseForm').addEventListener('submit', function(e) {
            e.preventDefault();
            // Add your purchase logic here
            alert('Order placed successfully!');
            closePurchaseModal();
        });
    </script>
</body>
</html>
'''

# Run the app
if __name__ == '__main__':
    # Create admin user if it doesn't exist
    if 'admin@incredibleexplorer.com' not in users:
        users['admin@incredibleexplorer.com'] = {
            'name': 'Admin',
            'password': generate_password_hash('admin123'),
            'profile': {
                'bio': 'Administrator account',
                'country': 'India',
                'favorite_spots': []
            },
            'created_at': datetime.now()
        }

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5005)