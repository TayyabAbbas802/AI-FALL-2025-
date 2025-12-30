# usda_service.py
import requests
from config import USDA_API_KEY


class USDAService:
    # USDA data types in order of preference (most reliable first)
    DATA_TYPES = [
        "SR Legacy",           # Standard Reference Legacy - most comprehensive
        "Foundation",          # Foundation Foods - detailed nutrient data
        "Survey (FNDDS)",      # Food and Nutrient Database for Dietary Studies
        "Branded"              # Branded foods - last resort
    ]
    
    @staticmethod
    def search_foods(query, max_results=10):
        """
        Search USDA FoodData Central API with improved accuracy.
        Uses multiple search strategies to ensure results for all cases.
        """
        if not query or not query.strip():
            return []

        # Clean the query
        cleaned_query = USDAService._clean_query(query)
        if not cleaned_query:
            return []

        # Try different search strategies in order of preference
        search_strategies = [
            # Strategy 1: Exact search with SR Legacy (most reliable)
            lambda: USDAService._search_with_params(
                cleaned_query, 
                max_results, 
                data_types=["SR Legacy"],
                require_all_words=True
            ),
            # Strategy 2: Search with Foundation foods
            lambda: USDAService._search_with_params(
                cleaned_query, 
                max_results, 
                data_types=["Foundation"],
                require_all_words=True
            ),
            # Strategy 3: Broader search with multiple data types
            lambda: USDAService._search_with_params(
                cleaned_query, 
                max_results, 
                data_types=["SR Legacy", "Foundation", "Survey (FNDDS)"],
                require_all_words=False
            ),
            # Strategy 4: Search all data types (including branded)
            lambda: USDAService._search_with_params(
                cleaned_query, 
                max_results, 
                data_types=None,  # All types
                require_all_words=False
            ),
            # Strategy 5: Simplified query (remove descriptors like "raw", "cooked")
            lambda: USDAService._search_with_params(
                USDAService._simplify_query(cleaned_query), 
                max_results, 
                data_types=None,
                require_all_words=False
            ),
        ]

        # Try each strategy until we get results
        for strategy in search_strategies:
            try:
                foods = strategy()
                if foods:
                    print(f"✅ Found {len(foods)} foods for '{query}'")
                    return foods
            except Exception as e:
                print(f"⚠️ Search strategy failed: {e}")
                continue

        print(f"❌ No results found for '{query}' after trying all strategies")
        return []

    @staticmethod
    def _search_with_params(query, max_results, data_types=None, require_all_words=True):
        """Execute a single search with specific parameters"""
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        
        params = {
            "api_key": USDA_API_KEY,
            "query": query,
            "pageSize": min(max_results * 2, 50),  # Get more to filter better
            "requireAllWords": require_all_words
        }
        
        # Add data types if specified
        if data_types:
            params["dataType"] = data_types

        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                foods = USDAService._parse_food_data(data, max_results)
                return foods
            elif response.status_code == 400:
                # Bad request - try without requireAllWords
                if require_all_words:
                    params["requireAllWords"] = False
                    response = requests.get(url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        return USDAService._parse_food_data(data, max_results)
            
            return []
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return []

    @staticmethod
    def _clean_query(query):
        """Clean and normalize search query"""
        if not query:
            return None

        # Remove extra whitespace
        cleaned = ' '.join(query.strip().split())
        
        # Minimum length check
        if len(cleaned) < 2:
            return None

        return cleaned

    @staticmethod
    def _simplify_query(query):
        """Simplify query by removing common descriptors"""
        # Remove common cooking methods and descriptors
        descriptors = [
            ', raw', ', cooked', ', boiled', ', baked', ', fried', 
            ', grilled', ', roasted', ', steamed', ', fresh', ', dried',
            'raw ', 'cooked ', 'boiled ', 'baked ', 'fried ',
            'grilled ', 'roasted ', 'steamed ', 'fresh ', 'dried '
        ]
        
        simplified = query.lower()
        for descriptor in descriptors:
            simplified = simplified.replace(descriptor, '')
        
        return simplified.strip()

    @staticmethod
    def _parse_food_data(response_data, max_results):
        """Parse USDA API response into structured food data"""
        foods = []
        seen_names = set()  # Avoid duplicates
        
        for food in response_data.get('foods', []):
            # Skip if no description
            description = food.get('description', '').strip()
            if not description:
                continue
            
            # Skip duplicates (case-insensitive)
            description_lower = description.lower()
            if description_lower in seen_names:
                continue
            
            # Extract nutrients
            nutrients = USDAService._extract_nutrients(food.get('foodNutrients', []))
            
            # Only include foods with meaningful nutrient data
            if not nutrients.get('calories') and not nutrients.get('protein'):
                continue
            
            # Add food to results
            foods.append({
                'name': description,
                'nutrients': nutrients,
                'fdcId': food.get('fdcId'),
                'dataType': food.get('dataType', 'Unknown')
            })
            
            seen_names.add(description_lower)
            
            # Stop if we have enough
            if len(foods) >= max_results:
                break
        
        return foods

    @staticmethod
    def _extract_nutrients(nutrients_list):
        """Extract and organize nutrient data with improved accuracy"""
        nutrients = {}
        
        # USDA nutrient IDs (most reliable method)
        nutrient_mapping = {
            1003: 'protein',      # Protein
            1004: 'fat',          # Total lipid (fat)
            1005: 'carbs',        # Carbohydrate, by difference
            1008: 'calories',     # Energy (kcal)
        }
        
        for nutrient in nutrients_list:
            nutrient_id = nutrient.get('nutrientId')
            nutrient_name = nutrient.get('nutrientName', '').lower()
            value = nutrient.get('value', 0)
            
            # Skip if no value
            if value is None or value == 0:
                continue
            
            # Try matching by nutrient ID first (most accurate)
            if nutrient_id in nutrient_mapping:
                key = nutrient_mapping[nutrient_id]
                if key == 'calories':
                    nutrients[key] = round(value, 0)
                else:
                    nutrients[key] = round(value, 1)
            
            # Fallback to name matching if ID didn't match
            elif 'protein' in nutrient_name and 'protein' not in nutrients:
                nutrients['protein'] = round(value, 1)
            elif 'carbohydrate' in nutrient_name and 'carbs' not in nutrients:
                nutrients['carbs'] = round(value, 1)
            elif ('total lipid' in nutrient_name or 'fat, total' in nutrient_name) and 'fat' not in nutrients:
                nutrients['fat'] = round(value, 1)
            elif 'energy' in nutrient_name and 'calories' not in nutrients:
                nutrients['calories'] = round(value, 0)
        
        # Ensure all keys exist with default 0 if not found
        for key in ['calories', 'protein', 'carbs', 'fat']:
            if key not in nutrients:
                nutrients[key] = 0
        
        return nutrients

    @staticmethod
    def categorize_food(food_name):
        """
        Categorize food into protein, carbs, vegetables, or fats
        based on its nutrient profile and name
        """
        name_lower = food_name.lower()
        nutrients = food_name  # This will be the food dict in actual use
        
        # Protein-rich foods
        protein_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'turkey',
            'egg', 'tofu', 'tempeh', 'seitan', 'lentil', 'bean', 'chickpea',
            'yogurt', 'cottage cheese', 'protein', 'meat', 'shrimp', 'crab',
            'lobster', 'duck', 'lamb', 'veal', 'venison'
        ]
        
        # Carb-rich foods
        carb_keywords = [
            'rice', 'pasta', 'bread', 'potato', 'sweet potato', 'yam',
            'oat', 'quinoa', 'barley', 'wheat', 'corn', 'cereal',
            'noodle', 'tortilla', 'bagel', 'muffin', 'cracker'
        ]
        
        # Vegetables
        vegetable_keywords = [
            'broccoli', 'spinach', 'kale', 'lettuce', 'tomato', 'cucumber',
            'pepper', 'carrot', 'celery', 'onion', 'garlic', 'mushroom',
            'zucchini', 'squash', 'cauliflower', 'cabbage', 'bok choy',
            'asparagus', 'green bean', 'pea', 'brussels sprout', 'eggplant'
        ]
        
        # Fats
        fat_keywords = [
            'oil', 'butter', 'avocado', 'nut', 'almond', 'walnut', 'cashew',
            'peanut', 'seed', 'olive', 'coconut', 'cheese', 'cream'
        ]
        
        # Check keywords
        if any(keyword in name_lower for keyword in protein_keywords):
            return 'proteins'
        elif any(keyword in name_lower for keyword in carb_keywords):
            return 'carbs'
        elif any(keyword in name_lower for keyword in vegetable_keywords):
            return 'vegetables'
        elif any(keyword in name_lower for keyword in fat_keywords):
            return 'fats'
        
        # Default to proteins if high protein, carbs if high carbs, etc.
        return 'proteins'  # Default category

    @staticmethod
    def validate_api_connection():
        """Test USDA API connection"""
        try:
            test_foods = USDAService.search_foods("apple", max_results=1)
            return len(test_foods) > 0
        except Exception:
            return False