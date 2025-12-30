# main.py
from config import validate_environment
from diet_chatbot import DietChatbot

def main():
    try:
        validate_environment()
        chatbot = DietChatbot()
        chatbot.run()
    except EnvironmentError as e:
        print(f"❌ Configuration Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()