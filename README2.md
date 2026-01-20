# FaultyHermes - AI Real-Time Translation Chat

This project is a real-time chat application built with **Django Channels** and **Gemini 3 Flash AI**. It automatically translates messages into the recipient's target language in real-time.

## Features

- **Real-Time Messaging**: Powered by Django Channels (WebSockets).
- **AI Translation**: Uses Gemini-3-Flash-Preview to translate messages on the fly.
- **Dynamic Language Detection**: Fetches the recipient's preferred language (English, Spanish, French) from their profile.
- **English Shadow Bubbles**: Always provides an English translation below the foreign text for learning context.
- **Color-Coded Chat**: Blue bubbles for sent messages, Green for received translations.
- **In-Memory Channel Layer**: Optimized for local development (no Redis required).

## Installation & Setup

### 1. Requirements
Ensure you have Python 3.10+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install google-genai channels daphne
```

### 3. API Key Configuration
The AI translation requires a Gemini API Key. 
1. Create a `.env` file in the root directory (based on `.env.template`).
2. Add your key: `GEMINI_API_KEY=your_actual_key_here`.
3. The server uses `os.environ.get('GEMINI_API_KEY')` to load it.

**NEVER** hardcode or commit keys to the repository.

### 4. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Server
```bash
python manage.py runserver
```

## How It Works

### The Backend (`consumers.py`)
1.  **Connection**: When two users connect, they are placed in a unique "Group" based on their usernames.
2.  **Reception**: When User A sends a message, the `receive` method:
    - Fetches User B's preferred language.
    - Calls Gemini AI to translate the message.
    - Saves the original and translated text to the database.
3.  **Broadcast**: The server sends a JSON object to everyone in the group containing the `message`, `translated` text, and `sender`.

### The Frontend (`room.html`)
- **Sender**: Sees the original message they typed (Blue bubble).
- **Receiver**: Sees the AI-translated version (Green bubble).
- **Shadow Bubble**: Both users see an English translation below the main text to help with learning.
- **Input**: Supports the **Enter** key for quick messaging.

## Troubleshooting

- **WSL vs Windows**: If editing on Windows but running in WSL, remember to sync your files:
  ```bash
  cp /mnt/c/PATH_TO_PROJECT/chat/consumers.py ~/PATH_TO_PROJECT/chat/consumers.py
  ```
- **Static Files**: If colors are missing, ensure `chat/static/css/style.css` exists and is correctly copied.
- **AI Error**: If the terminal shows `[AI ERROR]`, check your API key and internet connection. The chat will fallback to the original text if translation fails.
