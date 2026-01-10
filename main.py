import uvicorn
from fastapi import FastAPI
app=FastAPI()


# 添加首页
@app.get("/")
def index():
    "这里是首页"
    return "This is Home Page."

@app.get("/users")
def users():
    return {"msg":"get all users", "code":200}

if __name__ == '__main__':
    uvicorn.run(app)