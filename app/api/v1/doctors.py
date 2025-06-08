from fastapi import APIRouter, Query
from starlette import status
from starlette.responses import JSONResponse

from app.init_logic import api_service
from app.api.v1.serializers import DoctorCreateBody, DoctorUpdateBody
from app.exception.domain_error import RequiredFieldError, UnavailableTelegramChannel, DoctorNotFound

router = APIRouter()


@router.get('/subscribers/{doctor_id}/')
async def doctor_subscribers(doctor_id: int):
    """Возвращает количество подписчиков у доктора"""
    doctor = api_service.get_doctor_subscribers(doctor_id)

    if not doctor:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Доктор не найден"}
        )

    return {
        "doctor_id": doctor.doctor_id,
        "instagram": doctor.inst_subs_count,
        "telegram": doctor.tg_subs_count,
        "telegram_short": doctor.telegram_short,
        "telegram_text": doctor.telegram_text,
    }


@router.get('/filter/info')
async def filter_info():
    """
    Информация для отображения фильтров. Возвращает список доступных соцсетей для фильтрации по подписчикам
    """
    messengers = api_service.get_filter_info()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "messengers": messengers
        }
    )


@router.get('/doctors/filter/')
async def doctors_filter(
        social_media: str = Query(None, description="Соцсеть, по которой фильтруем подписчиков - tg"),
        min_subscribers: str = Query(None, description="Минимальное количество подписчиков - default 0"),
        max_subscribers: str = Query(None, description="Максимальное количество подписчиков - default 100"),
        offset: str = Query(None, description="Офсет поиска - default 0"),
        limit: str = Query(None, description="Лимит поиска для страницы - default 30"),
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
        status_code=status.HTTP_200_OK,
        content={
            "min_subscribers": min_subscribers,
            "max_subscribers": max_subscribers,
            "offset": offset,
            "limit": limit,
            "doctors_ids": doctors_ids,
        }
    )


@router.post('/doctors/create/')
async def create_doctor(request: DoctorCreateBody):
    """Создает нового доктора в базе"""
    try:
        await api_service.create_doctor(request.doctor_id, request.instagram, request.telegram)
    except RequiredFieldError as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)})
    except UnavailableTelegramChannel as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(e)})

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Успешно создал запись DOC: {request.doctor_id}, канал:{request.telegram}"}
    )


@router.patch('/doctors/{doctor_id}/')
async def update_doctor(request: DoctorUpdateBody):
    """Обновляет информацию у доктора"""
    # api_service.update_doctor(request.doctor_id, request)
    # return JSONResponse(
    #     status_code=status.HTTP_200_OK,
    #     content={"message": f"Успешно обновил запись DOC: {request.doctor_id}, канал:{request.telegram}"}
    # )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Фича в разработке"}
    )

# todo
# @router.post('/doctors/migrate')
# async def migrate_doctors(request: DoctorCreateBody):
#     """Мигрирует докторов в базу"""
#     api_service.create_doctor(request.doctor_id, request.instagram, request.telegram)
#
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,,
#         content={"message": "success"}
#     )
