# app.py
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from diet_chatbot import DietChatbot
from usda_service import USDAService
from gemini_service import GeminiService
from nutrition_calculator import NutritionCalculator
from config import validate_environment
import os
import traceback

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Initialize services
usda_service = USDAService()
gemini_service = GeminiService()
nutrition_calculator = NutritionCalculator()

# Cuisine options
CUISINE_OPTIONS = {
    'american': ['chicken breast', 'beef steak', 'potato', 'broccoli', 'cheese', 'eggs'],
    'italian': ['pasta', 'tomato', 'olive oil', 'basil', 'mozzarella', 'bread'],
    'mexican': ['beans', 'corn', 'avocado', 'tomato', 'pepper', 'rice'],
    'asian': ['rice', 'tofu', 'soy sauce', 'ginger', 'noodles', 'bok choy'],
    'chinese': ['rice', 'tofu', 'soy sauce', 'ginger', 'noodles', 'bok choy', 'chicken'],
    'indian': ['rice', 'lentils', 'chicken', 'yogurt', 'spinach', 'potato'],
    'mediterranean': ['olive oil', 'fish', 'tomato', 'cucumber', 'yogurt', 'chickpeas'],
    'vegetarian': ['tofu', 'lentils', 'beans', 'spinach', 'broccoli', 'nuts']
}

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/submit-info', methods=['POST'])
def submit_info():
    """Handle user information submission"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['age', 'weight', 'height', 'gender', 'activity_level', 'goal', 'cuisine_preference']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Store user data in session
        session['user_data'] = {
            'age': int(data['age']),
            'weight': float(data['weight']),
            'height': float(data['height']),
            'gender': data['gender'].lower(),
            'activity_level': data['activity_level'],
            'goal': data['goal'],
            'cuisine_preference': data['cuisine_preference'].lower(),
            'preferred_foods': CUISINE_OPTIONS.get(data['cuisine_preference'].lower(), [])
        }
        
        # Calculate macros
        user_data = session['user_data']
        bmr = nutrition_calculator.calculate_bmr(
            user_data['weight'],
            user_data['height'],
            user_data['age'],
            user_data['gender']
        )
        tdee = nutrition_calculator.calculate_tdee(bmr, user_data['activity_level'])
        target_calories = nutrition_calculator.calculate_target_calories(tdee, user_data['goal'])
        macros = nutrition_calculator.calculate_macros(target_calories, user_data['goal'])
        
        session['user_data']['macros'] = macros
        
        return jsonify({
            'success': True,
            'macros': macros,
            'message': 'User information saved successfully!'
        })
        
    except Exception as e:
        print(f"Error in submit_info: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/generate-plan', methods=['POST'])
def generate_plan():
    """Generate personalized diet plan"""
    try:
        if 'user_data' not in session:
            return jsonify({'success': False, 'error': 'Please submit your information first'}), 400
        
        user_data = session['user_data']
        
        # Gather available foods
        available_foods = gather_available_foods(user_data)
        
        # Generate plan using Gemini
        plan = gemini_service.generate_diet_plan(user_data, available_foods)
        
        return jsonify({
            'success': True,
            'plan': plan,
            'cuisine': user_data['cuisine_preference']
        })
        
    except Exception as e:
        print(f"Error in generate_plan: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/search-food', methods=['POST'])
def search_food():
    """Search for specific foods"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400
        
        foods = usda_service.search_foods(query, max_results=10)
        
        if not foods:
            return jsonify({'success': True, 'foods': [], 'message': 'No foods found'})
        
        return jsonify({
            'success': True,
            'foods': foods
        })
        
    except Exception as e:
        print(f"Error in search_food: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update-cuisine', methods=['POST'])
def update_cuisine():
    """Update cuisine preference"""
    try:
        if 'user_data' not in session:
            return jsonify({'success': False, 'error': 'Please submit your information first'}), 400
        
        data = request.json
        cuisine = data.get('cuisine', '').lower()
        
        if cuisine not in CUISINE_OPTIONS:
            return jsonify({'success': False, 'error': 'Invalid cuisine option'}), 400
        
        session['user_data']['cuisine_preference'] = cuisine
        session['user_data']['preferred_foods'] = CUISINE_OPTIONS[cuisine]
        
        return jsonify({
            'success': True,
            'message': f'Cuisine updated to {cuisine.title()}',
            'cuisine': cuisine
        })
        
    except Exception as e:
        print(f"Error in update_cuisine: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get-macros', methods=['GET'])
def get_macros():
    """Get current user macros"""
    try:
        if 'user_data' not in session or 'macros' not in session['user_data']:
            return jsonify({'success': False, 'error': 'No user data found'}), 400
        
        return jsonify({
            'success': True,
            'macros': session['user_data']['macros']
        })
        
    except Exception as e:
        print(f"Error in get_macros: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

def gather_available_foods(user_data):
    """Gather available foods from USDA database based on cuisine preference"""
    preferred_foods = user_data['preferred_foods']
    cuisine = user_data['cuisine_preference']
    
    print(f"🔍 Searching USDA database for {cuisine.title()} cuisine foods...")
    
    available_foods = {
        'proteins': [],
        'carbs': [],
        'vegetables': [],
        'fats': []
    }
    
    # Search for each preferred food
    for food_term in preferred_foods:
        found_foods = usda_service.search_foods(food_term, max_results=3)
        
        if found_foods:
            # Categorize each food based on its name and nutrient profile
            for food in found_foods:
                category = categorize_food_by_nutrients(food)
                if category and len(available_foods[category]) < 6:  # Limit per category
                    available_foods[category].append(food)
    
    # Ensure we have at least some foods in each category
    # Add universal healthy options if needed
    universal_foods = {
        'proteins': ['chicken breast', 'eggs', 'salmon', 'tofu', 'greek yogurt'],
        'carbs': ['brown rice', 'oats', 'quinoa', 'sweet potato', 'whole wheat bread'],
        'vegetables': ['spinach', 'broccoli', 'tomatoes', 'bell peppers', 'carrots'],
        'fats': ['olive oil', 'almonds', 'avocado', 'walnuts', 'peanut butter']
    }
    
    for category, food_list in universal_foods.items():
        if len(available_foods[category]) < 3:  # Need at least 3 per category
            for food_term in food_list:
                if len(available_foods[category]) >= 5:  # Max 5 per category
                    break
                
                # Skip if we already have this food
                existing_names = [f['name'].lower() for f in available_foods[category]]
                if any(food_term in name for name in existing_names):
                    continue
                
                found_foods = usda_service.search_foods(food_term, max_results=1)
                if found_foods:
                    available_foods[category].extend(found_foods)
    
    # Print summary
    total_foods = sum(len(foods) for foods in available_foods.values())
    print(f"✅ Found {total_foods} foods for {cuisine.title()} cuisine:")
    for category, foods in available_foods.items():
        print(f"   • {category.title()}: {len(foods)} options")
    
    return available_foods


def categorize_food_by_nutrients(food):
    """
    Categorize food based on its nutrient profile and name.
    Returns: 'proteins', 'carbs', 'vegetables', or 'fats'
    """
    name_lower = food['name'].lower()
    nutrients = food.get('nutrients', {})
    
    # Get nutrient values (per 100g)
    protein = nutrients.get('protein', 0)
    carbs = nutrients.get('carbs', 0)
    fat = nutrients.get('fat', 0)
    calories = nutrients.get('calories', 0)
    
    # Keyword-based categorization (most reliable for edge cases)
    protein_keywords = [
        'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey', 'duck',
        'egg', 'tofu', 'tempeh', 'seitan', 'lentil', 'bean', 'chickpea', 'pea',
        'yogurt', 'cottage cheese', 'protein', 'meat', 'shrimp', 'crab', 'lobster',
        'lamb', 'veal', 'venison', 'bison', 'quail', 'sardine', 'mackerel'
    ]
    
    carb_keywords = [
        'rice', 'pasta', 'bread', 'potato', 'sweet potato', 'yam', 'oat', 'oatmeal',
        'quinoa', 'barley', 'wheat', 'corn', 'cereal', 'noodle', 'spaghetti',
        'tortilla', 'bagel', 'muffin', 'cracker', 'couscous', 'bulgur', 'farro'
    ]
    
    vegetable_keywords = [
        'broccoli', 'spinach', 'kale', 'lettuce', 'tomato', 'cucumber', 'pepper',
        'carrot', 'celery', 'onion', 'garlic', 'mushroom', 'zucchini', 'squash',
        'cauliflower', 'cabbage', 'bok choy', 'asparagus', 'green bean', 'brussels',
        'eggplant', 'radish', 'beet', 'turnip', 'arugula', 'chard', 'collard'
    ]
    
    fat_keywords = [
        'oil', 'butter', 'avocado', 'nut', 'almond', 'walnut', 'cashew', 'pecan',
        'peanut', 'seed', 'olive', 'coconut', 'cheese', 'cream', 'mayo', 'ghee'
    ]
    
    # Check keywords first (most reliable)
    if any(keyword in name_lower for keyword in protein_keywords):
        return 'proteins'
    elif any(keyword in name_lower for keyword in carb_keywords):
        return 'carbs'
    elif any(keyword in name_lower for keyword in vegetable_keywords):
        return 'vegetables'
    elif any(keyword in name_lower for keyword in fat_keywords):
        return 'fats'
    
    # Fallback to nutrient profile if keywords don't match
    if calories > 0:
        # Calculate percentage of calories from each macro
        protein_cal_pct = (protein * 4) / calories if calories > 0 else 0
        carbs_cal_pct = (carbs * 4) / calories if calories > 0 else 0
        fat_cal_pct = (fat * 9) / calories if calories > 0 else 0
        
        # Categorize based on dominant macronutrient
        if protein_cal_pct > 0.3:  # More than 30% from protein
            return 'proteins'
        elif fat_cal_pct > 0.5:  # More than 50% from fat
            return 'fats'
        elif carbs_cal_pct > 0.4:  # More than 40% from carbs
            return 'carbs'
        elif carbs < 10 and calories < 50:  # Low carb, low calorie = vegetable
            return 'vegetables'
    
    # Default to proteins if we can't determine
    return 'proteins'


if __name__ == '__main__':
    try:
        validate_environment()
        print("✅ Starting Diet Chatbot Web Application...")
        print("🌐 Open your browser and navigate to: http://localhost:5001")
        app.run(debug=True, host='0.0.0.0', port=5001)
    except EnvironmentError as e:
        print(f"❌ Configuration Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
