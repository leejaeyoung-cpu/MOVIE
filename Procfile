# Procfile for deploying both backend and frontend

# Backend API (FastAPI with uvicorn)
web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Frontend (Streamlit) - for separate deployment
# streamlit: cd frontend && streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
