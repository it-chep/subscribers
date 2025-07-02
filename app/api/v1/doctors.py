from fastapi import APIRouter, Query
from starlette import status
from starlette.responses import JSONResponse

from app.init_logic import api_service
from app.api.v1.serializers import DoctorCreateBody, DoctorUpdateBody
from app.exception.domain_error import RequiredFieldError, UnavailableTelegramChannel, DoctorNotFound

router = APIRouter()


@router.get('/subscribers/count')
async def doctor_subscribers():
    """Возвращает общее количество подписичок"""
    total_telegram_subscribers, count_text, tg_last_updated_timestamp = api_service.get_all_subscribers_count()

    formatted_date = None
    if tg_last_updated_timestamp:
        formatted_date = tg_last_updated_timestamp.strftime("%d.%m.%Y")

    return {
        "subscribers_count": total_telegram_subscribers,
        "subscribers_count_text": count_text,
        "last_updated": formatted_date,
    }


@router.get('/subscribers/{doctor_id}/')
async def doctor_subscribers(doctor_id: int):
    """Возвращает количество подписчиков у доктора"""
    doctor = api_service.get_doctor_subscribers(doctor_id)

    if not doctor:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Доктор не найден"}
        )

    tg_formatted_date = None
    if doctor.tg_last_updated_timestamp:
        tg_formatted_date = doctor.tg_last_updated_timestamp.strftime("%d.%m.%Y")

    inst_formatted_date = None
    if doctor.inst_last_updated_timestamp:
        inst_formatted_date = doctor.inst_last_updated_timestamp.strftime("%d.%m.%Y")

    return {
        "doctor_id": doctor.doctor_id,

        "instagram": doctor.inst_subs_count,
        "instagram_short": doctor.instagram_short,
        "instagram_text": doctor.instagram_text,
        "instagram_last_updated_date": inst_formatted_date,

        "telegram": doctor.tg_subs_count,
        "telegram_short": doctor.telegram_short,
        "telegram_text": doctor.telegram_text,
        "tg_last_updated_date": tg_formatted_date
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


@router.get('/doctors/by_ids/')
async def info_by_ids(doctor_ids: str):
    """
    Получение информации о докторах по списку ID.
    Формат запроса: /doctors/by_ids/?doctor_ids=1,2,3,4
    """
    # Преобразуем строку с ID в список чисел
    ids_list = [int(id_str) for id_str in doctor_ids.split(',') if id_str.strip().isdigit()]

    if not ids_list:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Не указаны ID пользователей"}
        )

    res_map = dict()
    dtos = api_service.get_subscribers_by_doctor_ids(ids_list)
    for dto in dtos:
        res_map[dto.doctor_id] = {
            "doctor_id": dto.doctor_id,
            "instagram_subs_count": dto.inst_subs_count,
            "instagram_subs_text": dto.instagram_text,
            "telegram_subs_count": dto.tg_subs_count,
            "telegram_subs_text": dto.telegram_text,
        }

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "data": res_map
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
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))

    doctors = api_service.doctors_filter(
        social_media,
        min_subscribers,
        max_subscribers,
        offset,
    )

    doctors_list = []
    for doctor in doctors:
        doctors_list.append({
            "doctor": {
                "doctor_id": doctor.doctor_id,
                "telegram_short": doctor.telegram_short,
                "telegram_text": doctor.telegram_text,
            }
        })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "min_subscribers": min_subscribers,
            "max_subscribers": max_subscribers,
            "offset": offset,
            "doctors": doctors_list,
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
async def update_doctor(doctor_id: int, request: DoctorUpdateBody):
    """Обновляет информацию у доктора"""
    try:
        updated = await api_service.update_doctor(doctor_id, request.instagram, request.telegram)
        if updated:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": f"Успешно обновил запись доктора ID: {doctor_id}, ТГ канал: {request.telegram}, ИНСТ: {request.instagram}"}
            )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": f"Создал нового доктора ID: {doctor_id}, ТГ канал: {request.telegram}, ИНСТ: {request.instagram}"}
        )
    except Exception as e:
        print(f"Ошибка при обновлении доктора {doctor_id}: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка при обновлении доктора {doctor_id}"}
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
