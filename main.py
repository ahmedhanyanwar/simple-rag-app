from fastapi import FastAPI
app = FastAPI()


@app.get("/welcome")
def wolcome():
    return {
        "massage": "Hello World!"
    }
    

