from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rapidfuzz import process, fuzz

app = FastAPI()

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_homepage():
    """Serve the chatbot UI"""
    return FileResponse("static/index.html")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session storage to remember previous queries
session_memory = {"last_city": None}  # Ensure last_city exists

# Predefined responses
responses = {
    "hello": "Hi there! How can I assist you with traffic updates?",
    "traffic condition": "Traffic is moderate in most areas. Any specific location?",
    "best route": "The best route depends on your location. Can you specify your starting point?",
    "default": "I'm not sure about that. Can you rephrase?"
}

# City-specific traffic data
city_traffic = {
    "hyderabad": "Traffic in Hyderabad is heavy during peak hours near Hitech City and Gachibowli.",
    "mumbai": "Mumbai has slow-moving traffic in South Mumbai and Bandra during rush hours.",
    "delhi": "Delhi experiences congestion near Connaught Place and India Gate during evenings.",
}

# Request model
class ChatRequest(BaseModel):
    query: str

def get_best_response(user_query: str) -> str:
    """Find best fuzzy-matching response"""
    result = process.extractOne(user_query, responses.keys(), scorer=fuzz.ratio)
    if result:
        best_match, score = result[:2]
        if score > 60:
            return responses[best_match]
    return responses["default"]

def check_for_city(user_query: str):
    """Use fuzzy matching to detect a city in the query."""
    best_match = process.extractOne(user_query, city_traffic.keys(), scorer=fuzz.partial_ratio)
    
    if best_match:
        city, score = best_match[:2]
        if score > 75:  # Adjusted threshold for better typo handling
            return city_traffic[city], city
    
    return None, None

@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle user messages and return intelligent responses."""
    user_query = request.query.lower()

    # Check if query is about a city
    city_response, city = check_for_city(user_query)
    
    if city:
        session_memory["last_city"] = city  # Store last city in memory
        return JSONResponse(content={"response": city_response})

    # If the last query was city-related and the new query is traffic-related, respond with last known city
    if session_memory["last_city"] and "traffic" in user_query:
        last_city = session_memory["last_city"]
        return JSONResponse(content={"response": f"Since you last asked, traffic in {last_city} remains similar: {city_traffic[last_city]}."})

    # If the query is general (like "hello", "error"), return a normal response
    general_response = get_best_response(user_query)
    return JSONResponse(content={"response": general_response})
