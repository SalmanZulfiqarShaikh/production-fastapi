# Header-Based Authentication API

A secure REST API built with **FastAPI** that uses custom header-based authentication.

## Features
* Fast and lightweight asynchronous performance with FastAPI.
* Custom HTTP header validation for secure endpoint access.
* Automatic interactive documentation via Swagger UI.

## Requirements
* Python 3.8+
* FastAPI
* Uvicorn

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install fastapi uvicorn
   ```

## Running the Application

Start the development server using Uvicorn:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Authentication

Every protected request must include your secret token in the custom header:
* **Header Name:** `x-api-key`
* **Header Value:** `your-secret-token`

## Example Request

You can test the protected endpoint using `curl`:
```bash
curl -X 'GET' \
  'http://127.0.0' \
  -H 'accept: application/json' \
  -H 'x-api-key: your-secret-token'
```

## API Documentation
Once the server is running, open your browser and go to:
* **Swagger UI:** `http://127.0.0`
* **Redoc:** `http://127.0.0`
