# vs_e_commerce6_ai

A full-stack e-commerce analytics dashboard with AI interaction — runnable locally or fully containerized with Docker.

This is a **Visual Studio Code** project built to practice modern full-stack development. It's an evolution of [e_commerce3](https://github.com/generateNscore/e_commerce3), now with support for both native execution and **Docker containerization**. This project is different from the previous in which a local AI agent without API key is added and no GPU required.

Once you verify the project works, you can use it as a solid, working boilerplate and customize it however you want.

> Preview: If your screen matches `screen.jpg`, setup succeeded.

### ✨ Key Features

- Full-stack web application with KPI dashboard and 3 analytics charts
- Auto-generated mock data for testing
- Dual run modes: Native Python and Docker Compose
- Interactive API documentation via Swagger UI
- Natural-language questions can be answered with a local AI agent

### 🛠 Tech Stack

- **Backend:** Python, FastAPI
- **Database:** PostgreSQL with SQLAlchemy
- **Frontend:** HTML / JS (served by FastAPI), RESTful API
- **DevOps:** Docker & Docker Compose
- **Data Model:** 5 related tables (see `e_commerce3_models.pptx` for ERD and details)
- **AI agent:** answer for natural-language questions

### 📋 Prerequisites

- [PyCharm](https://www.jetbrains.com/pycharm/) (or any Python IDE)
- [PostgreSQL](https://www.postgresql.org/download/) installed locally (for native mode)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for containerized mode)
- Python 3.10+

### ⚙️ Installation

**1. Clone the repository**

If you need help cloning into PyCharm: [Guide to cloning a GitHub repo in PyCharm](https://www.google.com/search?q=How+to+create+a+project+folder+in+PyCharm+with+a+GitHub+repository)

**2. Install dependencies**

Open the terminal in PyCharm and run:

```bash
pip install -r requirements.txt
```

## 🚀 Running the Project
You can run this project in two ways.

### Option 1: Native Mode (without Docker)

1. Create your .env file

Create a file named .env in the project root and add:

```env
DATABASE_URL=postgresql+psycopg2://postgres:{your_password}@localhost:5432/e_commerce_db
OLLAMA_BASE_URL=http://localhost:11434/v1 # locally
```
> Replace {your_password} with your local PostgreSQL password. This database e_commerce_db should be created in your local PostgreSQL.

2. Start the server

```Bash
uvicorn app.main:app --reload
```

When you see Application startup complete. in the logs, the server is ready on port 8000.

### Option 2: Docker Mode (Containerized)

1. Update your .env file

Comment out the previous lines and replace it with:

```env
DATABASE_URL=postgresql+psycopg2://postgres:{your_password}@db:5432/db_docker
POSTGRES_USER=postgres
POSTGRES_PASSWORD={your_password}
POSTGRES_DB=db_docker
OLLAMA_BASE_URL=http://ollama:11434/v1 # dockerized
```

> Replace {your_password} with the password you want to use.

> Note: Even if the DB name is similar, the Dockerized database is fully isolated from your local PC. It runs inside the db container.

2. Start with Docker Compose

Make sure Docker Desktop is running, then run:

```Bash
docker compose up --build
```

When you see Application startup complete., the server is ready — also on port 8000.

## 🌐 Accessing the Application
Once the server is running:

1. Frontend / Dashboard

```Code
http://127.0.0.1:8000
```

The main dashboard. It will show 0s initially until you generate data.

2. API Docs / Swagger UI

```Code
http://127.0.0.1:8000/docs
```

Interactive FastAPI documentation for testing all endpoints.

## 🗄️ Generating Initial Data
1. Open Swagger UI: http://127.0.0.1:8000/docs
2. You will find two admin endpoints: POST /admin/recreate_tables and POST /admin/generate_add_data
3. Recreate Tables: Click Try it out -> Execute on /admin/recreate_tables. This will drop all existing tables and recreate them from the SQLAlchemy metadata.
4. Generate Data: Click Try it out on /admin/generate_add_data. You will be prompted for

<ul>
   <li> customer_count: number of customers</li>
   <li> product_count: [category_count, products_per_category] e.g., [5, 20]</li> 
   <li> order_count: number of orders</li>
   <li> city_count: number of cities</li>
</ul>

5. Click Execute to populate the database.
6. Refresh http://127.0.0.1:8000 — you should now see KPIs and 3 charts populated with your generated data.


## 📄 License
MIT License - free for personal and commercial use.

Made to be cloned and run instantly. If you get the same screen as `screen.jpg`, setup succeeded.
![Preview](screen.jpg)
