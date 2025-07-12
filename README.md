# AutoSenseAI – Remote IoT Sensor Monitoring & Diagnostics (WIP)

## 📌 About the Project

AutoSenseAI began as a personal project driven by my interest in smart systems and how technology can be used to catch problems before they happen. I’ve gotten to know several building automation technicians, and one thing I kept hearing is how often they’re called out to job sites for issues that could have been fixed remotely—or even avoided entirely with better diagnostics.

That sparked the idea: what if an AI-powered backend system could simulate how these decisions are made? AutoSenseAI was built to explore that idea. It models rule-based fault detection and suggests potential fixes that could be reviewed and approved by technicians before dispatch. The goal is to save time, reduce unnecessary site visits, and move toward smarter remote diagnostics.

While it's not powered by machine learning yet, the architecture is designed to mimic how AI systems could learn from recurring problems, automate resolution suggestions, and ultimately improve operational efficiency. This project gave me the chance to combine backend development with a real-world problem I care about—and I hope to keep evolving it from here.


**AutoSenseAI** is a backend application designed to simulate real-time monitoring and diagnostics of HVAC sensor data in smart building environments. It models how predictive maintenance and anomaly detection workflows could operate using lightweight backend logic.

> ⚠️ **Note:** This project is currently a work in progress. Core backend functionality is complete. Diagnostic logic, frontend UI, and extended features are actively being developed.

---

## 🚀 Features

- Flask-style backend with RESTful API endpoints
- Full CRUD operations for managing HVAC devices
- SQLite database for persistent device storage
- Simulated diagnostics for temperature, fault status, and system activity
- Postman-tested endpoints for reliability and edge case handling
- Early-stage HTML/CSS UI (WIP)
- Simulates AI/LLM-driven support workflows (rule-based logic)

---

## 🧠 Simulated AI/LLM Workflow (Planned)

AutoSenseAI is designed to emulate key concepts of automated support systems without using actual machine learning. Planned features include:

- Rule-based anomaly detection from sensor data
- Trigger-based diagnostics and alerts
- Simulated triage logic for prioritizing maintenance cases
- A modular backend structure prepared for future AI integration

---

## 📦 Tech Stack

- **Language:** Python 3  
- **Framework:** Flask-style architecture  
- **Database:** SQLite  
- **Frontend:** HTML/CSS (in progress)  
- **Tools:** Postman, VS Code

---

## 📁 Project Structure

AutoSenseAI/
├── template.py # Core backend logic and routes
├── devices.db # Local SQLite database file
├── main.html # UI structure (WIP)
├── style.css # Basic styling (WIP)
├── README.md # Project documentation

---

## 🧪 Setup & Run Instructions

Clone the repository and start the backend locally:

```bash
git clone https://github.com/AlexisTarango1/AutoSenseAI.git
cd AutoSenseAI
pip install -r requirements.txt  # if requirements.txt exists
python template.py
Open your browser and navigate to:
http://localhost:5000