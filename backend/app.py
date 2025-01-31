from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import main

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://<extension-id>",  # Replace with your extension ID
        "http://localhost",  # Allow requests from localhost (for testing)
    ],
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    allow_credentials=True,  # Allow cookies and credentials
)

# Include routers
app.include_router(main.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Generative AI Web Scraper API!"}
