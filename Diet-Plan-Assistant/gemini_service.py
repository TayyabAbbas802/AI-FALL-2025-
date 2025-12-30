# gemini_service.py
import google.generativeai as genai
from config import GEMINI_API_KEY, MODEL_NAME


class GeminiService:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)

    def generate_diet_plan(self, user_data, available_foods):
        """Generate diet plan using USDA food data"""
        prompt = self._build_prompt(user_data, available_foods)

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating plan: {e}"

    def _build_prompt(self, user_data, available_foods):
        """Build the prompt for Gemini"""
        cuisine = user_data['cuisine_preference']

        return f"""You are a professional nutritionist. Create a {cuisine.title()} cuisine daily meal plan using ONLY the foods listed below from the USDA database.

**CRITICAL RULES:**
1. Use ONLY foods from the lists below - DO NOT make up or suggest foods not in these lists
2. Calculate portions to match the client's macro targets
3. Use exact food names from the lists
4. Show portion sizes in grams
5. Create meals in {cuisine.title()} cuisine style

**Client Profile:**
- Age: {user_data['age']} years
- Weight: {user_data['weight']} kg
- Height: {user_data['height']} cm
- Gender: {user_data['gender']}
- Activity Level: {user_data['activity_level']}
- Goal: {user_data['goal']}
- Preferred Cuisine: {cuisine.title()}

**Daily Targets:**
- Calories: {user_data['macros']['calories']} kcal
- Protein: {user_data['macros']['protein_g']}g
- Carbohydrates: {user_data['macros']['carbs_g']}g
- Fats: {user_data['macros']['fats_g']}g

**Available Foods from USDA Database:**
{self._format_all_foods(available_foods)}

Create a complete daily {cuisine.title()} cuisine meal plan with:
1. Breakfast (with timing, foods from lists above, and portion sizes in grams)
2. Morning Snack (if needed)
3. Lunch (with timing, foods from lists above, and portion sizes in grams)
4. Afternoon Snack (if needed)
5. Dinner (with timing, foods from lists above, and portion sizes in grams)

For each meal:
- List exact food names from above lists
- Show portion size in grams
- Calculate total macros for that meal
- Make it authentic to {cuisine.title()} cuisine

End with 3 tips for achieving their goal with {cuisine.title()} cuisine.

Remember: Use ONLY foods from the lists above. Do not suggest any foods not listed."""

    def _format_all_foods(self, available_foods):
        """Format all food categories for the prompt"""
        formatted = []

        for category, foods in available_foods.items():
            if foods:
                formatted.append(f"\n**{category.upper()}:**")
                formatted.append(self._format_food_list(foods))

        return '\n'.join(formatted)

    def _format_food_list(self, foods):
        """Format food list for the prompt"""
        formatted = []
        for food in foods[:8]:  # Limit to 8 foods per category
            nutrients = food['nutrients']
            formatted.append(
                f"- {food['name']}: "
                f"{nutrients.get('calories', 0)} kcal, "
                f"{nutrients.get('protein', 0)}g protein, "
                f"{nutrients.get('carbs', 0)}g carbs, "
                f"{nutrients.get('fat', 0)}g fat"
            )
        return '\n'.join(formatted) if formatted else "No foods available"