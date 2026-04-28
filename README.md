# 🚀 CareerForge AI

AI-powered resume generator using NLP to create job-specific, professional resumes from user skills and experience. Fast, accurate, and ATS-friendly.

---

## ✨ Features

- 🤖 AI-powered resume generation using NLP
- 📄 Job-specific resume customization
- ✅ ATS-friendly formatting
- ⚡ Fast processing
- 🎯 Professional output

---

## 📋 Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/hinal010/careerforge-ai.git
cd careerforge-ai
```

### 2️⃣ Create Virtual Environment

```bash
# Linux / Mac
python -m venv venv
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root directory and add the following environment variables:

```env
# Google OAuth Configuration
CLIENT_ID=your_google_client_id
CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/auth/callback

# JWT Authentication
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
SESSION_SECRET_KEY=your_session_secret_key

# Admin Credentials
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_secure_password

# Gemini AI API
GEMINI_API_KEY=your_gemini_api_key

# Email Configuration
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_email_password_or_app_password
```

**⚠️ Security Note**: 
- Never commit `.env` file to version control (it's already in `.gitignore`)
- Keep your API keys and secrets safe
- Use environment-specific values for development and production

---

### 5️⃣ Run Backend Server

```bash
uvicorn main:app --reload
```

### 6️⃣ Open Application

Visit: http://127.0.0.1:8000

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **NLP**: Natural Language Processing
- **Authentication**: Google OAuth, JWT
- **AI/ML**: Google Gemini API
- **Email**: SMTP Email Service

---

## 📚 Usage

1. Start the application following the installation steps
2. Upload your skills and experience
3. Select target job description
4. AI generates optimized resume
5. Download in your preferred format


