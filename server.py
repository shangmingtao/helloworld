"""
服务器启动脚本
"""
import uvicorn
from webproject.main import app

if __name__ == "__main__":
    print("启动用户管理后台服务...")
    print("API文档地址: http://localhost:8000/docs")
    print("健康检查: http://localhost:8000/health")
    
    uvicorn.run(
        "webproject.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )