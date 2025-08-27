import json
from ast import literal_eval

from fastapi import APIRouter, Query
from starlette import status
from starlette.responses import JSONResponse

from app.entities.sorted import SortedType
from app.init_logic import api_service
from app.api.v1.serializers import DoctorCreateBody, DoctorUpdateBody, DoctorsFilterBody

router = APIRouter()


@router.get('/subscribers/count/')
async def doctor_subscribers():
    """Возвращает общее количество подписичок"""
    total_subscribers, count_text, last_updated_timestamp = api_service.get_all_subscribers_count()

    formatted_date = None
    if last_updated_timestamp:
        formatted_date = last_updated_timestamp.strftime("%d.%m.%Y")

    return {
        "subscribers_count": total_subscribers,
        "subscribers_count_text": count_text,
        "last_updated": formatted_date,
    }


@router.get('/filter/info/')
async def filter_info():
    """
    Информация для отображения фильтров. Возвращает список доступных соцсетей для фильтрации по подписчикам
    """
    messengers = api_service.get_filter_info()
    data = list()
    for messenger in messengers:
        data.append({
            "name": messenger.name,
            "slug": str(messenger.slug.value),
        })
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "messengers": data
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


# Используем post чтобы не превысить лимит по get параметрам
@router.post('/doctors/filter/')
async def doctors_filter_with_ids(request: DoctorsFilterBody):
    """
    Фильтрация по фильтрам и id докторов, чтобы не урезать выдачу
    """
    # todo проверить работу request.social_media
    limit = 30 or request.limit
    try:
        sort_enum = SortedType(request.sort.lower())
    except ValueError:
        sort_enum = SortedType.DESC

    try:
        min_subscribers = int(request.min_subscribers)
        max_subscribers = int(request.max_subscribers)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))

    doctors, filtered_doctors_count, subscribers_count = api_service.doctors_filter_with_doctors_ids(
        request.social_media,
        sort_enum,
        min_subscribers,
        max_subscribers,
        limit,
        request.current_page,
        request.doctor_ids,
    )

    doctors_list = []
    for doctor in doctors:
        doctors_list.append({
            "doctor": {
                "doctor_id": doctor.doctor_id,
                "inst_short": doctor.inst_short,
                "inst_text": doctor.inst_text,
                "telegram_short": doctor.telegram_short,
                "telegram_text": doctor.telegram_text,
            }
        })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "filtered_doctors_count": filtered_doctors_count,
            "filtered_doctors_subscribers_count": subscribers_count,
            "doctors": doctors_list,
        }
    )


@router.get('/doctors/filter/')
async def doctors_filter(
        social_media: str = Query(None, description='Соцсети в формате JSON массива, например: "["tg", "inst"]"'),
        min_subscribers: str = Query(None, description="Минимальное количество подписчиков - default 0"),
        max_subscribers: str = Query(None, description="Максимальное количество подписчиков - default 100"),
        offset: str = Query(None, description="current_page поиска - default 0"),
        limit: str = Query(None, description="Лимит поиска для страницы - default 30"),
        sort: str = Query("desc", description="Сортировка по количеству подписчиков default desc"),
):
    """
    Возвращает докторов отфильтрованных по переданному значению количества подписчиков

    :param:
    - social_media: социальная сеть по которой необходимо фильтровать
    - min_subscribers: минимальное число подписчиков (включительно)
    - max_subscribers: максимальное число подписчиков (включительно)
    - offset: current_page - текущая страница поиска
    - limit: лимит поиска

    :return
    - doctors_ids: айдишники докторов, которые подходят под условия фильтрации
    """
    current_page = offset

    social_medias = []
    # todo выпилить костыль
    if social_media is not None and len(social_media) != 0:
        try:
            social_medias = json.loads(social_media)
        except json.JSONDecodeError:
            try:
                result = literal_eval(social_media)
                social_medias = result if isinstance(result, list) else [result]
            except (ValueError, SyntaxError):
                social_medias = [
                    s.strip()
                    for s in social_media.strip('[]').split(',')
                    if s.strip()
                ]

    # Дефолтные значения
    if not current_page:
        current_page = 0

    try:
        sort_enum = SortedType(sort.lower())
    except ValueError:
        sort_enum = SortedType.DESC

    if not limit or int(min_subscribers) <= 0:
        limit = 30

    if not min_subscribers or int(min_subscribers) < 0:
        min_subscribers = 0

    if not max_subscribers or int(max_subscribers) < 100:
        max_subscribers = 100

    try:
        min_subscribers = int(min_subscribers)
        max_subscribers = int(max_subscribers)
        current_page = int(current_page)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))

    doctors, filtered_doctors_count, subscribers_count = api_service.doctors_filter(
        social_medias,
        sort_enum,
        min_subscribers,
        max_subscribers,
        current_page,
        limit,
    )

    doctors_list = []
    for doctor in doctors:
        doctors_list.append({
            "doctor": {
                "doctor_id": doctor.doctor_id,
                "inst_short": doctor.inst_short,
                "inst_text": doctor.inst_text,
                "telegram_short": doctor.telegram_short,
                "telegram_text": doctor.telegram_text,
            }
        })

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "filtered_doctors_count": filtered_doctors_count,
            "filtered_doctors_subscribers_count": subscribers_count,
            "doctors": doctors_list,
        }
    )


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


@router.post('/doctors/create/')
async def create_doctor(request: DoctorCreateBody):
    """Создает нового доктора в базе"""
    try:
        await api_service.create_doctor(request.doctor_id, request.instagram, request.telegram)
    except Exception as e:
        print('Ошибка при создании доктора create_doctor', e)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=str(e))
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": f"Успешно создал запись DOC: {request.doctor_id}, канал:{request.telegram}"}
    )


@router.patch('/doctors/{doctor_id}/')
async def update_doctor(doctor_id: int, request: DoctorUpdateBody):
    """Обновляет информацию у доктора"""
    try:
        updated = await api_service.update_doctor(doctor_id, request.instagram, request.telegram, request.is_active)
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


# @router.post('/migrate_instagram/')
# async def migrate_instagram(request: DoctorCreateBody):
#     """Миграция инсты"""
#     try:
#         updated = api_service.migrate_instagram(request.doctor_id, request.instagram, )
#         if updated:
#             return JSONResponse(
#                 status_code=status.HTTP_200_OK,
#                 content={
#                     "message": f"Успешно обновил запись доктора ID: {request.doctor_id}, ИНСТ: {request.instagram}"}
#             )
#         return JSONResponse(
#             status_code=status.HTTP_201_CREATED,
#             content={
#                 "message": f"Создал нового доктора ID: {request.doctor_id}, ИНСТ: {request.instagram}"}
#         )
#     except Exception as e:
#         print(f"Ошибка при обновлении доктора {request.doctor_id}: {e}")
#         return JSONResponse(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             content={"message": f"Ошибка при обновлении доктора {request.doctor_id}"}
#         )
