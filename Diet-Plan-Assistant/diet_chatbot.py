# diet_chatbot.py
from usda_service import USDAService
from gemini_service import GeminiService
from nutrition_calculator import NutritionCalculator


class DietChatbot:
    def __init__(self):
        self.user_data = {}
        self.usda_service = USDAService()
        self.gemini_service = GeminiService()
        self.nutrition_calculator = NutritionCalculator()

        # Define cuisine options with corresponding USDA search terms
        self.cuisine_options = {
            'american': ['chicken breast', 'beef steak', 'potato', 'broccoli', 'cheese', 'eggs'],
            'italian': ['pasta', 'tomato', 'olive oil', 'basil', 'mozzarella', 'bread'],
            'mexican': ['beans', 'corn', 'avocado', 'tomato', 'pepper', 'rice'],
            'asian': ['rice', 'tofu', 'soy sauce', 'ginger', 'noodles', 'bok choy'],
            'chinese': ['rice', 'tofu', 'soy sauce', 'ginger', 'noodles', 'bok choy', 'chicken'],
            'indian': ['rice', 'lentils', 'chicken', 'yogurt', 'spinach', 'potato'],
            'mediterranean': ['olive oil', 'fish', 'tomato', 'cucumber', 'yogurt', 'chickpeas'],
            'vegetarian': ['tofu', 'lentils', 'beans', 'spinach', 'broccoli', 'nuts']
        }

    def collect_user_info(self):
        """Collect basic user information"""
        print("\n🤖 Hi! I'm your Diet Plan Assistant. Let's create your personalized plan!\n")

        self.user_data['age'] = int(input("Your age (years): "))
        self.user_data['weight'] = float(input("Your weight (kg): "))
        self.user_data['height'] = float(input("Your height (cm): "))
        self.user_data['gender'] = input("Gender (male/female): ").lower()
        self.user_data['activity_level'] = self._get_activity_level()
        self.user_data['goal'] = self._get_goal()

        # Calculate macros
        self._calculate_user_macros()
        self._display_targets()
        self.collect_cuisine_preference()

    def collect_cuisine_preference(self):
        """Collect user's cuisine preference"""
        print("\n🍽️ What type of cuisine do you prefer?")
        print("Available options:")
        for i, cuisine in enumerate(self.cuisine_options.keys(), 1):
            print(f"{i}. {cuisine.title()}")

        print("\nExamples: american, italian, mexican, asian, chinese, indian, mediterranean, vegetarian")

        while True:
            cuisine_pref = input("\nEnter your preferred cuisine: ").lower().strip()

            if cuisine_pref in self.cuisine_options:
                self.user_data['cuisine_preference'] = cuisine_pref
                self.user_data['preferred_foods'] = self.cuisine_options[cuisine_pref]
                print(f"✅ Selected {cuisine_pref.title()} cuisine")
                break
            else:
                print("❌ Invalid cuisine. Please choose from the available options.")
                print("Available: " + ", ".join(self.cuisine_options.keys()))

    def _get_activity_level(self):
        """Get and validate activity level"""
        print("\nActivity levels:")
        print("1. Sedentary (little/no exercise)")
        print("2. Light (1-3 days/week)")
        print("3. Moderate (3-5 days/week)")
        print("4. Active (6-7 days/week)")
        print("5. Very Active (athlete)")

        activity_choice = input("\nChoose activity level (1-5): ")
        activity_map = {
            '1': 'sedentary', '2': 'light', '3': 'moderate',
            '4': 'active', '5': 'very_active'
        }
        return activity_map.get(activity_choice, 'moderate')

    def _get_goal(self):
        """Get and validate goal"""
        print("\nGoals:")
        print("1. Weight Loss")
        print("2. Muscle Gain")
        print("3. Maintenance")

        goal_choice = input("\nChoose your goal (1-3): ")
        goal_map = {'1': 'weight_loss', '2': 'muscle_gain', '3': 'maintenance'}
        return goal_map.get(goal_choice, 'maintenance')

    def _calculate_user_macros(self):
        """Calculate user macros based on collected data"""
        bmr = self.nutrition_calculator.calculate_bmr(
            self.user_data['weight'],
            self.user_data['height'],
            self.user_data['age'],
            self.user_data['gender']
        )
        tdee = self.nutrition_calculator.calculate_tdee(bmr, self.user_data['activity_level'])
        target_calories = self.nutrition_calculator.calculate_target_calories(tdee, self.user_data['goal'])
        self.user_data['macros'] = self.nutrition_calculator.calculate_macros(target_calories, self.user_data['goal'])

    def _display_targets(self):
        """Display calculated targets"""
        print("\n" + "=" * 60)
        print("📊 YOUR DAILY TARGETS")
        print("=" * 60)
        print(f"Calories: {self.user_data['macros']['calories']} kcal")
        print(f"Protein:  {self.user_data['macros']['protein_g']}g")
        print(f"Carbs:    {self.user_data['macros']['carbs_g']}g")
        print(f"Fats:     {self.user_data['macros']['fats_g']}g")
        print("=" * 60 + "\n")

    def _gather_available_foods(self):
        """Gather available foods from USDA database based on cuisine preference"""
        preferred_foods = self.user_data['preferred_foods']
        cuisine = self.user_data['cuisine_preference']

        print(f"\n🔍 Searching USDA database for {cuisine.title()} cuisine foods...")

        available_foods = {
            'proteins': [],
            'carbs': [],
            'vegetables': [],
            'fats': []
        }

        # Search for each preferred food and categorize them
        for food in preferred_foods:
            found_foods = self.usda_service.search_foods(food, max_results=2)
            if found_foods:
                # Categorize the food
                if any(term in food for term in ['chicken', 'beef', 'fish', 'tofu', 'lentils', 'beans', 'yogurt']):
                    available_foods['proteins'].extend(found_foods)
                elif any(term in food for term in ['rice', 'pasta', 'bread', 'potato', 'corn', 'oats']):
                    available_foods['carbs'].extend(found_foods)
                elif any(term in food for term in
                         ['broccoli', 'spinach', 'tomato', 'cucumber', 'pepper', 'avocado', 'bok choy']):
                    available_foods['vegetables'].extend(found_foods)
                elif any(term in food for term in ['olive oil', 'cheese', 'nuts', 'avocado']):
                    available_foods['fats'].extend(found_foods)

        # Add some universal healthy options to ensure we have enough data
        universal_foods = {
            'proteins': ['chicken breast', 'eggs', 'tofu'],
            'carbs': ['rice', 'potato', 'oats'],
            'vegetables': ['spinach', 'broccoli', 'carrots'],
            'fats': ['olive oil', 'almonds', 'avocado']
        }

        for category, foods in universal_foods.items():
            if len(available_foods[category]) < 2:  # If we don't have enough in this category
                for food in foods:
                    if len(available_foods[category]) >= 4:  # Limit to 4 per category
                        break
                    found_foods = self.usda_service.search_foods(food, max_results=1)
                    if found_foods and found_foods[0] not in available_foods[category]:
                        available_foods[category].extend(found_foods)

        # Validate that we have enough food data
        total_foods = sum(len(foods) for foods in available_foods.values())
        if total_foods == 0:
            raise Exception("Failed to fetch food data from USDA. Please check your connection and try again.")

        # Print summary
        print(f"\n📊 Found {total_foods} food items for {cuisine.title()} cuisine")
        for category, foods in available_foods.items():
            print(f"   {category.title()}: {len(foods)} options")

        return available_foods

    def generate_diet_plan(self):
        """Generate diet plan with USDA data validation"""
        try:
            available_foods = self._gather_available_foods()

            print("\n⏳ Generating your personalized diet plan...\n")
            plan = self.gemini_service.generate_diet_plan(self.user_data, available_foods)
            return plan

        except Exception as e:
            return f"Error generating diet plan: {e}"

    def get_food_suggestions(self, query):
        """Get food suggestions from USDA database"""
        foods = self.usda_service.search_foods(query)
        if not foods:
            return "No foods found for that preference."

        suggestion = f"\n🍽️ Food options for '{query}':\n\n"
        for i, food in enumerate(foods, 1):
            nutrients = food['nutrients']
            suggestion += f"{i}. {food['name']}\n"
            if nutrients:
                suggestion += f"   Calories: {nutrients.get('calories', 'N/A')} kcal | "
                suggestion += f"Protein: {nutrients.get('protein', 'N/A')}g | "
                suggestion += f"Carbs: {nutrients.get('carbs', 'N/A')}g | "
                suggestion += f"Fat: {nutrients.get('fat', 'N/A')}g\n\n"
        return suggestion

    def run(self):
        """Main chatbot loop"""
        self.collect_user_info()

        while True:
            print("\n💬 What would you like to do?")
            print("1. Get complete diet plan")
            print("2. Search for specific foods")
            print("3. View my targets again")
            print("4. Update cuisine preference")
            print("5. Exit")

            choice = input("\nYour choice (1-5): ")

            if choice == '1':
                plan = self.generate_diet_plan()
                print(plan)
            elif choice == '2':
                food_pref = input("\n🔍 What food would you like to search for? ")
                suggestions = self.get_food_suggestions(food_pref)
                print(suggestions)
            elif choice == '3':
                self._display_targets()
            elif choice == '4':
                self.collect_cuisine_preference()
                print("\n✅ Cuisine preference updated!")
            elif choice == '5':
                print("\n👋 Thanks for using Diet Plan Chatbot! Stay healthy!\n")
                break
            else:
                print("Invalid choice. Please try again.")