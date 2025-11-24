# Chatbot with Sentiment Analysis - Production-Ready MVP

A production-ready Python chatbot application that conducts intelligent conversations with users and performs comprehensive sentiment analysis at both conversation and statement levels. Built with modular architecture, comprehensive error handling, and extensive testing.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Technology Stack](#technology-stack)
- [Sentiment Logic Explanation](#sentiment-logic-explanation)
- [Architecture Overview](#architecture-overview)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Bonus Features](#bonus-features)
- [Future Enhancements](#future-enhancements)
- [Screenshots/Examples](#screenshotsexamples)

## 🎯 Project Overview

This chatbot application demonstrates production-ready software engineering practices while providing:

- **Intelligent Conversations**: Context-aware, empathetic chatbot responses
- **Real-time Sentiment Analysis**: Per-message sentiment evaluation (Tier 2)
- **Conversation-Level Analysis**: Overall sentiment assessment (Tier 1)
- **Trend Analysis**: Sentiment progression tracking throughout conversations
- **Data Persistence**: Automatic conversation logging and export
- **Visualization**: Real-time sentiment trend charts
- **Emotion Detection**: Specific emotion identification (joy, anger, sadness, etc.)

## ✨ Features

### Tier 1 - Conversation-Level Sentiment Analysis (Mandatory) ✅

- ✅ Maintains complete conversation history throughout the interaction
- ✅ Generates comprehensive sentiment analysis for the entire conversation at the end
- ✅ Provides clear indication of overall emotional direction with detailed reasoning
- ✅ Calculates average sentiment scores and label distribution

### Tier 2 - Statement-Level Sentiment Analysis (Additional Credit) ✅

- ✅ Performs sentiment evaluation for every user message individually
- ✅ Displays each message alongside its sentiment output in real-time
- ✅ Tracks sentiment changes throughout the conversation
- ✅ **Enhancement**: Summarizes trend or shift in mood across the conversation
- ✅ Identifies key emotional moments and significant sentiment shifts
- ✅ Provides sentiment distribution statistics

### Bonus Features 🎁

1. **Real-time Sentiment Visualization** 📊
   - Generates sentiment trend charts using matplotlib
   - Visual representation of mood progression
   - Exports charts as PNG images

2. **Emotion Detection** 😊😢😠
   - Detects specific emotions beyond positive/negative
   - Identifies: joy, sadness, anger, fear, surprise, disgust
   - Emotion distribution analysis across conversations

3. **Export Reports** 📄
   - Detailed text reports with full conversation analysis
   - CSV export for data analysis
   - JSON export for programmatic access

4. **Multi-Analyzer Support** 🔄
   - Strategy pattern implementation
   - Support for VADER, TextBlob, and Transformers (Hugging Face)
   - Easy switching between analyzers via configuration

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Step-by-Step Setup

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd chatbot-sentiment-mvp
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**
   ```bash
   python -c "import vaderSentiment; print('VADER installed successfully')"
   ```

### Optional Dependencies

For advanced sentiment analysis using Transformers:
```bash
pip install transformers torch
```

Then update `config/config.yaml` to use `analyzer_type: transformers`

## 📖 Usage Guide

### Basic Usage

1. **Start the chatbot**
   ```bash
   python main.py
   ```

2. **Begin chatting**
   - Type your messages and press Enter
   - The bot will respond contextually
   - Real-time sentiment is displayed for each message (Tier 2)

3. **End the conversation**
   - Type one of: `quit`, `exit`, `bye`, `goodbye`
   - The application will display comprehensive sentiment analysis

### Example Conversation

```
=== Sentiment Analysis Chatbot ===

Bot: Hello! I'm Assistant. I'm here to chat with you.
     Type 'quit', 'exit', or 'bye' to end the conversation.

You: Hello
💭 Sentiment: Positive (+0.44)
Bot: Hello! I'm here to help. How can I assist you today?

You: Your service disappoints me
💭 Sentiment: Negative (-0.73)
Bot: I'm really sorry to hear that. I understand this is frustrating. 
     Can you tell me more about what went wrong?

You: Actually, my last experience was much better
💭 Sentiment: Positive (+0.52)
Bot: I'm glad your previous experience was positive. What made it better?

You: quit

=== Conversation Analysis ===

📊 Total Messages: 3
⏱️  Duration: 45.2 seconds

📈 Sentiment Trend: Started Positive → Shifted Negative → Improved Positive
   (improved from -0.11 to +0.08)

⚖️  Overall Sentiment: NEUTRAL
   Mixed conversation with balanced sentiment (1/3 neutral messages)

🔍 Key Insights:
   - Conversation mood improved over time
   - Detected 2 significant sentiment shift(s)
   - Balanced mix of positive and negative messages

💾 Conversation saved to: data/chat_20241123_153045.json
📊 Sentiment visualization saved to: data/sentiment_trend_chat_20241123_153045.png
📄 Detailed report saved to: data/report_chat_20241123_153045.txt
```

### Configuration

Edit `config/config.yaml` to customize:

- Sentiment analyzer type (vader, textblob, transformers)
- Chatbot name and personality
- UI settings (colors, timestamps)
- Feature toggles
- Data export formats

## 🛠 Technology Stack

### Core Technologies

- **Python 3.9+**: Primary programming language
- **VADER Sentiment Analyzer**: Default sentiment analysis engine
  - Lexicon and rule-based sentiment analysis
  - Optimized for social media and conversational text
  - Provides compound scores from -1.0 to +1.0
  - Fast and efficient for real-time analysis

### Alternative Analyzers

- **TextBlob**: Simple and effective sentiment analysis
- **Transformers (Hugging Face)**: State-of-the-art accuracy using pre-trained models
  - Model: `distilbert-base-uncased-finetuned-sst-2-english`
  - Requires: `transformers` and `torch` packages

### Supporting Libraries

- **colorama**: Colored terminal output
- **matplotlib**: Sentiment trend visualization
- **pyyaml**: Configuration file management
- **pytest**: Testing framework
- **rich**: Enhanced terminal formatting (optional)

### Why These Technologies?

1. **VADER**: Works excellently with short, conversational text without requiring training
2. **Strategy Pattern**: Allows easy switching between analyzers
3. **Modular Design**: Clean separation of concerns for maintainability
4. **Type Hints**: Improved code clarity and IDE support
5. **Comprehensive Logging**: Production-ready error tracking

## 🧠 Sentiment Logic Explanation

### Sentiment Scoring

The sentiment analyzer uses different scoring mechanisms based on the selected analyzer:

#### VADER (Default)
- **Compound Score**: Ranges from -1.0 (most negative) to +1.0 (most positive)
- Combines individual word sentiment scores with grammatical cues
- Accounts for punctuation, capitalization, and degree modifiers
- Provides separate positive, neutral, and negative scores

#### TextBlob
- **Polarity Score**: Ranges from -1.0 to +1.0
- **Subjectivity Score**: Ranges from 0.0 (objective) to 1.0 (subjective)
- Based on pattern analysis

#### Transformers
- **Confidence Score**: Probability of positive/negative classification
- Uses deep learning model fine-tuned on sentiment analysis
- Highest accuracy but requires more resources

### Sentiment Classification

- **Positive**: Score ≥ 0.05 (VADER) or > 0.1 (TextBlob)
- **Negative**: Score ≤ -0.05 (VADER) or < -0.1 (TextBlob)
- **Neutral**: Score between thresholds

### Conversation-Level Analysis (Tier 1)

1. Collects all user messages from the conversation
2. Analyzes each message individually
3. Calculates average sentiment score
4. Determines overall sentiment label based on average
5. Generates human-readable reasoning based on:
   - Average score
   - Label distribution (positive/negative/neutral counts)
   - Message count

### Statement-Level Analysis (Tier 2)

1. Analyzes each user message in real-time
2. Displays sentiment label and score immediately
3. Stores sentiment data with each message
4. Enables trend analysis across the conversation

### Trend Analysis

1. **Splits conversation into halves**
2. **Compares averages**:
   - First half average vs. second half average
3. **Determines trend**:
   - **Improving**: Second half > First half + threshold
   - **Declining**: First half > Second half + threshold
   - **Stable**: Difference < threshold
4. **Identifies key moments**:
   - Significant sentiment shifts (>0.3 change)
   - Extreme sentiment values (>0.7 absolute)
5. **Calculates volatility**: Standard deviation of sentiment scores

## 🏗 Architecture Overview

### Design Patterns

- **Strategy Pattern**: Sentiment analyzers (VADER, TextBlob, Transformers)
- **Factory Pattern**: Analyzer creation based on configuration
- **Observer Pattern**: Real-time sentiment display

### Module Structure

```
src/
├── sentiment.py      # Sentiment analysis engine with Strategy pattern
├── conversation.py   # Conversation management and persistence
├── chatbot.py        # Chatbot logic and response generation
├── analyzer.py       # Trend analysis and insights
├── emotion.py        # Emotion detection (bonus feature)
└── utils.py          # Utility functions (logging, validation, I/O)
```

### Data Flow

1. **User Input** → Validation & Sanitization
2. **Sentiment Analysis** → Real-time per-message analysis (Tier 2)
3. **Chatbot Response** → Context-aware, empathetic response generation
4. **Conversation Storage** → Message history with timestamps
5. **End Analysis** → Overall sentiment + Trend analysis (Tier 1)
6. **Export** → JSON/CSV/Report generation

### Key Components

- **SentimentEngine**: Orchestrates sentiment analysis with configurable analyzers
- **Conversation**: Manages message history, timestamps, and persistence
- **Chatbot**: Generates contextual responses based on sentiment and history
- **TrendAnalyzer**: Analyzes sentiment progression and identifies key moments
- **ChatbotApp**: Main application orchestrator with CLI interface

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_sentiment.py

# Run with verbose output
pytest -v tests/
```

### Test Coverage

The test suite includes:

- ✅ Sentiment analysis accuracy (positive/negative/neutral detection)
- ✅ Conversation history management
- ✅ Edge cases (empty inputs, special characters, long texts)
- ✅ Trend analysis calculations
- ✅ Chatbot response generation
- ✅ Data persistence (save/load)

### Expected Coverage

Target: **70%+ code coverage**

```bash
pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html to view coverage report
```

## 📁 Project Structure

```
chatbot-sentiment-mvp/
├── src/
│   ├── __init__.py
│   ├── sentiment.py          # Sentiment analysis engine
│   ├── conversation.py       # Conversation management
│   ├── chatbot.py            # Chatbot response logic
│   ├── analyzer.py           # Trend analysis
│   ├── emotion.py            # Emotion detection (bonus)
│   └── utils.py              # Helper functions
├── tests/
│   ├── __init__.py
│   ├── test_sentiment.py     # Sentiment analysis tests
│   ├── test_conversation.py  # Conversation management tests
│   ├── test_chatbot.py       # Chatbot logic tests
│   └── test_analyzer.py      # Trend analysis tests
├── config/
│   └── config.yaml           # Configuration file
├── data/                     # Conversation logs (auto-generated)
│   ├── *.json                # Conversation data
│   ├── *.csv                 # CSV exports
│   ├── *.png                 # Sentiment visualizations
│   └── *.txt                 # Detailed reports
├── logs/                     # Application logs (optional)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore                # Git ignore rules
└── main.py                   # Entry point
```

## 🎁 Bonus Features

### 1. Real-time Sentiment Visualization

- Generates matplotlib charts showing sentiment progression
- Visual representation of mood changes
- Exported as PNG images in the `data/` directory
- Automatically created at conversation end

### 2. Emotion Detection

- Detects specific emotions: joy, sadness, anger, fear, surprise, disgust
- Keyword-based detection with sentiment score refinement
- Emotion distribution analysis
- Primary emotion identification per message

### 3. Export Reports

- **Text Reports**: Comprehensive analysis in readable format
- **CSV Export**: Structured data for analysis
- **JSON Export**: Programmatic access to conversation data
- All exports include timestamps, sentiment scores, and metadata

### 4. Multi-Analyzer Support

- Easy switching between VADER, TextBlob, and Transformers
- Configuration-based analyzer selection
- Consistent interface across all analyzers

## 🔮 Future Enhancements

- [ ] Multi-language support with automatic language detection
- [ ] Web interface using Flask/FastAPI
- [ ] Database storage for conversation history
- [ ] Real-time sentiment graph during conversation (live updating)
- [ ] PDF report generation
- [ ] Conversation comparison across multiple sessions
- [ ] Customizable chatbot personality profiles
- [ ] Integration with LLM APIs (OpenAI, Anthropic) for more intelligent responses
- [ ] Advanced NLP features (entity recognition, topic modeling)
- [ ] User authentication and conversation history per user

## 📸 Screenshots/Examples

### Example Output Format

```
=== Sentiment Analysis Chatbot ===

Bot: Hello! I'm Assistant. I'm here to chat with you.

You: I'm really frustrated with this product
💭 Sentiment: Negative (-0.65)
Bot: I'm really sorry to hear that. I understand this is frustrating. 
     Can you tell me more about what went wrong?

You: The customer service was terrible
💭 Sentiment: Negative (-0.84)
Bot: I'm sorry to hear that. Can you provide more details so I can assist you better?

You: But the product itself is actually good
💭 Sentiment: Positive (+0.49)
Bot: I'm glad to hear that! Is there anything else I can help with?

You: quit

=== Conversation Analysis ===

📊 Total Messages: 3
⏱️  Duration: 1.2 minutes

📈 Sentiment Trend: Started Negative → Remained Negative → Improved Positive
   (improved from -0.75 to -0.33)

⚖️  Overall Sentiment: NEGATIVE
   Generally negative conversation with 2/3 negative messages

🔍 Key Insights:
   - Conversation mood improved over time
   - Detected 1 significant sentiment shift(s)
   - Predominantly negative messages (2/3)

💾 Conversation saved to: data/chat_20241123_153045.json
📊 Sentiment visualization saved to: data/sentiment_trend_chat_20241123_153045.png
📄 Detailed report saved to: data/report_chat_20241123_153045.txt
```

## 📝 License

This project is created for educational purposes as part of the LiaPlus Assignment.

## 👤 Author

Built with production-ready best practices, comprehensive testing, and modular architecture.

---

**Status**: ✅ Tier 1 Fully Implemented | ✅ Tier 2 Fully Implemented | ✅ Bonus Features Included
