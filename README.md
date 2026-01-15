# AI-Powered English Assessment System

This project is a modern **FastAPI**-based exam system designed to assess students' English skills (Reading, Listening, Writing, Speaking) with AI support.

The system utilizes **Google Gemini** (Writing analysis) and **OpenAI Whisper** (Audio analysis) models. It features a **"Fail-Safe"** hybrid architecture that activates during API interruptions.

## Features

* **4 Core Skills:** Reading, Listening, Writing, Speaking.
* **Hybrid AI Scoring:**
    * **Writing:** Detailed grammar and content analysis via Google Gemini API. (Fallback: Rule-Based Algorithm).
    * **Speaking:** Speech-to-Text (STT) and content analysis using Whisper.
* **Admin Panel:** Question adding, user management, manual scoring.
* **Fail-Safe Architecture:** The system does not crash during internet or quota issues; it generates scores using mathematical analysis.

## Technologies Used

* **Backend:** Python, FastAPI, Uvicorn
* **Database:** MySQL (SQLAlchemy)
* **AI:** `google-genai`, `openai-whisper`, `spacy`, `textstat`
* **Frontend:** HTML5, CSS3, JavaScript

## Installation

Follow these steps to run the project on your computer:

### 1. Clone the Project
```bash
git clone [https://github.com/YOUR_USERNAME/PROJECT_NAME.git](https://github.com/YOUR_USERNAME/PROJECT_NAME.git)
cd PROJECT_NAME
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# Mac/Linux için:
source venv/bin/activate

```

### 3. Install Libraries
```bash
pip install -r requirements.txt
```

### 4. Download Language Model (Spacy)
```bash
python -m spacy download en_core_web_sm
```

### 5. FFmpeg Installation (For Speaking)
* FFmpeg must be installed and added to PATH for Whisper to process audio.
   * Windows: Download FFmpeg, add the bin folder to Environment Variables (Path).
   * Linux: sudo apt install ffmpeg



### 6. Create .env File
```bash
DATABASE_URL=mysql+pymysql://root:sifreniz@localhost/db_adi
GEMINI_API_KEY=BURAYA_GOOGLE_AI_STUDIO_KEY_GELECEK
SECRET_KEY=gizli_anahtariniz_buraya
```

## Usage
```bash
uvicorn main:app --reload
```
* Go to the following address in your browser: http://127.0.0.1:8000
   *	Admin Login: (If created in the database)
   *	Register: You can create a new student record from the /register.html page.oluşturabilirsiniz.

 
##  Project Structure
 
```text
├── src/
│   ├── models/          # Database tables (SQLAlchemy)
│   ├── services/        # Business logic (AI Service, Exam Service)
│   ├── static/          # HTML, CSS, JS, and Uploaded Files
│   ├── schemas/         # Pydantic models & Data validation
│   ├── repositories/    # Database CRUD operations
│   ├── api/             # API Routes and Endpoints
│   ├── static/audio     # User voice recordings storage
│   ├── templates        # HTML templates for UI
│   ├── database.py      # DB connection for python
│   └── utils            # Helper functions and utilities
├── main.py              # Application entry point
├── requirements.txt     # Project dependencies list
└── README.md            # Project documentation
```


## Fail-Safe AI Architecture 
This project is resilient against API interruptions:
1.	The system first attempts to connect to the Google Gemini API.
2.	If the quota is exceeded or the connection fails, "Hybrid Mode" activates.
3.	A mathematical score is generated based on text length, vocabulary diversity, readability (Flesch Index), and keyword usage.
4.	The user experiences no interruption and successfully completes the exam.


## Project Team & Contact Info 
This project was developed by the following team members. Click on numbers or email addresses to contact.

| Name Surname | GitHub | WhatsApp | Email |
| :--- | :---: | :--- | :--- |
| Metehan Yeter | [🔗 Profil](https://github.com/MthnYtr) | [📱 0549 650 42 60](https://wa.me/905496504260) | [📧 s220204039@ankarabilim.edu.tr](mailto:s220204039@ankarabilim.edu.tr) |
| Fatih Oğuz Kaya | [🔗 Profil](https://github.com/fatihoguzkaya) | [📱 0546 611 98 21](https://wa.me/905466119821) | [📧 s220204056@ankarabilim.edu.tr](mailto:s220204056@ankarabilim.edu.tr) |
| Esma Azra Şahin | [🔗 Profil](https://github.com/azrashn) | [📱 0553 953 13 43](https://wa.me/905539531343) | [📧 s220204036@ankarabilim.edu.tr](mailto:s220204036@ankarabilim.edu.tr) |
| Anday Turgut | [🔗 Profil](https://github.com/andayk) | [📱 0530 890 22 05](https://wa.me/905308902205) | [📧 s220204050@ankarabilim.edu.tr](mailto:s220204050@ankarabilim.edu.tr) |
| Çağatay Samed Şahin | [🔗 Profil](https://github.com/CgtyShn10) | [📱 0507 159 59 90](https://wa.me/905071595990) | [📧 s220201048@ankarabilim.edu.tr](mailto:s220201048@ankarabilim.edu.tr) |
| Alaaddin Büyüksakallı | [🔗 Profil](https://github.com/Genos095) | [📱 0542 836 90 34](https://wa.me/905428369034) | [📧 s220204028@ankarabilim.edu.tr](mailto:s220204028@ankarabilim.edu.tr) |