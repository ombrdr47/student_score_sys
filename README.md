# Communication Skills Scoring Tool

##  Project Overview

An AI-powered tool that analyzes and scores students' spoken communication skills based on transcript text. The tool combines rule-based methods, NLP-based semantic scoring, and data-driven rubric evaluation to produce comprehensive feedback on self-introduction exercises.

##  Scoring System

The tool evaluates transcripts across **5 major criteria** with a total score of 0-100:

### 1. Content & Structure (40 points)
- **Salutation Level (5 points)**: Quality of greeting
  - Excellent (5): "I am excited to introduce", "feeling great"
  - Good (4): "Good morning/afternoon/evening", "Hello everyone"
  - Normal (2): "Hi", "Hello"
  - None (0): No salutation
  
- **Keyword Presence (30 points)**:
  - Must-have keywords (20 pts, 4 each): Name, Age, School/Class, Family, Hobbies/Interests
  - Good-to-have keywords (10 pts, 2 each): Family details, Origin, Ambition/Goal, Fun fact, Strengths
  
- **Flow (5 points)**: Proper structure order
  - Salutation → Basic Details → Additional Details → Closing

### 2. Speech Rate (10 points)
- Calculated as Words Per Minute (WPM)
- Ideal (10): 111-140 WPM
- Slow/Fast (6): 81-110 or 141-160 WPM
- Too Slow/Fast (2): <80 or >160 WPM

### 3. Language & Grammar (20 points)
- **Grammar Errors (10 points)**: Using LanguageTool Python library
  - Score = 1 - min(errors_per_100_words / 10, 1)
  
- **Vocabulary Richness (10 points)**: Type-Token Ratio (TTR)
  - TTR = Unique Words / Total Words
  - ≥0.9 (10 pts), 0.7-0.89 (8 pts), 0.5-0.69 (6 pts), etc.

### 4. Clarity (15 points)
- **Filler Word Rate**: Detects um, uh, like, you know, so, actually, basically, right, etc.
- 0-3% (15 pts), 4-6% (12 pts), 7-9% (9 pts), 10-12% (6 pts), 13%+ (3 pts)

### 5. Engagement (15 points)
- **Sentiment/Positivity**: Using VADER sentiment analysis
- Positive score ≥0.9 (15 pts), 0.7-0.89 (12 pts), 0.5-0.69 (9 pts), etc.

##  NLP & AI Components

### Rule-Based Methods
- Keyword matching for required elements
- Pattern detection for salutations and closings
- Word count and structure analysis

### NLP-Based Scoring
- **Semantic Similarity**: Uses sentence-transformers (all-MiniLM-L6-v2) to compute cosine similarity between transcript and ideal criterion descriptions
- **Grammar Analysis**: LanguageTool for detecting grammatical errors
- **Sentiment Analysis**: VADER for positivity scoring

### Data-Driven Weighting
- Weighted scoring based on rubric specifications
- Normalized final score (0-100)
- Per-criterion detailed feedback

##  Technology Stack

### Backend
- **Flask**: Web framework
- **sentence-transformers**: Semantic similarity (NLP)
- **language-tool-python**: Grammar checking
- **vaderSentiment**: Sentiment analysis
- **PyTorch**: Deep learning backend

### Frontend
- **HTML/CSS/JavaScript**: Simple, responsive UI
- **Vanilla JS**: No framework dependencies
- Gradient design with real-time results

##  Project Structure

```
Assignment/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Frontend UI
├── static/                     # (for additional assets)
├── README.md                   # This file
├── DEPLOYMENT.md              # Deployment instructions
└── case_study.md              # Rubric and sample data
```

##  Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/ombrdr47/student_score_sys
cd student_score_sys
```

### Step 2: Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: First-time installation will download:
- Sentence transformer model (~80MB)
- LanguageTool Java components (~200MB)
- This may take 5-10 minutes

### Step 4: Run the Application
```bash
python app.py
```

The server will start at `http://localhost:5001`

##  Usage

### Web Interface
1. Open browser and navigate to `http://localhost:5001`
2. Paste or type transcript in the text area
3. (Optional) Enter duration in seconds for accurate WPM calculation
4. Click "Score Transcript" button
5. View detailed results with overall score and per-criterion breakdown

### API Usage

#### Score Transcript Endpoint
```bash
POST /api/score
Content-Type: application/json

{
  "transcript": "Hello everyone, myself Om...",
  "duration_sec": 52  
}
```

#### Response Format
```json
{
  "overall_score": 86.0,
  "word_count": 142,
  "sentence_count": 11,
  "criteria": [
    {
      "name": "Content & Structure",
      "score": 29,
      "max_score": 40,
      "weight_percentage": 40,
      "details": [...],
      "semantic_similarity": 0.75
    },
    ...
  ]
}
```

#### Health Check
```bash
GET /api/health
```

##  Testing with Sample Data

The application includes a sample transcript from the rubric:

**Sample Transcript**: Muskan's self-introduction (142 words, 11 sentences, 52 seconds)

**Expected Score**: ~86/100

To test:
1. Click "Load Sample" button in the UI
2. Click "Score Transcript"
3. Verify scores match expected values

##  API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web interface |
| POST | `/api/score` | Score transcript |
| GET | `/api/health` | Health check |

### Request Schema
```json
{
  "transcript": "string (required)",
  "duration_sec": "number (optional)"
}
```

### Response Schema
```json
{
  "overall_score": "number (0-100)",
  "word_count": "number",
  "sentence_count": "number",
  "criteria": [
    {
      "name": "string",
      "score": "number",
      "max_score": "number",
      "weight_percentage": "number",
      "details": [...],
      "semantic_similarity": "number (0-1)"
    }
  ]
}
```

---

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

For questions or issues, please create an issue in the repository.
