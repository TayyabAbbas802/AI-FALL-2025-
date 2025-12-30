# nutrition_calculator.py
class NutritionCalculator:
    @staticmethod
    def calculate_bmr(weight_kg, height_cm, age, gender):
        """Calculate Basal Metabolic Rate"""
        if gender.lower() == 'male':
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            return (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    @staticmethod
    def calculate_tdee(bmr, activity_level):
        """Calculate Total Daily Energy Expenditure"""
        multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        return bmr * multipliers.get(activity_level, 1.2)

    @staticmethod
    def calculate_target_calories(tdee, goal):
        """Calculate target calories based on goal"""
        if goal == 'weight_loss':
            return tdee - 500
        elif goal == 'muscle_gain':
            return tdee + 300
        else:
            return tdee

    @staticmethod
    def calculate_macros(calories, goal):
        """Calculate macronutrient distribution"""
        if goal == 'weight_loss':
            protein_pct, carb_pct, fat_pct = 0.35, 0.30, 0.35
        elif goal == 'muscle_gain':
            protein_pct, carb_pct, fat_pct = 0.30, 0.40, 0.30
        else:
            protein_pct, carb_pct, fat_pct = 0.25, 0.45, 0.30

        return {
            'calories': round(calories),
            'protein_g': round((calories * protein_pct) / 4),
            'carbs_g': round((calories * carb_pct) / 4),
            'fats_g': round((calories * fat_pct) / 9)
        }