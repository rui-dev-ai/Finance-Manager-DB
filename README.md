# 💰 Budget-Brain — Smart Finance Manager

<div align="center">

![BudgetBrain Banner](screenshots/dashboard.png)

**A full-stack personal finance management system with AI-powered spending predictions.**

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-REST%20API-black?style=flat-square&logo=flask)
![SQL Server](https://img.shields.io/badge/SQL%20Server-Database-red?style=flat-square&logo=microsoft-sql-server)
![HTML CSS JS](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-orange?style=flat-square&logo=html5)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=flat-square&logo=bootstrap)

</div>

---

## 📌 Project Overview

**Budget-Brain** is a comprehensive database-driven web application developed as part of the PBL (Project-Based Learning) for **CS160 — Database Systems** at **National University of Technology (NUTech)**, Department of Artificial Intelligence, Batch AI-25B.

The system allows users to track daily expenses, set monthly budgets, monitor savings goals, and receive AI-powered spending predictions — all through a clean and responsive web dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 User Authentication | Secure login and account creation with password hashing |
| 💸 Expense Tracking | Full CRUD — add, edit, delete, and view all expenses |
| 📊 Budget Monitoring | Set monthly limits and get real-time feedback |
| 🤖 AI Spending Prediction | Forecast next month's spending using weighted rolling average |
| 🎯 Savings Goals | Create and track personalized savings milestones |
| 📈 Visual Analytics | Interactive pie, bar, and line charts via ApexCharts |

---

## 🖼️ Screenshots

### Login & Sign Up
<div align="center">
<img src="screenshots/login.png" width="45%" />
<img src="screenshots/creating_acc.png" width="45%" />
</div>

### Dashboard
<div align="center">
<img src="screenshots/dashboard.png" width="90%" />
</div>

### Expense Tracking
<div align="center">
<img src="screenshots/expenses.png" width="45%" />
<img src="screenshots/adding_expenses.png" width="45%" />
</div>

### Analytics & Predictions
<div align="center">
<img src="screenshots/charts_dashboard.png" width="45%" />
<img src="screenshots/prediction.png" width="45%" />
</div>

### Savings Goals
<div align="center">
<img src="screenshots/goals.png" width="45%" />
<img src="screenshots/saving_amount.png" width="45%" />
</div>

---

## 🗄️ Database Design

### ERD Diagram
<div align="center">
<img src="screenshots/erd.png" width="80%" />
</div>

### Core Tables

| Table | Description |
|---|---|
| `Users` | Account identity, credentials, and monthly income |
| `Categories` | Expense classification labels with budget limits |
| `Expenses` | All transactional records (weak entity) |
| `AI_Prediction` | Stored forecast results (associative entity) |
| `Savings_Goal` | User-defined financial targets (weak entity) |

### Normalization
All tables are normalized to **Third Normal Form (3NF)**:
- No partial dependencies
- No transitive dependencies
- Categories and Users are separate tables — no redundancy
- Primary and foreign key constraints enforced across all tables

---

## 🛠️ Tech Stack

### Frontend
- **HTML5** — Semantic structure and markup
- **Bootstrap 5** — Responsive layout and UI components
- **JavaScript** — Dynamic interactions and API calls
- **ApexCharts** — Interactive financial visualizations

### Backend
- **Python Flask** — Lightweight REST API framework
- **Flask-CORS** — Cross-origin request handling
- **PyODBC** — Database connectivity layer

### Database
- **Microsoft SQL Server** — Relational data storage and management

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/summary` | GET | Returns total income, expenses, and balance |
| `/api/expenses` | GET / POST / PUT / DELETE | Full CRUD for expense records |
| `/api/categories` | GET | Fetch and manage expense categories |
| `/api/predict` | GET | Returns AI-generated spending forecast |
| `/api/goals` | GET / POST | Create and monitor savings goals |

---

## 🤖 AI Prediction Engine

```
INPUT   → Average spending across last 3 months from database
PROCESS → Weighted rolling average via /api/predict endpoint  
OUTPUT  → Predicted amount + confidence percentage + forecast month
```

The AI prediction uses a **weighted rolling average** — recent months carry more weight than older ones, giving a more accurate forecast of future spending behavior.

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.12+
- Microsoft SQL Server
- SQL Server Management Studio (SSMS)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/rui-dev-ai/Finance-Manager-DB.git
cd Finance-Manager-DB

# 2. Install dependencies
pip install flask flask-cors pyodbc

# 3. Set up database
# Open SSMS and run PBL.sql to create all tables

# 4. Configure database connection
# Edit db_config.py with your SQL Server details

# 5. Run the app
python app.py

# 6. Open in browser
# Go to http://localhost:5000/login.html
```

---

## 👥 Team

| Member | Role |
|---|---|
| **Syed Ruidar Ali Shah** | ERD Design & Database Schema |
| **Anus Manan** | SQL Tables, Data Insertion & Queries |
| **Shaban** | Flask REST API Development |
| **Hashir** | Frontend Dashboard Development |
| **Azfar** | Testing, Bug Fixing & Validation |

---

## 🏫 Project Info

| | |
|---|---|
| **University** | National University of Technology (NUTech) |
| **Department** | Artificial Intelligence |
| **Course** | CS160 — Database Systems |
| **Instructor** | Ms. Sumera Aslam |
| **Batch** | AI-25 B — Spring 2026 |

---

<div align="center">
<i>Combining finance and artificial intelligence to build smarter financial futures.</i>
</div>
