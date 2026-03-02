"""
Módulo de agendamento de tarefas usando APScheduler.

Agenda lembretes diários de revisão SRS via WhatsApp para
usuários com cards vencidos today.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from .database import get_reviews_collection, get_users_collection
from .services.shared import AppServices

# Timezone do Brasil
BRAZIL_TZ = 'America/Sao_Paulo'

# Instância global do scheduler
scheduler = AsyncIOScheduler(timezone=BRAZIL_TZ)


async def setup_scheduler() -> None:
    """
    Configura as tarefas agendadas no scheduler.
    """
    try:
        logger.info('Configurando tarefas agendadas...')

        # Lembrete SRS diário às 21h BRT
        scheduler.add_job(
            func=_send_srs_daily_reminder,
            trigger=CronTrigger(hour=21, minute=0),
            id='srs_daily_reminder',
            name='Lembrete SRS Diário',
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )

        logger.success('Tarefas agendadas configuradas com sucesso')

    except Exception as e:
        logger.error(f'Erro ao configurar tarefas agendadas: {e}')
        raise


async def _send_srs_daily_reminder() -> None:
    """
    Envia mensagem WhatsApp para usuários com cards vencidos hoje.
    """
    try:
        agora = datetime.now(ZoneInfo(BRAZIL_TZ))
        logger.info(
            f'[{agora.strftime("%d/%m/%Y %H:%M:%S")}] '
            'Executando lembrete SRS diário'
        )

        whatsapp_service = AppServices.get_whatsapp_service()
        if not whatsapp_service:
            logger.warning(
                'WhatsApp service não disponível — lembrete cancelado'
            )
            return

        now = datetime.now(timezone.utc)
        reviews_col = get_reviews_collection()
        users_col = get_users_collection()

        # Agregar usuários com cards vencidos
        pipeline = [
            {'$match': {'next_review_date': {'$lte': now}}},
            {'$group': {'_id': '$user_id', 'due_count': {'$sum': 1}}},
        ]
        cursor = await reviews_col.aggregate(pipeline)
        due_by_user = []
        async for doc in cursor:
            due_by_user.append(doc)

        for entry in due_by_user:
            user_id = entry['_id']
            due_count = entry['due_count']

            user = await users_col.find_one({'_id': user_id})
            if not user:
                continue

            phone = user.get('phone_number')
            if not phone:
                continue

            message = (
                f'*OmniFlash — Oráculo de Bolso*\n\n'
                f'Tens *{due_count} cenário{"s" if due_count > 1 else ""}* '
                f'para treinar hoje.\n\n'
                f'Cada revisão afina os teus reflexos preditivos. '
                f'Acede ao app e treina agora.'
            )
            await whatsapp_service.send_message(phone, message)

        logger.success('Lembretes SRS enviados com sucesso')

    except Exception as e:
        logger.error(f'Erro na tarefa de lembrete SRS: {e}')
        logger.exception('Detalhes do erro:')


async def start_scheduler() -> None:
    """Inicia o scheduler de tarefas agendadas."""
    try:
        if not scheduler.running:
            scheduler.start()
            logger.info('Scheduler de tarefas iniciado')
        else:
            logger.warning('Scheduler já está em execução')
    except Exception as e:
        logger.error(f'Erro ao iniciar scheduler: {e}')
        raise


async def stop_scheduler() -> None:
    """Para o scheduler de tarefas agendadas."""
    try:
        if scheduler.running:
            scheduler.shutdown(wait=True)
            logger.info('Scheduler de tarefas parado')
        else:
            logger.info('Scheduler não estava em execução')
    except Exception as e:
        logger.error(f'Erro ao parar scheduler: {e}')
        raise


def get_scheduler_status() -> dict:
    """Retorna o status atual do scheduler."""

    agora = datetime.now(ZoneInfo(BRAZIL_TZ))
    jobs_info = []

    for job in scheduler.get_jobs():
        job_data = {
            'id': job.id,
            'nome': job.name,
            'proxima_execucao': None,
            'trigger': str(job.trigger),
            'pendente': job.pending,
        }

        if job.next_run_time:
            proxima = job.next_run_time.astimezone(ZoneInfo(BRAZIL_TZ))
            job_data['proxima_execucao'] = proxima.strftime(
                '%d/%m/%Y %H:%M:%S'
            )

        jobs_info.append(job_data)

    return {
        'running': scheduler.running,
        'jobs_count': len(scheduler.get_jobs()),
        'timezone': str(scheduler.timezone),
        'horario_atual': agora.strftime('%d/%m/%Y %H:%M:%S'),
        'jobs': jobs_info,
    }
