# CareerQuest-AIVerse 🚀

[cite_start]**Team Name:** The Powerpuff Girls [cite: 25]
[cite_start]**Track:** Agentic AI [cite: 26]
[cite_start]**Problem Statement:** Students face uncertainty in identifying suitable job opportunities and lack continuous support to translate skills into career success. [cite: 6]

## 📖 Project Description
Career Quest is an Agentic AI career companion that transforms professional growth into an immersive RPG adventure. [cite_start]Unlike standard job boards, it continuously analyzes user behavior, plans learning paths, and evolves with the user’s career journey. [cite: 7, 12]

[cite_start]It identifies exact skill gaps by matching resumes to real-time job requirements, generating focused roadmaps that close the employability gap without tutorial overload. [cite: 14]

## ✨ Key Features
* **Hybrid Entry System:** Choose a target role directly or discover it via a 3-step AI discovery process (Behavior, Resume, Interests).
* **Precision Gap Analysis:** Radar-based skill mapping comparing your current abilities against real industry requirements.
* **Active Skill Verification:** Real-time AI "Boss Battles" (interviews) to validate actual competency instead of passive course completion.
* **Gamified Progress Tracking:** XP, levels, and milestone-based progression with weekly telemetry to track learning velocity.
* [cite_start]**Live Market Intelligence:** Location-aware job listings and skill demand trends ensure learning stays market-relevant. [cite: 16]

## 🛠️ Tech Stack (Solution Architecture)
This project is built using a "Local Brain" privacy-first architecture:

**🧠 AI & Orchestration**
* [cite_start]**Ollama + Llama 3:** Local Intelligence / LLM [cite: 19]
* [cite_start]**LangChain:** Agent Orchestration [cite: 19]

**💾 Data & Memory**
* [cite_start]**ChromaDB:** RAG Knowledge retrieval [cite: 20]
* [cite_start]**SQLite:** User Data storage [cite: 20]

**🎨 Frontend & Visuals**
* [cite_start]**HTML5 + TailwindCSS:** Pixel Art UI [cite: 21]
* [cite_start]**Chart.js:** Visual data representation (Radar charts, Trend lines) [cite: 21]

**🔌 Backend & APIs**
* [cite_start]**Flask:** API Framework [cite: 22]
* [cite_start]**Pytrends:** Job trend analysis curve [cite: 22]
* [cite_start]**JSearch RapidApi:** Real-time Hiring Links [cite: 22]

## ⚙️ Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/CareerQuest-AIVerse.git](https://github.com/YOUR_USERNAME/CareerQuest-AIVerse.git)
    cd CareerQuest-AIVerse
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python app.py
    ```

4.  **Access the App:**
    Open your browser and navigate to `http://127.0.0.1:5000`

## 📸 Prototype Note
*For the purpose of the hackathon demonstration, some local AI components (Llama 3) may be simulated using cloud proxies (Gemini) to ensure performance on non-GPU hardware during the demo recording.*

---
*Submitted for AiVERSE Hackathon 2026*