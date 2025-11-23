from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
from collections import Counter
import language_tool_python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)
CORS(app)

try:
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
except:
    semantic_model = None
    
try:
    grammar_tool = language_tool_python.LanguageTool('en-US')
except:
    grammar_tool = None
    
sentiment_analyzer = SentimentIntensityAnalyzer()


class TranscriptScorer:
    def __init__(self):
        self.salutation_keywords = {
            'no_salutation': [],
            'normal': ['hi', 'hello'],
            'good': ['good morning', 'good afternoon', 'good evening', 'good day', 'hello everyone'],
            'excellent': ['excited to introduce', 'feeling great', 'i am excited', 'excited to']
        }
        
        self.must_have_keywords = {
            'name': ['name', 'myself', 'i am', "i'm", 'call me'],
            'age': ['years old', 'age', 'year old'],
            'school_class': ['class', 'grade', 'school', 'studying'],
            'family': ['family', 'mother', 'father', 'brother', 'sister', 'parents', 'siblings'],
            'hobbies': ['hobby', 'hobbies', 'enjoy', 'like', 'love', 'play', 'playing', 'interest']
        }
        
        self.good_to_have_keywords = {
            'about_family': ['kind', 'loving', 'caring', 'supportive', 'special thing about'],
            'origin': ['from', 'born', 'live in', 'belong'],
            'ambition': ['want to', 'dream', 'goal', 'ambition', 'aspire', 'become'],
            'unique': ['fun fact', 'unique', 'interesting', 'special'],
            'strengths': ['strength', 'achievement', 'good at', 'proud']
        }
        
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'so', 'actually', 'basically', 
            'right', 'i mean', 'well', 'kinda', 'sort of', 'okay', 'hmm', 'ah'
        ]
        
        self.flow_order = {
            'salutation': ['hi', 'hello', 'good morning', 'good afternoon', 'good evening', 'hello everyone'],
            'basic_details': ['name', 'myself', 'age', 'class', 'school'],
            'closing': ['thank you', 'thanks', 'thank']
        }

    def count_words_sentences(self, text):
        """Count words and sentences"""
        if not text or not text.strip():
            return 0, 0
        words = re.findall(r'\b\w+\b', text.lower())
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return len(words), len(sentences)

    def score_salutation(self, text):
        """Score salutation level (0-5 points)"""
        text_lower = text.lower()
        
        for keyword in self.salutation_keywords['excellent']:
            if keyword in text_lower:
                return 5, "Excellent salutation detected", "Excellent"
        
        for keyword in self.salutation_keywords['good']:
            if keyword in text_lower:
                return 4, "Good salutation detected", "Good"
        
        for keyword in self.salutation_keywords['normal']:
            if keyword in text_lower:
                return 2, "Basic salutation detected", "Normal"
        
        return 0, "No salutation detected", "None"

    def score_keyword_presence(self, text):
        """Score keyword presence - Must-have (20) + Good-to-have (10) = 30 points"""
        text_lower = text.lower()
        must_have_score = 0
        good_to_have_score = 0
        found_keywords = []
        
        for category, keywords in self.must_have_keywords.items():
            found = False
            for keyword in keywords:
                if keyword in text_lower:
                    found = True
                    found_keywords.append(f"{category}: {keyword}")
                    break
            if found:
                must_have_score += 4
        
        for category, keywords in self.good_to_have_keywords.items():
            found = False
            for keyword in keywords:
                if keyword in text_lower:
                    found = True
                    found_keywords.append(f"{category}: {keyword}")
                    break
            if found:
                good_to_have_score += 2
        
        total_score = min(must_have_score, 20) + min(good_to_have_score, 10)
        feedback = f"Found {len(found_keywords)} key elements. Keywords: {', '.join(found_keywords[:10])}"
        
        return total_score, feedback

    def score_flow(self, text):
        """Score flow/structure (0-5 points)"""
        text_lower = text.lower()
        sentences = re.split(r'[.!?]+', text_lower)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        has_salutation_first = False
        if sentences:
            for sal in self.flow_order['salutation']:
                if sal in sentences[0]:
                    has_salutation_first = True
                    break
        
        has_basic_early = False
        if len(sentences) > 1:
            first_third = ' '.join(sentences[:max(1, len(sentences)//3)])
            for detail in self.flow_order['basic_details']:
                if detail in first_third:
                    has_basic_early = True
                    break
        
        has_closing = False
        if sentences:
            last_sentence = sentences[-1]
            for closing in self.flow_order['closing']:
                if closing in last_sentence:
                    has_closing = True
                    break
        
        if has_salutation_first and has_basic_early and has_closing:
            return 5, "Good flow: Salutation → Details → Closing"
        elif has_basic_early:
            return 3, "Partial flow: Some structure present"
        else:
            return 0, "Flow not followed"

    def score_speech_rate(self, text, duration_sec=None):
        """Score speech rate (0-10 points)"""
        word_count, _ = self.count_words_sentences(text)
        
        if duration_sec is None:
            duration_sec = word_count / 2.0
        
        wpm = (word_count / duration_sec) * 60
        
        if 111 <= wpm <= 140:
            score = 10
            feedback = f"Ideal speech rate: {wpm:.1f} WPM"
        elif (81 <= wpm <= 110) or (141 <= wpm <= 160):
            score = 6
            feedback = f"{'Slow' if wpm < 111 else 'Fast'} speech rate: {wpm:.1f} WPM"
        elif wpm > 160 or wpm < 81:
            score = 2
            feedback = f"{'Too fast' if wpm > 160 else 'Too slow'} speech rate: {wpm:.1f} WPM"
        else:
            score = 10
            feedback = f"Speech rate: {wpm:.1f} WPM"
        
        return score, feedback, wpm

    def score_grammar(self, text):
        """Score grammar (0-10 points) using LanguageTool"""
        if not grammar_tool:
            return 8, "Grammar check unavailable", 0
        
        word_count, _ = self.count_words_sentences(text)
        matches = grammar_tool.check(text)
        error_count = len(matches)
        
        errors_per_100 = (error_count / max(word_count, 1)) * 100
        grammar_score_calc = 1 - min(errors_per_100 / 10, 1)
        
        if grammar_score_calc >= 0.9:
            score = 10
        elif grammar_score_calc >= 0.7:
            score = 8
        elif grammar_score_calc >= 0.5:
            score = 6
        elif grammar_score_calc >= 0.3:
            score = 4
        else:
            score = 2
        
        feedback = f"{error_count} grammar errors detected ({errors_per_100:.1f} per 100 words)"
        return score, feedback, error_count

    def score_vocabulary_richness(self, text):
        """Score vocabulary richness using TTR (0-10 points)"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words or len(words) == 0:
            return 0, "No words found", 0
        
        unique_words = len(set(words))
        total_words = len(words)
        ttr = unique_words / max(total_words, 1)
        
        if ttr >= 0.9:
            score = 10
        elif ttr >= 0.7:
            score = 8
        elif ttr >= 0.5:
            score = 6
        elif ttr >= 0.3:
            score = 4
        else:
            score = 2
        
        feedback = f"TTR: {ttr:.2f} ({unique_words} unique / {total_words} total words)"
        return score, feedback, ttr

    def score_filler_words(self, text):
        """Score filler word rate (0-15 points)"""
        text_lower = text.lower()
        word_count, _ = self.count_words_sentences(text)
        
        if word_count == 0:
            return 0, "No words to analyze", 0
        
        filler_count = 0
        found_fillers = []
        for filler in self.filler_words:
            count = text_lower.count(filler)
            if count > 0:
                filler_count += count
                found_fillers.append(f"{filler}({count})")
        
        filler_rate = (filler_count / max(word_count, 1)) * 100
        
        if filler_rate <= 3:
            score = 15
        elif filler_rate <= 6:
            score = 12
        elif filler_rate <= 9:
            score = 9
        elif filler_rate <= 12:
            score = 6
        else:
            score = 3
        
        feedback = f"{filler_count} filler words ({filler_rate:.1f}%). Found: {', '.join(found_fillers[:5])}"
        return score, feedback, filler_rate

    def score_sentiment(self, text):
        """Score sentiment/engagement (0-15 points) using VADER"""
        sentiment_scores = sentiment_analyzer.polarity_scores(text)
        positive_score = sentiment_scores['pos']
        
        if positive_score >= 0.9:
            score = 15
        elif positive_score >= 0.7:
            score = 12
        elif positive_score >= 0.5:
            score = 9
        elif positive_score >= 0.3:
            score = 6
        else:
            score = 3
        
        feedback = f"Positive sentiment: {positive_score:.2f}"
        return score, feedback, positive_score

    def calculate_semantic_similarity(self, text, criterion_description):
        """Calculate semantic similarity between text and criterion"""
        if not semantic_model:
            return 0.5
        
        try:
            text_embedding = semantic_model.encode(text, convert_to_tensor=True)
            criterion_embedding = semantic_model.encode(criterion_description, convert_to_tensor=True)
            similarity = util.cos_sim(text_embedding, criterion_embedding).item()
            return max(0, min(1, similarity))
        except:
            return 0.5

    def score_transcript(self, text, duration_sec=None):
        """Main scoring function"""
        # Handle empty or invalid input
        if not text or not text.strip():
            return {
                "error": "Empty transcript",
                "overall_score": 0,
                "word_count": 0,
                "sentence_count": 0,
                "criteria": []
            }
        
        word_count, sentence_count = self.count_words_sentences(text)
        
        salutation_score, salutation_feedback, salutation_level = self.score_salutation(text)
        keyword_score, keyword_feedback = self.score_keyword_presence(text)
        flow_score, flow_feedback = self.score_flow(text)
        content_structure_total = salutation_score + keyword_score + flow_score
        
        speech_rate_score, speech_rate_feedback, wpm = self.score_speech_rate(text, duration_sec)
        
        grammar_score, grammar_feedback, error_count = self.score_grammar(text)
        vocab_score, vocab_feedback, ttr = self.score_vocabulary_richness(text)
        language_grammar_total = grammar_score + vocab_score
        
        filler_score, filler_feedback, filler_rate = self.score_filler_words(text)
        
        sentiment_score, sentiment_feedback, positive_score = self.score_sentiment(text)
        
        semantic_scores = {}
        if semantic_model:
            semantic_scores['content'] = self.calculate_semantic_similarity(
                text, 
                "self introduction with name age school family hobbies interests"
            )
            semantic_scores['engagement'] = self.calculate_semantic_similarity(
                text,
                "enthusiastic positive confident grateful energetic"
            )
            semantic_scores['clarity'] = self.calculate_semantic_similarity(
                text,
                "clear articulate well-spoken fluent"
            )
        
        total_score = (content_structure_total + speech_rate_score + 
                      language_grammar_total + filler_score + sentiment_score)
        
        result = {
            "overall_score": round(total_score, 2),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "criteria": [
                {
                    "name": "Content & Structure",
                    "score": content_structure_total,
                    "max_score": 40,
                    "weight_percentage": 40,
                    "details": [
                        {
                            "metric": "Salutation Level",
                            "score": salutation_score,
                            "max_score": 5,
                            "feedback": salutation_feedback,
                            "level": salutation_level
                        },
                        {
                            "metric": "Keyword Presence",
                            "score": keyword_score,
                            "max_score": 30,
                            "feedback": keyword_feedback
                        },
                        {
                            "metric": "Flow",
                            "score": flow_score,
                            "max_score": 5,
                            "feedback": flow_feedback
                        }
                    ],
                    "semantic_similarity": semantic_scores.get('content', 'N/A')
                },
                {
                    "name": "Speech Rate",
                    "score": speech_rate_score,
                    "max_score": 10,
                    "weight_percentage": 10,
                    "details": [
                        {
                            "metric": "Words Per Minute",
                            "value": round(wpm, 1),
                            "feedback": speech_rate_feedback
                        }
                    ]
                },
                {
                    "name": "Language & Grammar",
                    "score": language_grammar_total,
                    "max_score": 20,
                    "weight_percentage": 20,
                    "details": [
                        {
                            "metric": "Grammar Errors",
                            "score": grammar_score,
                            "max_score": 10,
                            "error_count": error_count,
                            "feedback": grammar_feedback
                        },
                        {
                            "metric": "Vocabulary Richness (TTR)",
                            "score": vocab_score,
                            "max_score": 10,
                            "value": round(ttr, 2),
                            "feedback": vocab_feedback
                        }
                    ]
                },
                {
                    "name": "Clarity",
                    "score": filler_score,
                    "max_score": 15,
                    "weight_percentage": 15,
                    "details": [
                        {
                            "metric": "Filler Word Rate",
                            "value": round(filler_rate, 2),
                            "feedback": filler_feedback
                        }
                    ],
                    "semantic_similarity": semantic_scores.get('clarity', 'N/A')
                },
                {
                    "name": "Engagement",
                    "score": sentiment_score,
                    "max_score": 15,
                    "weight_percentage": 15,
                    "details": [
                        {
                            "metric": "Sentiment/Positivity",
                            "value": round(positive_score, 2),
                            "feedback": sentiment_feedback
                        }
                    ],
                    "semantic_similarity": semantic_scores.get('engagement', 'N/A')
                }
            ]
        }
        
        return result


scorer = TranscriptScorer()


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/score', methods=['POST'])
def score_transcript():
    """API endpoint to score a transcript"""
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({"error": "No transcript provided"}), 400
        
        transcript = data['transcript']
        duration_sec = data.get('duration_sec', None)
        
        if not transcript.strip():
            return jsonify({"error": "Transcript cannot be empty"}), 400
        
        result = scorer.score_transcript(transcript, duration_sec)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "semantic_model_loaded": semantic_model is not None,
        "grammar_tool_loaded": grammar_tool is not None
    })


if __name__ == '__main__':
    print("Starting Communication Scoring API...")
    print(f"Semantic model loaded: {semantic_model is not None}")
    print(f"Grammar tool loaded: {grammar_tool is not None}")
    app.run(debug=True, host='0.0.0.0', port=5001)
