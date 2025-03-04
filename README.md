# Paperlens Multimodal RAG Bot

![WIP](https://img.shields.io/badge/WIP-Work%20In%20Progress-blue)
![Build](https://github.com/Rahul2991/PaperLens_Multimodal_RAG/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11.10-blue.svg)
![License](https://img.shields.io/github/license/Rahul2991/PaperLens_Multimodal_RAG)


PaperLens Multimodal RAG Bot is an AI-powered chatbot supporting text and image-based interactions using FastAPI, React, Ollama, Qdrant, and Llama 3.2 Vision. It offers:

- ✅ No-RAG Chat (Regular Chat Mode)
- ✅ File-Based RAG Chat (RAG Mode with Uploaded Files)
- ✅ Search Everything RAG Chat (Retrieval from All Sources)
- ✅ Admin Panel (User Management & Settings)
- ✅ JWT Authentication with SQLite
- ✅ MongoDB for Chat Data Storage

## 🛠️ Tech Stack
- **Backend**: FastAPI, Ollama, Qdrant, Llama 3.2 Vision
- **Frontend**: React.js
- **Database**: MongoDB (Chat Data), SQLite (Auth)
- **Auth**: JWT-Based Authentication

## 📂 Project Structure
```
📦 multimodal-rag-bot
├── backend/              # FastAPI Backend
│   ├── main.py           # API Endpoints
│   ├── auth/             # JWT Authentication
│   ├── models/           # SQLite & MongoDB Setup
│   ├── rag_modules/      # RAG and bot Logic
│   ├── schemas/          # Pydantic Models
│   ├── routes/           # API Routes
│   ├── tests/            # Unit tests
│   ├── requirements.txt  # Python Dependencies
│   └── services/         # Service Logic
│
├── frontend/             # React.js Frontend
│   ├── src/              # Components & Pages
│   │   ├── components/   # UI Components
│   │   └── pages/        # Page Layouts
│   ├── package.json      # Frontend Dependencies
│   └── App.js            # Main App Entry
└── README.md           # Documentation
```

## 🚀 Getting Started
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Rahul2991/PaperLens_Multimodal_RAG.git
cd PaperLens_Multimodal_RAG
```
### 2️⃣ Install Dependencies
#### Prerequisites
Ensure you have:
- Python 3.11.10 installed in a conda environment
- Docker Installed [Get it here](https://docs.docker.com/engine/install/)

#### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
conda install -c conda-forge tesseract==5.5.0
conda install -c conda-forge poppler==24.12.0
```
#### Install PyTorch
Follow the [official PyTorch installation guide](https://pytorch.org/get-started/locally/) to install the appropriate version based on your system and CUDA setup.

#### Install Ollama
Download and install Ollama from the [official website](https://ollama.com/download).
After installation, pull the required model:
```bash
ollama pull llama3.2-vision
```
#### Frontend (React.js)
```bash
cd frontend
npm install
```

### 3️⃣ Run the Project
#### 🏃‍♂️ Start Backend
```bash
cd backend
uvicorn main:app --reload
```
#### Start Qdrant Vector DB
```bash
docker run -p 6333:6333 -p 6334:6334 -v "${PWD}/qdrant_storage:/qdrant/storage" qdrant/qdrant
```

#### 🏃‍♂️ Start Frontend
```bash
cd frontend
npm start
```
- React App: [http://localhost:3000](http://localhost:3000)

## 🔑 Authentication & Roles
- **Users**: Can chat in different modes and upload files.
- **Admins**: Can chat in different modes, manage users and upload files.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

