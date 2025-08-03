from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from search import find_buses

app = FastAPI()

# Allow Streamlit to access FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "Bus agent is running"}

@app.get("/bus")
def get_bus_info(destination: str = Query(..., min_length=2)):
    result = find_buses(destination)
    if result:
        return result
    return {"message": f"No buses found for '{destination}'."}