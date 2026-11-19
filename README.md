# CareerQuest-AIVerse 🚀

**Team Name:** The Powerpuff Girls
**Track:** Agentic AI
**Problem Statement:** Students face uncertainty in identifying suitable job opportunities and lack continuous support to translate skills into career success.

## 📖 Project Description
Career Quest is an Agentic AI career companion that transforms professional growth into an immersive RPG adventure. Unlike standard job boards, it continuously analyzes user behavior, plans learning paths, and evolves with the user’s career journey.

It identifies exact skill gaps by matching resumes to real-time job requirements, generating focused roadmaps that close the employability gap without tutorial overload.

## ✨ Key Features
* **Hybrid Entry System:** Choose a target role directly or discover it via a 3-step AI discovery process (Behavior, Resume, Interests).
* **Precision Gap Analysis:** Radar-based skill mapping comparing your current abilities against real industry requirements.
* **Active Skill Verification:** Real-time AI "Boss Battles" (interviews) to validate actual competency instead of passive course completion.
* **Gamified Progress Tracking:** XP, levels, and milestone-based progression with weekly telemetry to track learning velocity.
* **Live Market Intelligence:** Location-aware job listings and skill demand trends ensure learning stays market-relevant.

## 🛠️ Tech Stack (Solution Architecture)
This project is built using a "Local Brain" privacy-first architecture:

**🧠 AI & Orchestration**
* **Ollama + Llama 3:** Local Intelligence / LLM
* **LangChain:** Agent Orchestration

**💾 Data & Memory**
* **ChromaDB:** RAG Knowledge retrieval
* **SQLite (via ChromaDB):** Persistent vector store

**🎨 Frontend & Visuals**
* **HTML5 + TailwindCSS:** Pixel Art UI
* **Chart.js:** Visual data representation (Radar charts, Trend lines)

**🔌 Backend & APIs**
* **Flask:** API Framework
* **Pytrends:** Job trend analysis curve
* **JSearch RapidApi:** Real-time Hiring Links

## ⚙️ Installation & Setup

**Prerequisites:** Python 3.10+, [Ollama](https://ollama.com), and a free [RapidAPI](https://rapidapi.com) key subscribed to the *JSearch* and *Internships* APIs.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hemlabs/CareerQuest-AIVerse.git
    cd CareerQuest-AIVerse
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Pull the local model:**
    ```bash
    ollama pull llama3
    ```

4.  **Add your API key:**
    Copy `.env.example` to `.env` and put your RapidAPI key in it:
    ```bash
    cp .env.example .env      # Windows: copy .env.example .env
    ```
    `.env` is git-ignored, so never commit your real key.

5.  **Build the knowledge base** (one-time, downloads the job-description and interview datasets into `chroma_db/`):
    ```bash
    python ingest.py
    ```

6.  **Run the application:**
    ```bash
    python app.py
    ```

7.  **Access the App:**
    Open your browser and navigate to `http://127.0.0.1:5000`

## 📸 Prototype Note
*For the purpose of the hackathon demonstration, some local AI components (Llama 3) may be simulated using cloud proxies (Gemini) to ensure performance on non-GPU hardware during the demo recording.*

---
*Submitted for AiVERSE Hackathon 2026*
