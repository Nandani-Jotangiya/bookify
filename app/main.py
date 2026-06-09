from fastapi import FastAPI

# This variable name must match the name in your terminal command
app = FastAPI() 

@app.get("/")
def home():
    return {"message": "Working!"}
