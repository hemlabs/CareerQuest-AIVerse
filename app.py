import os
import json
import requests
import PyPDF2
import re
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pytrends.request import TrendReq

# --- AI & DATABASE IMPORTS ---
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.vectorstores import Chroma

app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# 🔑 API keys are read from environment variables (or a local .env file, never committed)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
RAPID_API_KEY = os.environ.get("RAPID_API_KEY", "")
if not RAPID_API_KEY:
    print("⚠️ RAPID_API_KEY not set - job/internship search will not work. See .env.example")

# --- GLOBAL SESSION MEMORY ---
USER_SESSION = {
    "resume_text": "No resume uploaded yet.",
    "role_focus": "General Tech"
}

STATS_CACHE = {} 

# --- SETUP LOCAL BRAIN (AI) ---
print("🧠 Connecting to Local Llama 3...")
try:
    llm = OllamaLLM(model="llama3") 
    print("✅ AI Connected!")
except Exception as e:
    print(f"❌ AI Error: {e}")
    llm = None

# --- SETUP MEMORY (ChromaDB) ---
print("📂 Connecting to Knowledge Base...")
try:
    embedding_fn = OllamaEmbeddings(model="llama3")
    vector_db = Chroma(persist_directory="./chroma_db", embedding_function=embedding_fn)
    print("✅ Memory Loaded Successfully!")
except:
    vector_db = None
    print("⚠️ Warning: No ChromaDB found. Chat will rely on generic AI.")

# --- HELPER FUNCTIONS ---

def clean_json(text):
    """Robust JSON Extractor"""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = text[start:end]
            return json.loads(json_str)
        return {}
    except:
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return {}

def get_smart_stats(role):
    """Generates TARGET stats (Red Chart)"""
    key = role.lower().strip()
    
    if key in STATS_CACHE:
        print(f"⚡ Using Cached Stats for '{key}'")
        return STATS_CACHE[key]
    
    print(f"🤖 AI Generating Target Stats for '{key}'...")
    prompt = f"""
    Act as a Tech Lead. Rate the importance of these 6 skills (0-5) for the role: '{role}'.
    Skills: [Architecture, Frontend, Data, Security, Embedded, Product]
    
    CRITICAL: Return ONLY JSON: {{ "stats": [5, 2, 4, 1, 0, 3] }}
    """
    
    try:
        response = llm.invoke(prompt)
        data = clean_json(response)
        stats = data.get('stats', [])
        
        if not isinstance(stats, list): stats = [3,3,3,3,3,3]
        stats = stats[:6]
        while len(stats) < 6: stats.append(3)
        
        STATS_CACHE[key] = stats
        return stats
    except Exception as e:
        print(f"⚠️ AI Stat Gen Error: {e}")
        return [3,3,3,3,3,3]

def query_rag_with_context(question, user_context_str):
    """Combines Local Database knowledge with User Context and Llama 3"""
    
    greetings = ["hey", "hi", "hello", "sup", "yo", "greetings", "test"]
    if question.lower().strip().strip("!?.") in greetings:
        return "Hello! I am Guide.exe. I've analyzed your profile. Ask me how to improve!"

    db_context = ""
    if vector_db:
        try:
            results = vector_db.similarity_search(question, k=2)
            db_context = "\n".join([doc.page_content for doc in results])
        except Exception as e:
            print(f"RAG Error: {e}")

    prompt = f"""
    System: You are 'Guide.exe', a helpful and witty career strategy AI.
    
    --- USER CONTEXT (LIVE DATA) ---
    {user_context_str}
    
    --- KNOWLEDGE BASE ---
    {db_context}
    
    --- INSTRUCTION ---
    Answer the user's question based on their SPECIFIC stats and resume.
    1. If they ask about their resume, quote the 'User Resume Snippet'.
    2. If they ask about skills, refer to their 'Current Skill Stats' (0=Novice, 5=Expert).
    3. Keep the answer concise and helpful.

    User Question: {question}
    Answer:
    """
    return llm.invoke(prompt)

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

# 1. RESUME ANALYZER (Capped at 4)
@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    if 'file' not in request.files: return jsonify({"error": "No file"})
    file = request.files['file']
    
    try:
        pdf = PyPDF2.PdfReader(file)
        text = "".join([p.extract_text() for p in pdf.pages])[:3000]
        
        USER_SESSION["resume_text"] = text
        print("💾 Resume text saved to memory.")
        
        print("📄 Analyzing Resume...")
        prompt = f"""
        Analyze this resume text. Return a JSON object with scores (0-5) for these skills: 
        [Architecture, Frontend, Data, Security, Embedded, Product].
        Resume: {text}
        
        Output ONLY valid JSON like this: {{ "resume_stats": [0,0,0,0,0,0] }}
        """
        response = llm.invoke(prompt)
        data = clean_json(response)
        
        raw_stats = data.get("resume_stats", [0,0,0,0,0,0])
        if not isinstance(raw_stats, list): raw_stats = [0,0,0,0,0,0]
        
        # Force Cap at 4
        capped_stats = [min(s, 4) for s in raw_stats]
        
        return jsonify({"resume_stats": capped_stats})
        
    except Exception as e:
        print(f"Resume Error: {e}")
        return jsonify({"resume_stats": [1,1,1,1,1,1]})

# 2. ARCHETYPE REPORT
@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        data = request.json
        stats = data.get('stats')
        print(f"🛡️ Generating Professional Profile for stats: {stats}")
        
        prompt = f"""
        Act as a RPG Class Master for a Tech Career Game.
        Candidate Skills Score (0-5): 
        [Architecture, Frontend, Data, Security, Embedded, Product] -> {stats}
        
        Task:
        1. Assign a professional 'Class Title' (e.g., 'Code Paladin', 'Data Wizard').
        2. Recommend 3 REAL industry job titles.
        3. 'Angel Analysis': 1 positive sentence on strength.
        4. 'Devil Analysis': 1 critical sentence on weakness.
        
        JSON FORMAT: 
        {{
            "archetype": "Title Here",
            "angel_analysis": "Strength...",
            "devil_analysis": "Weakness...",
            "jobs": ["Job 1", "Job 2", "Job 3"]
        }}
        """
        
        raw_response = llm.invoke(prompt)
        json_data = clean_json(raw_response)
        if not json_data.get('jobs'):
            json_data['jobs'] = ["Software Engineer", "Systems Analyst", "Technical Lead"]
        
        return jsonify(json_data)

    except Exception as e:
        print(f"❌ Report Error: {e}")
        return jsonify({
            "archetype": "Software Engineer", 
            "angel_analysis": "Strong foundation detected.", 
            "devil_analysis": "Needs specialization.",
            "jobs": ["Python Developer", "Java Engineer", "Data Analyst"]
        })

# 3. ROADMAP GENERATOR (STRICT WEAKNESS TARGETING)
@app.route('/get_roadmap', methods=['POST'])
def get_roadmap():
    try:
        data = request.json
        role = data.get('role')
        user_stats = data.get('user_stats', [0,0,0,0,0,0]) 
        
        USER_SESSION["role_focus"] = role
        
        # 1. GET TARGET STATS (Red Chart)
        consistent_stats = get_smart_stats(role)
        
        # 2. IDENTIFY STRICT WEAKNESSES
        stat_labels = ['Architecture', 'Frontend', 'Data', 'Security', 'Embedded', 'Product']
        weak_areas = []
        weak_indices = [] # This list stores ONLY the indices where user < target
        
        for i in range(6):
            if consistent_stats[i] > user_stats[i]:
                gap = consistent_stats[i] - user_stats[i]
                weak_areas.append(f"{stat_labels[i]} (Gap: {gap})")
                weak_indices.append(i)
        
        # 3. CONSTRUCT STRICT PROMPT
        if not weak_indices:
            # If user has NO gaps, focus on their absolute lowest skill for mastery
            min_val = min(user_stats)
            weak_indices = [i for i, x in enumerate(user_stats) if x == min_val]
            focus_prompt = "User meets all requirements. Focus on ADVANCED MASTERY for their lowest stats to reach Level 5."
        else:
            focus_prompt = f"User is LACKING specifically in: {', '.join(weak_areas)}. You MUST generate tasks ONLY for these specific skills."

        valid_indices_str = str(weak_indices)

        print(f"🗺️ Generating Roadmap for {role}. Forced Indices: {valid_indices_str}")

        prompt = f"""
        Act as a Career Coach. Create a personalized learning path for '{role}'.
        
        CONTEXT:
        - Target Skills: {consistent_stats}
        - Current User Skills: {user_stats}
        - STRICT INSTRUCTION: {focus_prompt}

        CRITICAL RULES:
        1. Generate EXACTLY 5 sequential levels.
        2. The 'skill_reward_idx' for every level MUST be one of these integers: {valid_indices_str}.
        3. Do NOT generate tasks for skills that are not in that list.
        4. The 'title' and 'description' must match the skill being rewarded.
        
        REQUIRED JSON FORMAT:
        {{
            "levels": [
                {{ 
                    "title": "Task Name", 
                    "type": "Quest", 
                    "xp": 100, 
                    "skill_reward_idx": {weak_indices[0]}, 
                    "estimated_hours": 10,
                    "description": "Specific task to fix the weakness.",
                    "link": "search_url"
                }}
            ]
        }}
        """
        
        raw_response = llm.invoke(prompt)
        json_data = clean_json(raw_response)
        json_data['target_stats'] = consistent_stats
        
        # Fallback
        if not json_data.get('levels'):
             json_data['levels'] = [
                {"title": "Skill Gap Analysis", "type": "Quest", "xp": 100, "skill_reward_idx": weak_indices[0], "estimated_hours": 5},
                {"title": "Bridge the Gap", "type": "Quest", "xp": 200, "skill_reward_idx": weak_indices[0], "estimated_hours": 10},
                {"title": "Advanced Concepts", "type": "Quest", "xp": 300, "skill_reward_idx": weak_indices[0], "estimated_hours": 15},
                {"title": "Practical Application", "type": "Quest", "xp": 400, "skill_reward_idx": weak_indices[0], "estimated_hours": 20},
                {"title": "Final Project", "type": "Job", "xp": 500, "skill_reward_idx": weak_indices[0], "estimated_hours": 25}
            ]

        return jsonify(json_data)

    except Exception as e:
        print(f"❌ Roadmap Error: {e}")
        return jsonify({
            "target_stats": get_smart_stats(request.json.get('role', '')),
            "levels": []
        })

# 4. REAL JOB SEARCH
@app.route('/get_real_jobs', methods=['POST'])
def get_real_jobs():
    original_role = request.json.get('role', 'Developer')
    print(f"🌍 Searching Real Data for: {original_role}...")
    
    final_jobs_list = []
    FALLBACK_MAP = {
        "ai": "Python Developer", "ml": "Data Scientist", "data": "Data Analyst",
        "security": "Cyber Security", "cyber": "Network Engineer", "game": "Unity Developer",
        "blockchain": "Backend Developer", "cloud": "DevOps Engineer", "frontend": "Web Developer",
        "react": "Frontend Developer", "backend": "Software Engineer", "full stack": "Software Developer"
    }

    def fetch_live_data(search_term, is_fallback=False):
        results = []
        try:
            url_intern = "https://internships-api.p.rapidapi.com/active-jb-7d"
            headers_intern = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "internships-api.p.rapidapi.com"}
            response = requests.get(url_intern, headers=headers_intern, params={"title_filter": search_term, "location_filter": "India"})
            data = response.json()
            intern_list = data if isinstance(data, list) else data.get('data', [])

            for item in intern_list[:3]:
                prefix = "[RELATED] " if is_fallback else ""
                results.append({
                    "company": item.get('organization', 'Unknown Organization'),
                    "role": f"{prefix}{item.get('title', 'Internship')}",
                    "location": "India (See Apply Link)",
                    "type": "Internship", 
                    "apply_link": item.get('url', '#'),
                    "salary": "Stipend: Check Listing",
                    "probability": "Verified Listing"
                })
        except: pass

        try:
            url_job = "https://jsearch.p.rapidapi.com/search"
            headers_job = {"X-RapidAPI-Key": RAPID_API_KEY, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
            query_prefix = "" if is_fallback else "Junior "
            response = requests.get(url_job, headers=headers_job, params={"query": f"{query_prefix}{search_term} in India", "page": "1", "num_pages": "1"})
            data = response.json()
            job_list = data.get('data', [])

            if job_list:
                top_job = job_list[0]
                salary = "Market Competitive"
                if top_job.get('job_min_salary') and top_job.get('job_max_salary'):
                    salary = f"₹{top_job.get('job_min_salary')} - {top_job.get('job_max_salary')}"
                
                results.append({
                    "company": top_job.get('employer_name', 'Hiring Company'),
                    "role": f"{prefix if is_fallback else ''}{top_job.get('job_title')}",
                    "location": f"{top_job.get('job_city', 'Remote')}, India",
                    "type": "Full Time",
                    "apply_link": top_job.get('job_apply_link', '#'),
                    "salary": salary,
                    "probability": "Verified Listing"
                })
        except: pass
        return results

    final_jobs_list = fetch_live_data(original_role, is_fallback=False)

    if len(final_jobs_list) == 0:
        fallback_role = "Software Engineer"
        for key, value in FALLBACK_MAP.items():
            if key in original_role.lower():
                fallback_role = value
                break
        final_jobs_list = fetch_live_data(fallback_role, is_fallback=True)

    if len(final_jobs_list) == 0:
        final_jobs_list.append({
            "company": "System Alert",
            "role": "No Live Listings Found",
            "location": "Try a different role",
            "type": "Error",
            "apply_link": "#",
            "salary": "---",
            "probability": "0%"
        })

    return jsonify({"jobs": final_jobs_list})

# 5. MARKET TRENDS
@app.route('/get_job_details', methods=['POST'])
def get_job_details():
    role = request.json.get('role', 'Python')
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload([role], cat=0, timeframe='today 12-m', geo='IN')
        data = pytrends.interest_over_time()
        trends = data[role].tolist()[-12:] if not data.empty else [50]*12
    except:
        trends = [20, 35, 40, 50, 60, 55, 70, 80, 75, 85, 90, 85]

    ai_stats = get_smart_stats(role)
    return jsonify({ "trends": trends, "required_stats": ai_stats })

# 6. CHAT AGENT
@app.route('/chat_agent', methods=['POST'])
def chat_agent():
    data = request.json
    msg = data.get('message', '')
    client_stats = data.get('stats', [0,0,0,0,0,0]) 
    client_role = data.get('role', USER_SESSION["role_focus"])
    
    stat_labels = ['Architecture', 'Frontend', 'Data', 'Security', 'Embedded', 'Product']
    stats_str = ", ".join([f"{stat_labels[i]}: {client_stats[i]}/5" for i in range(6)])

    user_context_str = f"""
    Target Role: {client_role}
    Current Skill Stats: {stats_str}
    User Resume Snippet: {USER_SESSION['resume_text'][:1000]}...
    """
    
    response = query_rag_with_context(msg, user_context_str)
    return jsonify({"reply": response})

# 7. INTERVIEW
@app.route('/interview_chat', methods=['POST'])
def interview_chat():
    data = request.json
    role = data.get('role')
    msg = data.get('message')
    
    if "start" in msg.lower():
        q = llm.invoke(f"Ask one hard technical question for a {role} role.")
        return jsonify({"reply": q})
    else:
        q = llm.invoke(f"User answered: '{msg}'. Grade answer and ask next question for {role}.")
        return jsonify({"reply": q})

if __name__ == '__main__':
    print("🚀 CareerQuest Backend Running on Port 5000...")
    app.run(port=5000, debug=True)