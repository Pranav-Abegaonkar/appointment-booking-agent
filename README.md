# Appointment Booking Agent

This project is a real-time AI-powered appointment booking system using VideoSDK, FastAPI, and React. It features an AI agent that can join video calls, interact with participants using voice (TTS/STT), and manage appointments via Google Calendar.

## 🚀 Features

- **Real-time Voice Interaction**: AI agent with low-latency STT (Deepgram/Google) and TTS (Cartesia/SarvamAI/OpenAI).
- **Video Call Integration**: Built on top of VideoSDK for seamless multi-party video conferencing.
- **Smart Scheduling**: Integration with Google Calendar for booking and managing appointments.
- **Modern UI**: React-based frontend with Framer Motion for smooth animations.

---

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.9+**
- **Node.js 18+**
- **npm** or **yarn**

You will also need API keys for:
- [VideoSDK](https://app.videosdk.live/api-keys)
- [OpenAI](https://platform.openai.com/)
- [Deepgram](https://console.deepgram.com/)
- [Cartesia](https://cartesia.ai/) (Optional)
- [SarvamAI](https://www.sarvam.ai/) (Optional)
- [Google Cloud Console](https://console.cloud.google.com/) (For Calendar API)

---

## 📦 Setup

### 1. Clone the repository
```bash
git clone https://github.com/Pranav-Abegaonkar/appointment-booking-agent.git
cd appointment-booking-agent
```

### 2. Configure Environment Variables
Copy the example environment file and fill in your API keys:
```bash
cp .env.example scheduling_app/agent/.env
```
Edit `scheduling_app/agent/.env` with your actual credentials.

### 3. Backend Setup (Python)
Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 4. Frontend Setup (React/Vite)
Install Node dependencies:
```bash
cd scheduling_app/frontend
npm install
cd ../..
```

---

## 🏃 Driving the Application

You need to run both the backend and frontend simultaneously.

### 1. Start the Backend
From the root directory:
```bash
# Ensure your venv is activated
uvicorn scheduling_app.backend.app:app --reload
```
The backend will be running at `http://localhost:8000`.

### 2. Start the Frontend
In a new terminal:
```bash
cd scheduling_app/frontend
npm run dev
```
The frontend will be running at `http://localhost:5173`.

---

## 🔑 Google Calendar Setup
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Google Calendar API**.
3. Create **OAuth 2.0 Client IDs** and download the JSON file.
4. Rename the file to something simple or update `GOOGLE_OAUTH_CLIENT_SECRET_JSON` in your `.env`.
5. Ensure the path in `.env` points to this JSON file.

---

## 🤖 How It Works
1. **Frontend**: The user joins a VideoSDK room.
2. **Backend**: Provide a token and room creation API for the frontend.
3. **Agent**: When triggered (via `/start-agent`), the Python backend spawns an AI agent process that joins the same VideoSDK room using the credentials provided in `.env`.
4. **Interaction**: The agent listens to the audio stream, processes it via LLMs (OpenAI), and responds using TTS.

---

## 📄 License
This project is licensed under the MIT License.
