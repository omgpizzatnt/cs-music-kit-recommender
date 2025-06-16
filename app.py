import os
import random
import requests
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Google Gemini AI
api_key = os.environ.get('GOOGLE_AI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
else:
    model = None
    print("Warning: GOOGLE_AI_API_KEY not found. AI recommendations will not work.")

# CS:GO loading messages
LOADING_MESSAGES = [
    "Aligning headshots...",
    "Reloading magazines...",
    "Priming grenades...",
    "Filling molotovs...",
    "Stocking ammo...",
    "Gathering bullets...",
    "Dusting off armor...",
    "Repairing helmets...",
    "Locking and loading...",
    "Lining up smokes...",
    "Recoil compensating...",
    "Equipping loadouts...",
    "Spray transferring...",
    "Calculating sightlines...",
    "Securing positions...",
    "Counting entry frags...",
    "Preparing to clutch...",
    "Analyzing flickshots...",
    "Marking bombsites...",
    "Calibrating sniper scopes...",
    "Counter-strafing...",
    "Practicing bunny-hops...",
    "Going sneaky-beaky-like...",
    "Running and gunning...",
    "Holding an angle...",
    "Calling strats...",
    "Hatching chickens...",
    "Rushing B...",
    "Squeezing lemons...",
    "Going on a windy walk...",
    "Planting for cat...",
    "Incrementing StatTraks...",
    "Memorizing callouts...",
    "Peeking mid...",
    "Picking up shell casings...",
    "Flashing in...",
    "Taking hostages...",
    "Striking-counters...",
    "Adjusting crosshairs...",
    "Inspecting weapons...",
    "Accepting...",
    "Dropping for teammates...",
    "Making friends...",
    "Scrubbing graffiti...",
    "Closing squeaky doors...",
    "Replacing windows...",
    "Demarcating buy zones...",
    "Attaching suppressors...",
    "One bullet left...",
    "Watching Major highlights..."
]

# Music kits data will be loaded from the API
MUSIC_KITS_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/en/music_kits.json"

def fetch_music_kits():
    """Fetch music kits from the API"""
    try:
        response = requests.get(MUSIC_KITS_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching music kits: {e}")
        return []

def get_rule_based_recommendation(feelings_data, music_kits):
    """Fallback rule-based recommendation when AI is not available - Updated for 4-axis system"""
    motivation = feelings_data.get('motivation', 50)  # Performance(0) ↔ Entertainment(100)
    identity = feelings_data.get('identity', 50)      # Individualist(0) ↔ Conformist(100)
    style = feelings_data.get('style', 50)            # Aggression(0) ↔ Composure(100)
    status = feelings_data.get('status', 50)          # Pragmatism(0) ↔ Flex(100)
    mood = feelings_data.get('mood', 'neutral')
    
    # Rule-based selection based on 4-axis personality
    if motivation < 30 and style < 30:
        # Performance-focused + Aggressive = Competitive/Pro kits
        keywords = ['professional', 'tactical', 'intense', 'domination', 'ultimate', 'pro']
    elif motivation > 70 and identity < 30:
        # Entertainment + Individualist = Unique/Creative kits
        keywords = ['unique', 'creative', 'artistic', 'experimental', 'funky', 'colorful']
    elif style < 30:
        # Aggressive style = Heavy/Metal kits
        keywords = ['metal', 'aggressive', 'heavy', 'death', 'hardcore', 'demolition', 'battle']
    elif style > 70:
        # Composed style = Atmospheric/Cinematic kits
        keywords = ['cinematic', 'atmospheric', 'epic', 'orchestral', 'ambient', 'peaceful']
    elif status > 70:
        # Flex-oriented = Premium/Exclusive kits
        keywords = ['legendary', 'premium', 'exclusive', 'rare', 'epic', 'ultimate']
    elif status < 30:
        # Pragmatic = Classic/Reliable kits
        keywords = ['classic', 'reliable', 'standard', 'traditional', 'original']
    elif identity > 70:
        # Conformist = Popular/Mainstream kits
        keywords = ['popular', 'mainstream', 'community', 'favorite', 'loved']
    elif identity < 30:
        # Individualist = Niche/Underground kits
        keywords = ['underground', 'niche', 'alternative', 'experimental', 'indie']
    else:
        # Balanced = Versatile kits
        keywords = ['versatile', 'balanced', 'adaptable', 'smooth', 'refined']
    
    # Find kits matching keywords
    suitable_kits = []
    for kit in music_kits:
        description_lower = kit['description'].lower()
        name_lower = kit['name'].lower()
        if any(keyword in description_lower or keyword in name_lower for keyword in keywords):
            suitable_kits.append(kit)
    
    # If no matches, fallback to random selection
    if not suitable_kits:
        suitable_kits = music_kits[:20]  # Take first 20 as fallback
    
    selected_kit = random.choice(suitable_kits)
      # Generate explanation based on axis positioning
    explanation_parts = []
    
    if motivation < 40:
        explanation_parts.append("suits performance-oriented players")
    elif motivation > 60:
        explanation_parts.append("designed for entertainment experience")
    
    if identity < 40:
        explanation_parts.append("showcases your unique personality")
    elif identity > 60:
        explanation_parts.append("aligns with mainstream community taste")
    
    if style < 40:
        explanation_parts.append("matches your aggressive playstyle")
    elif style > 60:
        explanation_parts.append("reflects composed and calm temperament")
    
    if status < 40:
        explanation_parts.append("a pragmatic and wise choice")
    elif status > 60:
        explanation_parts.append("displays your gaming taste")
    
    if explanation_parts:
        explanation = f"This music kit {', '.join(explanation_parts)}, perfectly matching your current {mood} mood!"
    else:
        explanation = f"This balanced music kit perfectly suits your current {mood} state and will enhance your CS2 gaming experience."
    
    return {
        'kit': selected_kit,
        'explanation': explanation
    }

def get_enhanced_music_kit_recommendation(feelings_data):
    """Enhanced recommendation using AI with web search capabilities"""
    try:
        # Get music kits
        music_kits = fetch_music_kits()
        if not music_kits:
            return None
        
        # Filter out StatTrak and exclusive kits for simplicity
        regular_kits = [kit for kit in music_kits if not kit['name'].startswith('StatTrak™') and not kit.get('exclusive', False)]
        
        # If no AI model available, use rule-based recommendation
        if not model:
            return get_rule_based_recommendation(feelings_data, regular_kits)
        
        # Create a more detailed prompt for AI with search context
        kit_descriptions = []
        for kit in regular_kits[:30]:  # Limit to first 30 to avoid token limits
            kit_descriptions.append(f"- {kit['name']}: {kit['description']}")
        prompt = f"""
        You are an expert CS2 music kit recommender. Based on the user's 4-dimensional personality profile, recommend the most suitable CS2 music kit.

        User's 4-Axis Personality Profile:
        - X-Axis Motivation: {feelings_data.get('motivation', 50)}/100 (0=Performance-oriented, 100=Entertainment-oriented)
        - Y-Axis Identity: {feelings_data.get('identity', 50)}/100 (0=Individualist, 100=Conformist)
        - Z-Axis Style: {feelings_data.get('style', 50)}/100 (0=Aggressive, 100=Composed)
        - W-Axis Status: {feelings_data.get('status', 50)}/100 (0=Pragmatic, 100=Flex-oriented)
        - Current Mood: {feelings_data.get('mood', 'neutral')}

        Available CS2 Music Kits:
        {chr(10).join(kit_descriptions)}

        Recommendation Guidelines:
        1. For Performance-oriented (low motivation): Choose tactical/competitive kits
        2. For Entertainment-oriented (high motivation): Choose fun/creative kits
        3. For Individualist (low identity): Choose unique/experimental kits
        4. For Conformist (high identity): Choose popular/mainstream kits
        5. For Aggressive style (low style): Choose intense/metal kits
        6. For Composed style (high style): Choose atmospheric/cinematic kits
        7. For Pragmatic (low status): Choose classic/reliable kits
        8. For Flex-oriented (high status): Choose premium/exclusive kits

        Consider the combination of these axes to find the perfect match for their gaming personality.        Respond in this exact JSON format:
        {{
            "recommended_kit": "Exact Music Kit Name",
            "explanation": "Detailed explanation of why this kit matches their 4-axis profile",
            "mood_match": "How it specifically matches their current mood and personality axes"
        }}
        """        
        # Generate content with the model
        response = model.generate_content(prompt)
        
        # Parse the AI response
        try:
            # Clean the response text
            response_text = response.text.strip()
            
            # Try to extract JSON from the response
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Additional cleaning for common AI response issues
            response_text = response_text.replace('\n', ' ').replace('\r', '')
            
            # Try to find JSON in the response if it's wrapped in text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                response_text = response_text[json_start:json_end]
            
            ai_response = json.loads(response_text)
            recommended_name = ai_response.get('recommended_kit', '')
            
            # Find the exact kit match
            for kit in regular_kits:
                if recommended_name.lower() in kit['name'].lower() or kit['name'].lower() in recommended_name.lower():
                    return {
                        'kit': kit,
                        'explanation': ai_response.get('explanation', 'This music kit matches your current mood and gaming style.'),
                        'mood_match': ai_response.get('mood_match', f'Perfect for your {feelings_data.get("mood", "current")} mood'),
                        'ai_powered': True
                    }
            
            # If no exact match, try partial matching
            for kit in regular_kits:
                kit_words = kit['name'].lower().split()
                recommended_words = recommended_name.lower().split()
                if any(word in kit_words for word in recommended_words if len(word) > 3):
                    return {
                        'kit': kit,
                        'explanation': ai_response.get('explanation', 'This music kit was selected based on AI analysis of your mood.'),
                        'mood_match': ai_response.get('mood_match', f'Matches your {feelings_data.get("mood", "current")} state'),
                        'ai_powered': True
                    }
                    
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            # Fallback to text analysis
            response_text = response.text.lower()
            for kit in regular_kits:
                kit_key_words = [word for word in kit['name'].lower().split() if len(word) > 3]
                if any(word in response_text for word in kit_key_words):
                    return {
                        'kit': kit,
                        'explanation': 'This music kit was recommended by AI based on your current feelings.',
                        'mood_match': f'Selected for your {feelings_data.get("mood", "current")} mood',
                        'ai_powered': True
                    }
        
        # Final intelligent fallback based on user feelings
        return get_intelligent_fallback_recommendation(feelings_data, regular_kits)
            
    except Exception as e:
        print(f"Error in enhanced recommendation: {e}")
        return get_rule_based_recommendation(feelings_data, regular_kits if 'regular_kits' in locals() else fetch_music_kits())

def get_intelligent_fallback_recommendation(feelings_data, music_kits):
    """Intelligent fallback when AI parsing fails"""
    motivation = feelings_data.get('motivation', 50)  # Performance vs Entertainment
    identity = feelings_data.get('identity', 50)      # Individualist vs Conformist  
    style = feelings_data.get('style', 50)            # Aggression vs Composure
    status = feelings_data.get('status', 50)          # Pragmatism vs Flex
    mood = feelings_data.get('mood', 'neutral')
    
    # Advanced scoring system
    scored_kits = []
    
    for kit in music_kits:
        score = 0
        description_lower = kit['description'].lower()
        name_lower = kit['name'].lower()
        
        # Motivation axis scoring (Performance vs Entertainment)
        if motivation > 70:  # Entertainment-oriented
            if any(word in description_lower for word in ['fun', 'exciting', 'energetic', 'creative', 'experimental']):
                score += 25
        elif motivation < 30:  # Performance-oriented
            if any(word in description_lower for word in ['professional', 'competitive', 'tactical', 'serious']):
                score += 25
        
        # Identity axis scoring (Individualist vs Conformist)
        if identity < 30:  # Individualist
            if any(word in description_lower for word in ['unique', 'experimental', 'special', 'rare', 'different']):
                score += 25
        elif identity > 70:  # Conformist
            if any(word in description_lower for word in ['classic', 'popular', 'traditional', 'standard']):
                score += 25
        
        # Style axis scoring (Aggression vs Composure)
        if style < 30:  # Aggressive            if any(word in description_lower for word in ['metal', 'hardcore', 'death', 'demolition', 'battle']):
                score += 25
        elif style > 70:  # Composed
            if any(word in description_lower for word in ['melodic', 'beautiful', 'serene', 'gentle', 'atmospheric']):
                score += 25
        
        # Status axis scoring (Pragmatism vs Flex)
        if status < 30:  # Pragmatic
            if any(word in description_lower for word in ['classic', 'reliable', 'standard', 'practical']):
                score += 25
        elif status > 70:  # Flex-oriented
            if any(word in description_lower for word in ['legendary', 'epic', 'ultimate', 'supreme', 'exclusive']):
                score += 25
        
        # Mood-based scoring
        if mood == 'excited':
            if any(word in description_lower for word in ['electronic', 'dance', 'upbeat', 'energetic']):
                score += 25
        elif mood == 'competitive':
            if any(word in description_lower for word in ['domination', 'ultimate', 'intense', 'battle']):
                score += 25
        elif mood == 'chill':
            if any(word in description_lower for word in ['chill', 'relaxed', 'smooth', 'jazz', 'funk']):
                score += 25
        elif mood == 'focused':
            if any(word in description_lower for word in ['focused', 'precision', 'tactical', 'strategic']):
                score += 25
        
        scored_kits.append((kit, score))
    
    # Sort by score and pick the best match
    scored_kits.sort(key=lambda x: x[1], reverse=True)
    
    if scored_kits:
        best_kit, best_score = scored_kits[0]
          # Generate explanation based on the 4-axis scoring
        explanation_parts = []
        if motivation > 70:
            explanation_parts.append(f"suits entertainment-focused gaming style ({motivation}%)")
        elif motivation < 30:
            explanation_parts.append(f"matches performance-oriented approach ({motivation}%)")
        
        if identity < 30:
            explanation_parts.append("showcases your unique personality")
        elif identity > 70:
            explanation_parts.append("aligns with mainstream community taste")
        
        if style < 30:
            explanation_parts.append("complements your aggressive playstyle")
        elif style > 70:
            explanation_parts.append("reflects your composed and calm demeanor")
        
        if status > 70:
            explanation_parts.append("displays your refined gaming taste")
        
        if explanation_parts:
            explanation = f"This music kit {' and '.join(explanation_parts)}. Perfect for your current {mood} gaming session!"
        else:
            explanation = f"This balanced music kit perfectly suits your current {mood} mood and will enhance your CS2 experience."
        
        return {
            'kit': best_kit,
            'explanation': explanation,
            'mood_match': f'Intelligent match for your {mood} state',
            'ai_powered': False,
            'score': best_score
        }
    
    # Ultimate fallback
    return get_rule_based_recommendation(feelings_data, music_kits)

def get_music_kit_recommendation(feelings_data):
    """Main recommendation function that chooses between enhanced AI or rule-based"""
    return get_enhanced_music_kit_recommendation(feelings_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/loading-message')
def get_loading_message():
    return jsonify({'message': random.choice(LOADING_MESSAGES)})

@app.route('/api/recommend', methods=['POST'])
def recommend_music_kit():
    feelings_data = request.get_json()
    
    if not feelings_data:
        return jsonify({'error': 'No feelings data provided'}), 400
    
    recommendation = get_music_kit_recommendation(feelings_data)
    
    if recommendation:
        return jsonify(recommendation)
    else:
        return jsonify({'error': 'Unable to get recommendation'}), 500

@app.route('/api/music-kits')
def get_all_music_kits():
    """Endpoint to get all music kits"""
    kits = fetch_music_kits()
    return jsonify(kits)

if __name__ == '__main__':
    app.run(debug=True)
