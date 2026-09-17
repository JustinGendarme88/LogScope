from fastapi import FastAPI

app = FastAPI(
    title="LogScope API",
    description="API for uploading and analyzing server log files.",
    version="1.0.0",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to LogScope API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}