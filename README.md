# Enterprise Reporting and Integration Portal

A high-performance, full-stack platform for transforming, validating, and distributing enterprise data.

## 🚀 Overview
This portal connects SQL Server data sources to a modern web interface. It features automated Python-based ETL pipelines, a robust C# API, and a premium vanilla JS dashboard.

## 📁 Project Structure
- **/src/Api**: ASP.NET Core 8 Web API (Dapper, JWT, Background Service)
- **/src/Scripts**: Python ETL scripts (Ingestion, Validation, Transformation, Reporting)
- **/src/Web**: Frontend Dashboard (Vanilla HTML/CSS/JS)
- **/sql**: Database schema, stored procedures, and seed data

## 🛠️ Prerequisites
- .NET 8 SDK
- Python 3.11+
- Docker (for SQL Server)
- ODBC Driver 18 for SQL Server

## ⚙️ Local Setup

### 1. Database
Start the SQL Server container:
```bash
docker-compose up -d sqlserver
```
Run the SQL scripts in order:
1. `sql/schema.sql`
2. `sql/stored_procedures/operations.sql`
3. `sql/views/reporting_views.sql`
4. `sql/seed_data.sql`

### 2. Python Environment
```bash
cd src/Scripts
pip install -r requirements.txt
```

### 3. C# API
```bash
cd src/Api
dotnet restore
dotnet run
```

### 4. Frontend
Simply open `src/Web/index.html` in your browser.

## 🔄 End-to-End Flow
1. **Upload**: Drag a CSV into the **Upload Data** page.
2. **Sync**: Run the Python scheduler to process raw data:
   ```bash
   python3 src/Scripts/scheduler.py --full-sync --file source.csv --source ERP_SYS
   ```
3. **Report**: Go to the **Reports** page and click **Run New Report**.
4. **Download**: Once the status hits "Completed", click **Download**.

## 🔒 Authentication
- **Default User**: `admin`
- **Default Password**: `password123`
