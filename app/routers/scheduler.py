from fastapi import APIRouter

from ..scheduler import (
    _send_daily_sigaa_summary,
    get_current_time,
    get_scheduler_status,
)

router = APIRouter(prefix='/scheduler', tags=['scheduler'])


@router.get('/status')
def get_status():
    """Retorna o status do scheduler e jobs agendados"""
    return get_scheduler_status()


@router.get('/time')
def get_time():
    """Retorna o horário atual no timezone do Brasil"""
    return get_current_time()


@router.post('/trigger-daily-summary')
async def trigger_daily_summary():
    """Dispara manualmente a tarefa de resumo diário do SIGAA"""
    try:
        await _send_daily_sigaa_summary()
        return {
            'status': 'success',
            'message': 'Tarefa de resumo diário executada',
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
