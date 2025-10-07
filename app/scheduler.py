"""
Módulo de agendamento de tarefas usando APScheduler.

Este módulo configura e gerencia tarefas agendadas para a aplicação,
incluindo o envio diário de resumos do SIGAA via WhatsApp.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

from .agents.tasks import trigger_sigaa_summary_agent
from .config import SCHEDULED_TASKS_USER_NUMBER
from .services.shared import AppServices

# Timezone do Brasil
BRAZIL_TZ = 'America/Sao_Paulo'

# Instância global do scheduler
scheduler = AsyncIOScheduler(timezone=BRAZIL_TZ)


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
            trigger=CronTrigger(hour=11, minute=0),  # Todos os dias às 11:00
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
        agora = datetime.now(ZoneInfo(BRAZIL_TZ))
        logger.info(
            f'📅 [{agora.strftime("%d/%m/%Y %H:%M:%S")}]'
            ' Executando tarefa agendada: resumo diário do SIGAA'
        )

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


def get_current_time() -> dict:
    """
    Retorna o horário atual no timezone do Brasil.
    """
    agora = datetime.now(ZoneInfo(BRAZIL_TZ))
    return {
        'horario_atual': agora.isoformat(),
        'horario_formatado': agora.strftime('%d/%m/%Y %H:%M:%S'),
        'timezone': BRAZIL_TZ,
        'utc_offset': agora.strftime('%z'),
    }


def formatar_tempo_restante(segundos: int) -> str:
    """Formata segundos em formato legível"""
    if segundos < 0:
        return 'Job atrasado'

    dias, resto = divmod(segundos, 86400)
    horas, resto = divmod(resto, 3600)
    minutos, segs = divmod(resto, 60)

    partes = []
    if dias > 0:
        partes.append(f'{dias} dia{"s" if dias > 1 else ""}')
    if horas > 0:
        partes.append(f'{horas} hora{"s" if horas > 1 else ""}')
    if minutos > 0:
        partes.append(f'{minutos} minuto{"s" if minutos > 1 else ""}')
    if segs > 0 or not partes:
        partes.append(f'{segs} segundo{"s" if segs != 1 else ""}')

    return ', '.join(partes)


def get_scheduler_status() -> dict:
    """
    Retorna o status atual do scheduler.

    :return: Dicionário com informações sobre o estado do scheduler
    """
    agora = datetime.now(ZoneInfo(BRAZIL_TZ))
    jobs_info = []

    for job in scheduler.get_jobs():
        job_data = {
            'id': job.id,
            'nome': job.name,
            'proxima_execucao': None,
            'proxima_execucao_formatada': None,
            'tempo_restante': None,
            'tempo_restante_formatado': None,
            'trigger': str(job.trigger),
            'pendente': job.pending,
        }

        if job.next_run_time:
            proxima = job.next_run_time
            if proxima.tzinfo is None:
                proxima = proxima.replace(tzinfo=ZoneInfo(BRAZIL_TZ))
            else:
                proxima = proxima.astimezone(ZoneInfo(BRAZIL_TZ))

            tempo_restante = proxima - agora
            segundos_restantes = int(tempo_restante.total_seconds())

            if segundos_restantes < 0:
                tempo_formatado = 'Atrasado'
            else:
                horas, resto = divmod(segundos_restantes, 3600)
                minutos, segundos = divmod(resto, 60)
                horas_24 = 24
                if horas > horas_24:
                    dias = horas // horas_24
                    horas %= horas_24
                    tempo_formatado = (
                        f'{dias}d {horas}h {minutos}m {segundos}s'
                    )
                else:
                    tempo_formatado = f'{horas}h {minutos}m {segundos}s'

            job_data.update({
                'proxima_execucao': proxima.isoformat(),
                'proxima_execucao_formatada': proxima.strftime(
                    '%d/%m/%Y %H:%M:%S'
                ),
                'tempo_restante': segundos_restantes,
                'tempo_restante_formatado': tempo_formatado,
            })

        jobs_info.append(job_data)

    return {
        'running': scheduler.running,
        'jobs_count': len(scheduler.get_jobs()),
        'timezone': str(scheduler.timezone),
        'horario_atual': agora.strftime('%d/%m/%Y %H:%M:%S'),
        'jobs': jobs_info,
    }
