from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import close_db_connection, get_client
from .routers import auth, register, scheduler, whatsapp
from .scheduler import setup_scheduler, start_scheduler, stop_scheduler
from .services.whatsapp import WhatsAppService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida do FastAPI para inicializar e
    encerrar os serviços da aplicação.
    """
    # Inicializa o cliente do banco de dados no startup
    app.state.db_client = get_client()

    # Inicializa o serviço do WhatsApp
    whatsapp_service = WhatsAppService()
    app.state.whatsapp_service = whatsapp_service

    # Inicializa o serviço Gemini WebAPI
    # gemini_web_api_service = GeminiWebApiService()
    # await gemini_web_api_service._initialize_client()  # noqa: SLF001
    # app.state.gemini_web_api_service = gemini_web_api_service

    # Configura e inicia o scheduler de tarefas agendadas
    await setup_scheduler()
    await start_scheduler()

    yield

    # Encerra os serviços ao finalizar a aplicação
    await stop_scheduler()
    await whatsapp_service.close()
    # await gemini_web_api_service.close()
    close_db_connection()


app = FastAPI(title='Klique AI API', version='1.0.0', lifespan=lifespan)


origins = [
    'http://localhost.tiangolo.com',
    'https://localhost.tiangolo.com',
    'http://localhost',
    'http://localhost:8080',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth.router)
app.include_router(register.router)
app.include_router(scheduler.router)
app.include_router(whatsapp.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
