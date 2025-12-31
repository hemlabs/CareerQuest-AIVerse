import json
import PyPDF2 
import io
from serpapi import GoogleSearch
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import datetime

# Import Google AI
try:
    import google.generativeai as genai
    print("✓ Using google.generativeai")
except ImportError:
    print("⚠ Please install: pip install google-generativeai")
    exit(1)

# --- CONFIGURATION ---
app = Flask(__name__)
CORS(app)

# Your API Key
GOOGLE_API_KEY = "YOUR_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)
MODEL_NAME = 'gemini-flash-latest'

# --- ROUTES ---
# --- SERPAPI: REAL JOB FETCHER ---
@app.route('/get_real_jobs', methods=['POST'])
def get_real_jobs():
    try:
        data = request.json
        role = data.get('role', 'Developer')
        location = "India" # You can make this dynamic if you want

        print(f"🔎 Searching Real Jobs for: {role} in {location}...")

        # 1. Configure Search
        params = {
            "engine": "google_jobs",
            "q": f"{role} jobs in {location}",
            "hl": "en",
            "gl": "in",
            "api_key": "YOUR_KEY_HERE"  # <--- PASTE YOUR KEY HERE
        }

        # 2. Fetch Data
        search = GoogleSearch(params)
        results = search.get_dict()
        jobs_results = results.get("jobs_results", [])

        # 3. Format for Frontend (Take top 5)
        formatted_jobs = []
        for job in jobs_results[:5]:
            formatted_jobs.append({
                "company": job.get("company_name", "Unknown Guild"),
                "role": job.get("title", role),
                "location": job.get("location", "Remote"),
                "package": "Salary Hidden", # Google Jobs often hides salary, so we use a placeholder or check 'detected_extensions'
                "type": job.get("detected_extensions", {}).get("schedule_type", "Full Time"),
                "apply_link": job.get("related_links", [{}])[0].get("link", "#"), # Link to apply
                "probability": "REAL" # Tag to show it's a live listing
            })

        return jsonify({"jobs": formatted_jobs})

    except Exception as e:
        print(f"SerpAPI Error: {e}")
        return jsonify({"error": "Could not fetch real jobs."}), 500
@app.route('/')
def home():
    return render_template('index.html')

# 1. RESUME ANALYZER
@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    try:
        # Check if file part exists
        if 'file' not in request.files:
            return jsonify({"resume_stats": [1,1,1,1,1,1], "error": "No file uploaded"})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"resume_stats": [1,1,1,1,1,1], "error": "No file selected"})

        print(f"📄 Processing Resume: {file.filename}...")
        
        resume_text = ""

        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                resume_text += page.extract_text() or ""
        else:
            # Fallback for .txt files
            resume_text = file.read().decode('utf-8')

        prompt = f"""
        Analyze this resume for a Tech Career RPG.
        Score these 6 stats (0-5) based on experience:
        [Architecture, Frontend, Data, Security, Embedded, Product]
        
        Resume Content: "{resume_text[:4000]}"
        
        JSON ONLY: {{ "resume_stats": [0,0,0,0,0,0] }}
        """
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = response.text
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return jsonify(json.loads(json_str))
        else:
            raise ValueError("No JSON found in response")

    except Exception as e:
        print(f"Resume Error: {e}")
        return jsonify({"resume_stats": [1,1,1,1,1,1]})
# 2. ARCHETYPE REPORT
# ... existing imports ...

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        stats = data.get('stats')
        interests = data.get('interests')
        
        prompt = f"""
        Role: You are a game engine generating a Career RPG report.
        User Stats: {stats} (Order: Architecture, Frontend, Data, Security, Embedded, Product).
        Interests: {interests}.
        
        Task:
        1. Determine an RPG "Archetype Name" (e.g., "Code Paladin").
        2. Recommend 2 Job Roles.
        3. Create "Angel Analysis": A sweet, encouraging paragraph explaining which high stats make them perfect for these roles.
        4. Create "Devil Analysis": A cynical, but not harsh paragraph explaining the hidden daily costs (because the right career isn’t about advantages alone, but the inconveniences you’re willing to live with)
        
        Output JSON ONLY: 
        {{
            "archetype": "Name",
            "jobs": ["Role A", "Role B"],
            "angel_analysis": "You are amazing at... (explain pros)",
            "devil_analysis": "You are terrible at... (explain cons)"
        }}
        """
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = response.text
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return jsonify(json.loads(json_str))
        else:
            raise ValueError("No JSON found")

    except Exception as e:
        print(f"Report Error: {e}")
        # Fallback if AI fails
        return jsonify({
            "archetype": "Novice", 
            "jobs": ["Frontend Dev", "Backend Dev"],
            "angel_analysis": "You show great potential! Keep learning!",
            "devil_analysis": "You are going to bugs everywhere. Good luck."
        })

# 3. ROADMAP GENERATOR (With Time Estimation)
@app.route('/get_roadmap', methods=['POST'])
def get_roadmap():
    try:
        data = request.json
        role = data.get('role')
        
        if not role: return jsonify({"target_stats":[3,3,3,3,3,3], "levels":[]})

        print(f"🗺️ Generating Roadmap for {role}...")

        prompt = f"""
        Create a gamified 'Duolingo-style' learning path for a '{role}'.
        Generate 6 sequential 'Levels'. 
        For EACH level, assign:
        - title: Short name
        - type: 'Course', 'Project', or 'Hackathon'
        - skill_reward_idx: Which stat (0-5) increases?
        - xp: XP gained (int)
        - estimated_hours: Typical hours to complete this level (int)
        
        Also define 'Target Stats' (0-5).

        JSON ONLY:
        {{
            "target_stats": [4, 5, 2, 1, 0, 3],
            "levels": [
                {{"title": "Level 1: Syntax", "type": "Course", "skill_reward_idx": 1, "xp": 100, "estimated_hours": 5}}
            ]
        }}
        """
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = response.text
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return jsonify(json.loads(json_str))
        else:
            raise ValueError("No JSON found")

    except Exception as e:
        print(f"Roadmap Error: {e}")
        return jsonify({
            "target_stats": [3,3,3,3,3,3],
            "levels": [{"title": "Basics", "type": "Course", "skill_reward_idx": 1, "xp": 100, "estimated_hours": 5}]
        })

# 4. CHAT AGENT (Guide)
@app.route('/chat_agent', methods=['POST'])
def chat_agent():
    try:
        data = request.json
        user_msg = data.get('message')
        context = data.get('context', 'General Career Help')

        prompt = f"""
        You are the 'Career Quest' Guide, a helpful 8-bit RPG character.
        Context: {context}
        User asks: {user_msg}
        Respond in a helpful, encouraging, short, and 'game-like' style (under 3 sentences).
        """
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Chat Error: {e}")
        return jsonify({"reply": "System Malfunction... Check console."})

# 5. INTERVIEW SIMULATOR (Boss Battle)
@app.route('/interview_chat', methods=['POST'])
def interview_chat():
    try:
        data = request.json
        history = data.get('history', [])
        role = data.get('role', 'General Developer')
        user_msg = data.get('message')
        
        prompt = f"""
        You are a strict Technical Interviewer for a {role} position.
        This is a simulation.
        
        Chat History:
        {history}
        
        User's latest input: "{user_msg}"
        
        Instructions:
        1. If the user's answer is wrong, correct them briefly.
        2. Then, ask ONE new technical question related to {role}.
        3. Keep it professional but challenging.
        4. If the input is "Start Interview", just ask the first question.
        """
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"Interview Error: {e}")
        return jsonify({"reply": "Interview simulation error."})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')
# 6. JOB OFFER GENERATOR
@app.route('/get_job_offer', methods=['POST'])
def get_job_offer():
    try:
        data = request.json
        role = data.get('role', 'Developer')
        
        prompt = f"""
        Generate 5 fictional "Job or Internship Opportunities" for a '{role}' in India.
        Context: The user has good stats in a coding game. 
        Don't make them "hired" yet. Just list opportunities they have a high chance of getting.
        
        Requirements:
        1. Mix of "Internship" and "Full Time".
        2. Real Indian Tech Hubs (Bangalore, Pune, Gurgaon, Hyderabad, etc.).
        3. Realistic Packages (LPA).
        4. Company Names: Cool fictional tech startups.
        5. Probability: "High", "Very High", or "Medium".
        
        Output JSON ONLY:
        {{
            "jobs": [
                {{
                    "company": "Nexus AI",
                    "role": "Jr. Dev",
                    "location": "Bangalore",
                    "package": "6.5 LPA",
                    "type": "Full Time",
                    "probability": "95%"
                }},
                {{
                    "company": "Pune Pixel",
                    "role": "Intern",
                    "location": "Pune",
                    "package": "15k/mo",
                    "type": "Internship",
                    "probability": "High"
                }}
            ]
        }}
        """
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = response.text
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return jsonify(json.loads(text[start:end]))
        else:
            raise ValueError("No JSON")

    except Exception as e:
        print(f"Offer Error: {e}")
        # Fallback if AI fails
        return jsonify({
            "jobs": [
                {"company": "Server Down Sys", "role": "Dev", "location": "Remote", "package": "4 LPA", "type": "Full Time", "probability": "High"},
                {"company": "Glitch Corp", "role": "Intern", "location": "Bangalore", "package": "20k/mo", "type": "Internship", "probability": "Medium"}
            ]
        })
        
# 7. JOB DETAILS (Trends & Skills)
@app.route('/get_job_details', methods=['POST'])
def get_job_details():
    try:
        data = request.json
        role = data.get('role', 'Developer')
        
        prompt = f"""
        Generate market data for the job role '{role}' in India.
        
        Output JSON ONLY:
        {{
            "trends": [65, 70, 80, 85, 90, 88, 92, 95, 85, 75, 70, 72], (12 integers 0-100 representing popularity Jan-Dec)
            "required_stats": [3, 5, 2, 1, 0, 4] (6 integers 0-5 representing required level for: Architecture, Frontend, Data, Security, Embedded, Product)
        }}
        """
        
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = response.text
        
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            return jsonify(json.loads(text[start:end]))
        else:
            raise ValueError("No JSON")

    except Exception as e:
        print(f"Details Error: {e}")
        return jsonify({
            "trends": [50,50,50,50,50,50,50,50,50,50,50,50],
            "required_stats": [3,3,3,3,3,3]
        })
        
if __name__ == '__main__':
    Timer(1, open_browser).start()
    print("🚀 PC App Running on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)