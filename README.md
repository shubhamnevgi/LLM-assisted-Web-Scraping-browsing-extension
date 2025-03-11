# Generative AI-based Web Scraping Browser Extension  

## 📌 Project Overview  
 A Generative AI-powered Web Scraping Browser Extension using FastAPI, BeautifulSoup, Selenium, and Llama 3.3 with LangChain (Groq's model). It extracts and structures web data, allowing users to input URLs, scrape dynamic content, and download data in CSV, JSON, XML, and Excel formats with AI-based parsing and future scalability.

---

This project is a **Generative AI-powered Web Scraping Browser Extension** that enables users to extract data from websites efficiently. The extension allows users to input URLs, scrape web data dynamically, and format it into structured formats such as **CSV, JSON, XML, and Excel**. It integrates a **FastAPI backend** for handling scraping operations and AI-based data parsing.  

## 🚀 Features  
- **Web Scraping**: Extracts data from static and dynamic web pages using **BeautifulSoup** and **Selenium**.  
- **AI-Powered Parsing**: Utilizes **Llama 3.3 with LangChain (Groq's model)** for intelligent data processing and structuring.  
- **Multiple Data Formats**: Supports **CSV, JSON, XML, and Excel** downloads.  
- **Browser Extension Interface**: Allows users to input URLs, manage scraping settings, and download data in the preferred format.  
- **FastAPI Backend**: Ensures seamless communication between the extension and the AI-powered backend.  

## 📂 Project Structure  
```
project/
├── backend/                            # FastAPI Backend
│   ├── app.py                          # Main FastAPI app
│   ├── models.py                       # Data models and schemas
│   ├── services/                       # Business logic like scraping, parsing
│   │   ├── __init__.py                 # Make the folder a Python package
│   │   ├── scrape.py                   # Web scraping logic
│   │   └── parse.py                    # Parsing logic (AI-based, HuggingFace)
│   ├── routers/                        # API routes (FastAPI routes)
│   │   ├── __init__.py                 # Make the folder a Python package
│   │   ├── main.py                     # Routes for scraping and parsing
│   │   └── visualize.py                # Route for data visualization (if needed)
│   ├── static/                         # Static files (graphs, temporary data files)
│   ├── requirements.txt                # Python dependencies
├── extension/                          # Browser Extension
│   ├── manifest.json                   # Extension configuration (defines permissions, etc.)
│   ├── popup.html                      # Popup UI for the extension
│   ├── popup.js                        # JavaScript to interact with the backend (API requests)
│   └── styles.css                      # Styling for the extension's popup
├── web_app/                            # Optional: Web application for data visualization
│   ├── app.py                          # Main backend (FastAPI)
│   ├── templates/                      # HTML templates for frontend
│   ├── static/                         # Static files for the web app
│   ├── requirements.txt                # Python dependencies
```

## 🛠️ Technologies Used  
- **Backend**: Python, FastAPI, BeautifulSoup, Selenium, Llama 3.3 with LangChain (Groq's model)  
- **Browser Extension**: HTML, JavaScript (Manifest V3)  
- **Data Formats**: CSV, JSON, XML, Excel  

## 📌 How to Get Started  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/yourusername/Generative-AI-based-Web-Scraping-browsing-extension.git
cd Generative-AI-based-Web-Scraping-browsing-extension
```

### 2️⃣ Create a virtual environment  
Create a virtual environment:  
```bash
python -m venv venv
```
Activate this virtual environment:  
```bash
venv\Scripts\activate     # On Windows
source venv/bin/activate  # On Linux/Mac
```

### 3️⃣ Setup Backend  
Install dependencies:  
```bash
pip install -r backend/requirements.txt
```

### 4️⃣ Set up environment variables
Create a .env file in the root directory.
Add your Groq API key:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 5️⃣ Run FastAPI backend:  
```bash
<<<<<<< HEAD
uvicorn backend.app:app --reload
=======
uvicorn backend.main:app --reload
>>>>>>> 591b0eda9c46a1bfc7af3ef912a20ece51fe5fdf
```

### 6️⃣ Load Browser Extension  
1. Open **Chrome** and go to `chrome://extensions/`.  
2. Enable **Developer Mode** (top right corner).  
3. Click **Load Unpacked** and select the `extension/` folder.  
4. The extension should now be active in your browser.  

---
