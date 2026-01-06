from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, cases, chat, documents

app = FastAPI(
    title="LexGuard API",
    description="Backend for LexGuard AI Corporate Lawyer",
    version="1.0.0"
)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(chat.router)
app.include_router(documents.router)

@app.get("/")
async def root():
    return {"message": "LexGuard API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)