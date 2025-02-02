# Profiler Tool

## Introduction  
Profiler Tool is a web application designed for entity extraction and profiling from uploaded PDF files. It allows users to upload PDFs, extract named entities, visualize relationships in a network graph, and perform entity-based searches.

This tool utilizes **Flask** for the backend, **MongoDB** for data storage, and **Vue.js** for the frontend. Additionally, **D3.js** is used for network graph visualization.

---

## Features  

### **Frontend** (Vue.js)  
- Upload multiple PDF files.  
- Search and filter extracted entities.  
- View extracted details, including associated crimes, jobs, and locations.  
- Interactive **network graph visualization** of entities and their relationships.  

### **Backend** (Flask)  
- Extracts text from PDFs using **PyMuPDF (Fitz)**.  
- Processes text with **spaCy** to detect named entities.  
- Stores extracted data in **MongoDB**.  
- Provides **RESTful API** endpoints for file and entity retrieval.  
- Handles **CORS** to enable frontend-backend communication.  

---

## **Tech Stack**
- **Frontend:** Vue.js, TailwindCSS, D3.js  
- **Backend:** Flask, MongoDB, spaCy, PyMuPDF  
- **Database:** MongoDB  

---

## **Setup Instructions**  

### **1. Clone the Repository**  
### **2. Backend Setup**  
cd server
pip install -r requirements.txt
1. Ensure Ensure you have a MongoDB database running.
2. Create a .env file inside the server directory and add your MongoDB URI:
MONGO_URI=mongodb+srv://yourusername:yourpassword@yourcluster.mongodb.net/yourdb

python backend.py

### **3. Frontend Setup** 
cd client
npm install
npm run serve
