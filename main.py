from fastapi import FastAPI

# from fastapi.middleware.cors import CORSMiddleware
from src.routers import auth, register, whatsapp

app = FastAPI(title='Klique AI API', version='1.0.0')


# origins = [
#     'http://localhost.tiangolo.com',
#     'https://localhost.tiangolo.com',
#     'http://localhost',
#     'http://localhost:8080',
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*'],
# )

app.include_router(auth.router)
app.include_router(register.router)
app.include_router(whatsapp.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
