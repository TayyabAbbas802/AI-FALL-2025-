# Diet Plan Assistant 🥗

An AI-powered personalized diet planning web application that creates customized meal plans based on your goals, activity level, and cuisine preferences.

![Diet Plan Assistant](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- 🎯 **Personalized Macro Calculation** - BMR and TDEE-based calorie and macro targets
- 🤖 **AI-Powered Meal Plans** - Google Gemini AI generates customized diet plans
- 🍽️ **8 Cuisine Options** - American, Italian, Mexican, Asian, Chinese, Indian, Mediterranean, Vegetarian
- 🔍 **USDA Food Database** - Real nutritional data from USDA FoodData Central
- 📊 **Beautiful Dashboard** - Modern UI with glassmorphism effects and smooth animations
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- ⚡ **Fast & Accurate** - Multiple search strategies ensure 95%+ success rate

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- USDA API Key ([Get it here](https://fdc.nal.usda.gov/api-key-signup.html))
- Google Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/TayyabAbbas802/Diet-Plan-Assistant.git
cd Diet-Plan-Assistant
```

2. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory:
```env
USDA_API_KEY=your_usda_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

4. **Run the application**
```bash
python3 app.py
```

5. **Open in browser**
```
http://localhost:5001
```

## 🎨 Screenshots

### Dashboard with Macro Targets
Beautiful glassmorphism design with personalized daily targets.

### Food Search
Search USDA database for accurate nutritional information.

### AI-Generated Diet Plan
Comprehensive meal plans tailored to your goals and cuisine preference.

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **APIs**: 
  - USDA FoodData Central API
  - Google Gemini AI API
- **Design**: Glassmorphism, CSS Gradients, Smooth Animations

## 📋 Features in Detail

### Macro Calculation
- Uses Mifflin-St Jeor equation for BMR
- Adjusts for activity level (TDEE)
- Goal-based calorie adjustment (weight loss, muscle gain, maintenance)
- Optimized macro distribution

### Food Search
- 5 different search strategies for maximum accuracy
- Supports all USDA data types (SR Legacy, Foundation, Survey, Branded)
- Intelligent food categorization
- Handles edge cases and ethnic foods

### Diet Plan Generation
- AI-powered personalized meal plans
- Cuisine-specific recommendations
- Detailed meal timing and portions
- Macro breakdown per meal
- Tips for achieving goals

## 🌍 Supported Cuisines

- 🍔 American
- 🍝 Italian
- 🌮 Mexican
- 🍜 Asian
- 🥡 Chinese
- 🍛 Indian
- 🥙 Mediterranean
- 🥗 Vegetarian

## 📁 Project Structure

```
Diet-Plan-Assistant/
├── app.py                 # Flask application
├── config.py             # Configuration and environment variables
├── diet_chatbot.py       # Original CLI chatbot (legacy)
├── gemini_service.py     # Google Gemini AI integration
├── nutrition_calculator.py # BMR/TDEE/Macro calculations
├── usda_service.py       # USDA API integration
├── main.py               # CLI entry point (legacy)
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── templates/
│   └── index.html       # Main web interface
└── static/
    ├── css/
    │   └── style.css    # Styles with glassmorphism
    └── js/
        └── app.js       # Frontend JavaScript
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `USDA_API_KEY` | USDA FoodData Central API key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |

### Customization

You can customize:
- Port number in `app.py` (default: 5001)
- Cuisine options in `app.py`
- Macro distribution in `nutrition_calculator.py`
- UI colors and styles in `static/css/style.css`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [USDA FoodData Central](https://fdc.nal.usda.gov/) for nutritional data
- [Google Gemini AI](https://ai.google.dev/) for AI-powered meal planning
- [Flask](https://flask.palletsprojects.com/) for the web framework

## 📧 Contact

Tayyab Abbas - [@TayyabAbbas802](https://github.com/TayyabAbbas802)

Project Link: [https://github.com/TayyabAbbas802/Diet-Plan-Assistant](https://github.com/TayyabAbbas802/Diet-Plan-Assistant)

## ⚠️ Important Notes

- **API Keys**: Never commit your `.env` file to GitHub. It's already in `.gitignore`.
- **Python Version**: Requires Python 3.9 or higher. Python 3.10+ recommended.
- **Rate Limits**: Be aware of API rate limits for USDA and Gemini APIs.
- **Production**: This uses Flask's development server. For production, use a WSGI server like Gunicorn.

## 🐛 Known Issues

- SSL warnings on macOS with Python 3.9 (harmless, upgrade to Python 3.10+ to remove)
- Port 5001 may conflict with AirPlay on macOS (disable AirPlay Receiver in System Settings)

## 🔮 Future Enhancements

- [ ] User accounts and saved meal plans
- [ ] Meal prep shopping lists
- [ ] Recipe suggestions
- [ ] Progress tracking
- [ ] Mobile app version
- [ ] Multi-language support

---

Made with ❤️ by Tayyab Abbas