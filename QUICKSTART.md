# Quick Start Guide

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the chatbot:**
   ```bash
   python main.py
   ```

## Basic Usage

1. Start the chatbot - it will display a welcome message
2. Type your messages and press Enter
3. See real-time sentiment analysis for each message
4. Type `quit`, `exit`, or `bye` to end the conversation
5. View comprehensive sentiment analysis report

## Configuration

Edit `config/config.yaml` to customize:

- **Sentiment Analyzer**: Change `sentiment.analyzer_type` to `vader`, `textblob`, or `transformers`
- **Emotion Detection**: Set `features.emotion_detection: true` to enable
- **Visualization**: Set `features.visualization: true` to generate charts
- **Export Format**: Change `data.export_format` to `json`, `csv`, or `both`

## Testing

Install pytest first:
```bash
pip install pytest pytest-cov
```

Then run tests:
```bash
pytest tests/ -v
```

## Troubleshooting

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- If using transformers, install: `pip install transformers torch`

### No Colors in Terminal
- Install colorama: `pip install colorama`
- On Windows, colors should work automatically
- On Linux/Mac, ensure terminal supports ANSI colors

### Visualization Not Working
- Install matplotlib: `pip install matplotlib`
- Charts are saved to `data/` directory

## Example Conversation

```
You: Hello
💭 Sentiment: Positive (+0.44)
Bot: Hello! I'm here to help. How can I assist you today?

You: I'm frustrated
💭 Sentiment: Negative (-0.65)
Bot: I'm really sorry to hear that. I understand this is frustrating...

You: quit
[Shows comprehensive analysis]
```

