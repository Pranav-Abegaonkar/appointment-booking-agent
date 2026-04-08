import React, { useState } from 'react';
import { Phone, ArrowLeft, Heart, Calendar, MessageCircle, Star, Shield, Users } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

import axios from 'axios';

const VIDEOSDK_PREBUILT_URL = "https://embed.videosdk.live/rtc-js-prebuilt/0.3.43/?name=Pavan&meetingId=mbp0-ug28-4roy&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlrZXkiOiI1NjFiNjlkYS0yYTJhLTQ1NDctODNhMi0xMDEwYTk2Y2U1YzciLCJwZXJtaXNzaW9ucyI6WyJhbGxvd19qb2luIiwiYWxsb3dfbW9kIl0sImlhdCI6MTc3NTA1MjQyOSwiZXhwIjoxODA2NTg4NDI5fQ.yv1QAxWyfG3swG-Kg-q-K1k6tKHYOsNkhj96igvjD_g";
const API_URL = "http://localhost:8000";

const App: React.FC = () => {
  const [isCalling, setIsCalling] = useState(false);

  const startCall = async () => {
    try {
      // 1. Invoke the AI Agent into the room via the backend
      await axios.post(`${API_URL}/start-agent?room_id=mbp0-ug28-4roy`);

      // 2. Open the UI to join the room
      setIsCalling(true);
    } catch (error) {
      console.error("Failed to start agent:", error);
      // Fallback: still open UI but agent might not join automatically
      setIsCalling(true);
    }
  };

  return (
    <div className="app-container">
      <AnimatePresence mode="wait">
        {!isCalling ? (
          <motion.div
            key="start-screen"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="hero-section"
          >
            <div className="header-logo">
              <Heart size={48} color="#e74c3c" fill="#e74c3c" />
            </div>
            <h1>Talk Your Heart Out</h1>
            <p>Your journey to emotional well-being starts with a conversation. Speak with Anushka, our AI care coordinator, to book your therapy session — online or in-person in Singapore.</p>

            <div className="card-container">
              <div className="feature-grid">
                <div className="feature-item">
                  <Calendar size={24} color="#8e44ad" />
                  <h3>Book a Therapy Session</h3>
                  <p>Schedule with qualified therapists — CBT, EMDR, DBT, and more.</p>
                </div>
                <div className="feature-item">
                  <MessageCircle size={24} color="#8e44ad" />
                  <h3>Empathetic Matching</h3>
                  <p>Anushka understands your concerns and matches you with the right therapist.</p>
                </div>
                <div className="feature-item">
                  <Users size={24} color="#8e44ad" />
                  <h3>For Everyone</h3>
                  <p>Individuals, couples, families, children & adolescents.</p>
                </div>
                <div className="feature-item">
                  <Shield size={24} color="#8e44ad" />
                  <h3>Private & Confidential</h3>
                  <p>Your information is never shared without your consent.</p>
                </div>
              </div>

              <button className="call-button" onClick={startCall}>
                <Phone size={24} />
                Schedule Your Therapy Session
              </button>

              <div className="status-indicator">
                <div className="pulse"></div>
                Anushka is available to help you right now
              </div>
            </div>

            <div className="footer-stats">
              <div className="stat-item">
                <Star size={16} fill="#f1c40f" color="#f1c40f" />
                <span>All therapists hold a Master's degree or higher</span>
              </div>
              <div className="stat-item">
                <span>Online & In-Person Sessions</span>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="call-screen"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="iframe-container"
          >
            <button className="back-button" onClick={() => setIsCalling(false)}>
              <ArrowLeft size={18} />
              Return to Dashboard
            </button>
            <iframe 
              src={VIDEOSDK_PREBUILT_URL} 
              allow="camera; microphone; fullscreen; display-capture; autoplay"
              title="Appointment Call"
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default App;
