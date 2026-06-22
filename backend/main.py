# FastAPI imports - used to create the FastAPI application, add middleware, and mount static files
# database imports - used to create the database tables and import the models
# routers imports - used to include the API endpoints for each module
# os import - used to construct the path to the frontend static files

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import engine, Base
from backend.models import User  # Notice it says backend.models, NOT backend.database
            

from backend.routers import (
    auth, menu, orders, billing, inventory, 
    employees, customer, reservation, feedback, reports
)
import os

# Create the database tables using the models defined in the models.py file
# This will create the tables in the database specified in the DATABASE_URL environment variable
Base.metadata.create_all(bind=engine)

#  Create the FastAPI application and add CORS middleware to allow cross-origin requests from any origin
app = FastAPI(title="Monika G Cafe Management System API")

# Add CORS middleware to allow cross-origin requests from any origin, with any method and any header
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers for each module, which will add the API endpoints to the FastAPI application
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(billing.router)
app.include_router(inventory.router)
app.include_router(employees.router)
app.include_router(customer.router)
app.include_router(reservation.router)
app.include_router(feedback.router)
app.include_router(reports.router)


''' Construct the path to the frontend static files, which are located in the "frontend" directory 
 relative to this main.py file '''

frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "frontend"))
if os.path.exists(frontend_path):
    from fastapi.responses import RedirectResponse
    
    @app.get("/")
    def read_root():
        return RedirectResponse(url="/login.html")
        
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")