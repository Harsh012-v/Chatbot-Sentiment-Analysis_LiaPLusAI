# Web Application Guide

## 🚀 Running the Web Application

### Quick Start

1. **Install Flask dependencies:**
   ```bash
   pip install flask flask-cors
   ```
   
   Or install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the web application:**
   ```bash
   python web_app.py
   ```

3. **Open your browser:**
   Navigate to: **http://localhost:5000**

## ✨ Features

### Modern Web Interface
- **Beautiful, modern UI** with gradient backgrounds and smooth animations
- **Real-time chat** with instant sentiment analysis
- **Responsive design** that works on desktop, tablet, and mobile
- **Dark theme** optimized for extended use

### Real-time Features
- **Live sentiment display** for each message
- **Emotion detection** with emoji indicators
- **Interactive analysis** sidebar
- **Conversation statistics** and trends

### Analysis Features
- **Overall sentiment** analysis
- **Trend analysis** showing mood progression
- **Emotion distribution** across conversation
- **Key insights** and statistics
- **Visual charts** (when available)

## 🎨 UI Highlights

- **Gradient backgrounds** for a modern look
- **Smooth animations** for message appearance
- **Color-coded sentiment** indicators (green/red/yellow)
- **Emoji indicators** for emotions
- **Modal dialogs** for detailed analysis
- **Responsive sidebar** for quick stats

## 📱 Usage

1. **Start chatting**: Type your message and press Enter or click Send
2. **View sentiment**: Each message shows real-time sentiment analysis
3. **End conversation**: Click the stop button to view full analysis
4. **Reset**: Click reset to start a new conversation
5. **View analysis**: Analysis appears in both sidebar and modal

## 🔧 Configuration

The web app uses the same configuration as the CLI version. Edit `config/config.yaml` to customize:
- Sentiment analyzer type
- Emotion detection
- Other features

## 🌐 API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send message and get response
- `POST /api/end_conversation` - End conversation and get analysis
- `POST /api/reset` - Reset conversation

## 📊 Data Persistence

Conversations are automatically saved to the `data/` directory in JSON format, just like the CLI version.

## 🎯 Differences from CLI

- **Web interface** instead of terminal
- **Real-time updates** without page refresh
- **Visual feedback** with animations
- **Modal dialogs** for analysis
- **Responsive design** for all devices

Enjoy your modern chatbot experience! 🚀

