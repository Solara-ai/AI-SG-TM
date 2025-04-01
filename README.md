# Time-Flow API

## Introduction
This is an API system developed using FastAPI and MongoDB, supporting scheduling and AI conversation management.

## Directory Structure
```
├── core
│   ├── __init__.py
│   ├── request_logger.py       # Middleware for logging requests
│
├── database
│   ├── __init__.py
│   ├── mongo_services.py       # MongoDB connection and operations
│
├── models
│   ├── __init__.py
│   ├── event_model.py          # Defines data models
│
├── routes
│   ├── __init__.py
│   ├── chat_router.py          # API for conversations
│   ├── statistics_router.py    # API for statistics
│   ├── suggestion_router.py    # API for AI suggestions
│
├── schemas
│   ├── __init__.py
│   ├── schemas.py              # Defines request/response schemas
│
├── services
│   ├── __init__.py
│   ├── ai_service.py           # Handles AI logic
│   ├── statistics_service.py   # Handles statistics logic
│
├── utils
│   ├── __init__.py
│   ├── logger.py               # Logging configuration
│   ├── schedule_utils.py       # Utility functions for scheduling
│
├── .env                        # Environment variables
├── .gitignore                  # Git ignore file
├── config.py                   # System configuration
├── main.py                     # Main entry point of the application
├── README.md                   # User guide
```

## Installation
### System Requirements
- Python 3.9+
- MongoDB
- pip (or use venv/conda)

### Install Dependencies
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
2. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
1. Create a `.env` file with the following template:
   ```env
   MONGO_URI=mongodb://localhost:27017
   DATABASE_NAME=timeflow
   ```
2. Modify the necessary values according to your system.

## Running the Application
1. Start MongoDB if it is not already running:
   ```bash
   mongod --dbpath /path/to/data/db
   ```
2. Run FastAPI:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Testing
Once running, access:
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Contribution
1. Fork this repository.
2. Create a new branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m "Description of changes"`
4. Push to the repository: `git push origin feature-name`
5. Create a Pull Request

## Contact
If you encounter any issues or have suggestions, open an issue on GitHub or contact via email.

