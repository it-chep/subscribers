from fastapi import APIRouter, Query
from starlette import status
from starlette.responses import JSONResponse

from app.init_logic import api_service
from app.api.v1.serializers import DoctorCreateBody, DoctorUpdateBody

router = APIRouter()


@router.get('/subscribers/{doctor_id}/')
async def doctor_subscribers(doctor_id: int):
    """Возвращает количество подписчиков у доктора"""
    doctor = api_service.get_doctor_subscribers(doctor_id)

    if not doctor:
        return JSONResponse(
            status_code=404,
            content={"message": "Doctor not found"}
        )

    return {
        "doctor_id": doctor.doctor_id,
        "instagram": doctor.inst_subs_count,
        "telegram": doctor.tg_subs_count,
    }


@router.get('/filter/info')
async def filter_info():
    """
    Информация для отображения фильтров. Возвращает список доступных соцсетей для фильтрации по подписчикам
    """
    messangers = api_service.get_filter_info()
    return JSONResponse(
        status_code=200,
        content={
            "messangers": messangers
        }
    )


@router.get('/doctors/filter/')
async def doctors_filter(
        social_media: str = Query(None, description="Соцсеть, по которой фильтруем подписчиков"),
        min_subscribers: str = Query(None, description="Минимальное количество подписчиков"),
        max_subscribers: str = Query(None, description="Максимальное количество подписчиков"),
        offset: str = Query(None, description="Офсет поиска"),
        limit: str = Query(None, description="Лимит поиска для страницы"),
):
    """
    Возвращает докторов отфильтрованных по переданному значению количества подписчиков

    :param:
    - social_media: социальная сеть по которой необходимо фильтровать
    - min_subscribers: минимальное число подписчиков (включительно)
    - max_subscribers: максимальное число подписчиков (включительно)
    - offset: офсет поиска
    - limit: лимит поиска

    :return
    - doctors_ids: айдишники докторов, которые подходят под условия фильтрации
    """

    if not limit or int(limit) == 0:
        limit = 30

    if not offset:
        offset = 0

    if not min_subscribers or int(min_subscribers) < 0:
        min_subscribers = 0

    if not max_subscribers or int(max_subscribers) < 100:
        max_subscribers = 100

    try:
        min_subscribers = int(min_subscribers)
        max_subscribers = int(max_subscribers)
        offset = int(offset)
        limit = int(limit)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))

    doctors_ids = api_service.doctors_filter(
        social_media,
        min_subscribers,
        max_subscribers,
        offset,
        limit,
    )

    return JSONResponse(
        status_code=200,
        content={
            "min_followers": min_subscribers,
            "max_followers": max_subscribers,
            "offset": offset,
            "limit": limit,
            "doctors_ids": doctors_ids,
        }
    )


@router.post('/doctors/create/')
async def create_doctor(request: DoctorCreateBody):
    """Создает нового доктора в базе"""
    api_service.create_doctor(request.doctor_id, request.instagram, request.telegram)

    return JSONResponse(
        status_code=200,
        content={"message": "success"}
    )


@router.patch('/doctors/{doctor_id}/')
async def update_doctor(request: DoctorUpdateBody):
    """Обновляет информацию у доктора"""
    api_service.update_doctor(request.doctor_id, request)
    return
