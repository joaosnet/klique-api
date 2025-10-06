"""
Módulo de agendamento de tarefas usando APScheduler.

Este módulo configura e gerencia tarefas agendadas para a aplicação,
incluindo o envio diário de resumos do SIGAA via WhatsApp.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from .agents.tasks import trigger_sigaa_summary_agent
from .config import SCHEDULED_TASKS_USER_NUMBER
from .services.shared import AppServices

# Instância global do scheduler
scheduler = AsyncIOScheduler(timezone='America/Sao_Paulo')


async def setup_scheduler() -> None:
    """
    Configura as tarefas agendadas no scheduler.

    Esta função deve ser chamada durante a inicialização da aplicação
    para registrar todas as tarefas recorrentes.
    """
    try:
        logger.info('⏰ Configurando tarefas agendadas...')

        # Tarefa: Envio diário de resumo do SIGAA às 12:00
        scheduler.add_job(
            func=_send_daily_sigaa_summary,
            trigger=CronTrigger(hour=12, minute=0),  # Todos os dias às 12:00
            id='daily_sigaa_summary',
            name='Resumo Diário SIGAA',
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,  # Tolerar até 5 minutos de atraso
        )

        logger.success('✅ Tarefas agendadas configuradas com sucesso')

    except Exception as e:
        logger.error(f'❌ Erro ao configurar tarefas agendadas: {e}')
        raise


async def _send_daily_sigaa_summary() -> None:
    """
    Tarefa agendada para enviar resumo diário dos avisos do SIGAA.

    Esta função é executada automaticamente todos os dias às 12:00
    e envia um resumo dos avisos do SIGAA para o usuário configurado.
    """
    try:
        logger.info('📅 Executando tarefa agendada: resumo diário do SIGAA')

        # Obtém o serviço WhatsApp
        whatsapp_service = AppServices.get_whatsapp_service()

        # Executa a tarefa de resumo do SIGAA
        result = await trigger_sigaa_summary_agent(
            user_number=SCHEDULED_TASKS_USER_NUMBER,
            whatsapp_service=whatsapp_service,
        )

        if result['status'] == 'ok':
            logger.success('✅ Resumo diário do SIGAA enviado com sucesso')
        else:
            logger.error(
                f'❌ Falha no envio do resumo diário: {result["detail"]}'
            )

    except Exception as e:
        logger.error(f'❌ Erro na tarefa agendada do SIGAA: {e}')
        logger.exception('Detalhes do erro:')


async def start_scheduler() -> None:
    """
    Inicia o scheduler de tarefas agendadas.

    Esta função deve ser chamada durante o startup da aplicação.
    """
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info('🚀 Scheduler de tarefas iniciado')
        else:
            logger.warning('⚠️ Scheduler já está em execução')
    except Exception as e:
        logger.error(f'❌ Erro ao iniciar scheduler: {e}')
        raise


async def stop_scheduler() -> None:
    """
    Para o scheduler de tarefas agendadas.

    Esta função deve ser chamada durante o shutdown da aplicação.
    """
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)
            logger.info('🛑 Scheduler de tarefas parado')
        else:
            logger.info('📋 Scheduler não estava em execução')
    except Exception as e:
        logger.error(f'❌ Erro ao parar scheduler: {e}')
        raise


def get_scheduler_status() -> dict:
    """
    Retorna o status atual do scheduler.

    :return: Dicionário com informações sobre o estado do scheduler
    """
    return {
        'running': scheduler.running,
        'jobs_count': len(scheduler.get_jobs()),
        'timezone': str(scheduler.timezone),
    }
