import datetime
from typing import List, Optional

from app.entities.sorted import SortedType
from clients.postgres import Database
from app.entities.doctor_subs import DoctorSubs, DoctorSubsByIDs
from app.entities.messengers import Messenger, SocialNetworkType
from app.exception.domain_error import DoctorNotFound

SOCIAL_NETWORK_FIELDS = {
    SocialNetworkType.INSTAGRAM: "inst_subs_count",
    SocialNetworkType.TELEGRAM: "tg_subs_count",
    SocialNetworkType.YOUTUBE: "youtube_subs_count",
}


class ApiRepository:

    def __init__(self):
        self.db = Database()

    def get_doctor_subscribers(self, doctor_id: int) -> DoctorSubs:
        query = f"""
            select id, 
                doctor_id, 
                instagram_channel_name,
                inst_subs_count,
                inst_last_updated,
                telegram_channel_name,
                tg_subs_count,
                tg_last_updated,
                youtube_channel_name,
                youtube_last_updated,
                youtube_subs_count
            from doctors 
            where doctor_id = %s;
        """
        result = self.db.select(query, (doctor_id,), True)

        try:
            doctor = DoctorSubs(
                internal_id=result[0],
                doctor_id=result[1],
                instagram_channel_name=result[2] or "",
                inst_subs_count=result[3] or 0,
                inst_last_updated_timestamp=result[4],
                telegram_channel_name=result[5] or "",
                tg_subs_count=result[6] or 0,
                tg_last_updated_timestamp=result[7],

                youtube_channel_name=result[8] or "",
                youtube_last_updated_timestamp=result[9],
                youtube_subs_count=result[10] or 0,
            )
        except Exception as e:
            raise DoctorNotFound(doctor_id=doctor_id)

        return doctor

    def get_subscribers_by_doctor_ids(self, doctor_ids: list[int]) -> list[DoctorSubsByIDs]:
        query = f"""
            select
                doctor_id, 
                inst_subs_count,
                tg_subs_count,
                youtube_subs_count
            from doctors 
            where doctor_id = ANY(%s);
        """
        doctors = list()

        try:
            result = self.db.select(query, (doctor_ids,))

            for r in result:
                doctors.append(DoctorSubsByIDs(
                    doctor_id=r[0],
                    inst_subs_count=r[1] or 0,
                    tg_subs_count=r[2] or 0,
                    youtube_subs_count=r[3] or 0,
                ))

        except Exception as e:
            print("Ошибка при получении врачей по ids", e)

        return doctors

    def get_all_subscribers_count(self) -> (int, Optional[datetime.datetime]):
        query = f""" 
            select 
                sum(tg_subs_count) + sum(inst_subs_count) + sum(youtube_subs_count) AS total_subscribers,
                least(min(tg_last_updated), min(inst_last_updated)) AS last_updated_timestamp
            from doctors 
            where is_active is true;
        """

        try:
            result = self.db.select(query)[0]
            total_subscribers = result[0]
            last_updated_timestamp = result[1]

            return total_subscribers, last_updated_timestamp
        except Exception as e:
            print("Ошибка получения количества подписчиков", e)
            return 0, None

    def create_doctor_subscriber(
            self, doctor_id: int,
            instagram_channel_name: str,
            telegram_channel_name: str,
            youtube_channel_name: str
    ) -> None:
        query = f"""insert into doctors (
                doctor_id, 
                instagram_channel_name,
                telegram_channel_name,
                youtube_channel_name,
                tg_has_subscribed
        ) 
        values (%s, %s, %s, %s, false)
        on conflict (doctor_id) do nothing
        returning id;
        """

        try:
            self.db.execute(
                query,
                (doctor_id, instagram_channel_name, telegram_channel_name, youtube_channel_name)
            )
        except Exception as e:
            print("Ошибка при создании доктора в таблице", e)

    def get_filter_info(self) -> List[Messenger]:
        query = f"""
            select name, slug from social_media where enabled is true;
        """

        medias = list()
        try:
            results = self.db.select(query)
            for result in results:
                medias.append(
                    Messenger(
                        name=result[0],
                        slug=SocialNetworkType(result[1]),
                    )
                )
        except Exception as e:
            print("Ошибка при получении информации о фильтрах для соц.cетей", e)

        return medias

    def filtered_doctors_count_with_doctors_ids(
            self,
            social_networks: list[SocialNetworkType],
            min_subscribers: int,
            max_subscribers: int,
            doctors_ids: list[int],
    ):
        """
        Функция считает сколько врачей попадает под выборку для подсчета страниц,
        какой охват имеют отфильтрованные врачи
        """
        base_query = f""" 
        select 
            count(*) as doctors_count, 
            coalesce(sum(tg_subs_count), 0) + coalesce(sum(inst_subs_count), 0) + coalesce(sum(youtube_subs_count), 0) AS total_subscribers
        from doctors
        where doctor_id = any(%s::bigint[])
        """

        params = ()
        query = ""

        # Все либо никаких специальностей
        if not social_networks or len(social_networks) or len(social_networks) == len(SOCIAL_NETWORK_FIELDS.keys()):
            coalesce_query = ""
            counter = 0
            for social_network in SOCIAL_NETWORK_FIELDS.values():
                counter += 1
                if counter == len(SOCIAL_NETWORK_FIELDS.keys()):
                    coalesce_query += f"coalesce({social_network}, 0) "
                    continue
                coalesce_query += f"coalesce({social_network}, 0) + "

            query = base_query + f"and {coalesce_query} between %s and %s"

        if social_networks and len(social_networks) != len(SOCIAL_NETWORK_FIELDS.keys()):
            coalesce_query = ""
            counter = 0
            for social_network in social_networks:
                counter += 1
                if counter == len(social_networks):
                    coalesce_query += f"coalesce({SOCIAL_NETWORK_FIELDS[social_network]}, 0)"
                    continue
                coalesce_query += f"coalesce({SOCIAL_NETWORK_FIELDS[social_network]}, 0) + "

            query = base_query + f"and {coalesce_query} between %s and %s "

        if len(query) != 0:
            params = (doctors_ids, min_subscribers, max_subscribers)

        try:
            result = self.db.select(query, params)[0]
        except Exception as e:
            print("Ошибка при подсчете докторов для фильтрации", e)
            return 0, 0
        try:
            doctors_count = int(result[0])
        except Exception as e:
            doctors_count = 0

        try:
            subscribers_count = int(result[1])
        except Exception as e:
            subscribers_count = 0

        return doctors_count, subscribers_count

    def filtered_doctors_count(
            self,
            social_networks: list[SocialNetworkType],
            min_subscribers: int,
            max_subscribers: int,
    ):
        """
        Функция считает сколько врачей попадает под выборку для подсчета страниц,
        какой охват имеют отфильтрованные врачи
        """
        base_query = f""" 
        select 
            count(*) as doctors_count, 
            coalesce(sum(tg_subs_count), 0) + coalesce(sum(inst_subs_count), 0) + coalesce(sum(youtube_subs_count), 0) AS total_subscribers
        from doctors
        where is_active is true
        """

        params = ()
        query = ""

        # Все либо никаких специальностей
        if not social_networks or len(social_networks) or len(social_networks) == len(SOCIAL_NETWORK_FIELDS.keys()):
            coalesce_query = ""
            counter = 0
            for social_network in SOCIAL_NETWORK_FIELDS.values():
                counter += 1
                if counter == len(SOCIAL_NETWORK_FIELDS.keys()):
                    coalesce_query += f"coalesce({social_network}, 0) "
                    continue
                coalesce_query += f"coalesce({social_network}, 0) + "

            query = base_query + f"and {coalesce_query} between %s and %s"

        if social_networks and len(social_networks) != len(SOCIAL_NETWORK_FIELDS.keys()):
            coalesce_query = ""
            counter = 0
            for social_network in social_networks:
                counter += 1
                if counter == len(social_networks):
                    coalesce_query += f"coalesce({SOCIAL_NETWORK_FIELDS[social_network]}, 0)"
                    continue
                coalesce_query += f"coalesce({SOCIAL_NETWORK_FIELDS[social_network]}, 0) + "

            query = base_query + f"and {coalesce_query} between %s and %s "

        if len(query) != 0:
            params = (min_subscribers, max_subscribers)

        try:
            result = self.db.select(query, params)[0]
        except Exception as e:
            print("Ошибка при подсчете докторов для фильтрации", e)
            return 0, 0

        try:
            doctors_count = int(result[0])
        except Exception as e:
            doctors_count = 0

        try:
            subscribers_count = int(result[1])
        except Exception as e:
            subscribers_count = 0

        return doctors_count, subscribers_count

    def doctors_filter_with_doctors_ids(
            self,
            social_networks: list[SocialNetworkType],
            sort_enum: SortedType,
            min_subscribers: int,
            max_subscribers: int,
            limit: int,
            current_page: int,
            doctors_ids: list[int],
    ):
        if len(doctors_ids) == 0:
            return 0, 0

        if current_page <= 0:
            current_page = 1

        offset = (current_page - 1) * limit

        doctors = []
        params = doctors_ids
        query = ""

        base_query = f"""
                   select 
                       doctor_id,
                       coalesce(tg_subs_count, 0),
                       coalesce(inst_subs_count, 0),
                       coalesce(youtube_subs_count, 0),
                       coalesce(inst_subs_count, 0) + coalesce(tg_subs_count, 0) + coalesce(youtube_subs_count, 0) AS total_subscribers
                   from doctors
                   where doctor_id = any(%s::bigint[]) and is_active is true
               """

        # Все либо никаких специальностей
        if not social_networks or len(social_networks) or len(social_networks) == len(SOCIAL_NETWORK_FIELDS.keys()):
            coalesce_query = ""
            counter = 0
            for social_network in SOCIAL_NETWORK_FIELDS.values():
                counter += 1
                if counter == len(SOCIAL_NETWORK_FIELDS.keys()):
                    coalesce_query += f"coalesce({social_network}, 0) "
                    continue
                coalesce_query += f"coalesce({social_network}, 0) + "

            query = base_query + f"""
                and {coalesce_query} between %s and %s 
                order by total_subscribers {sort_enum} 
            """

        if social_networks and len(social_networks) == 1:
            query = base_query + f"""
                and {SOCIAL_NETWORK_FIELDS[social_networks[0]]} between %s and %s
                order by {SOCIAL_NETWORK_FIELDS[social_networks[0]]} {sort_enum}
            """

        if social_networks and len(social_networks) != len(SOCIAL_NETWORK_FIELDS.keys()) and len(social_networks) != 1:
            coalesce_query = ""
            counter = 0
            for social_network in social_networks:
                counter += 1
                if counter == len(social_networks):
                    coalesce_query += f"coalesce({SOCIAL_NETWORK_FIELDS[social_network]}, 0)"
                    continue
                coalesce_query += f"coalesce({SOCIAL_NETWORK_FIELDS[social_network]}, 0) + "

            query = base_query + f"""
                and {coalesce_query} between %s and %s 
                order by total_subscribers {sort_enum} 
            """

        if len(query) != 0:
            query += """
                offset %s 
                limit %s
            """
            params = (doctors_ids, min_subscribers, max_subscribers, offset, limit)

        try:
            results = self.db.select(
                query, params
            )
            for result in results:
                doctors.append(
                    DoctorSubs(
                        internal_id=0,
                        doctor_id=result[0],
                        tg_subs_count=int(result[1]),
                        inst_subs_count=int(result[2]),
                        youtube_subs_count=int(result[3]),
                    )
                )

        except Exception as e:
            print("Ошибка при фильтрации каналов докторов", e)

        return doctors

    def doctors_filter(
            self,
            social_networks: list[SocialNetworkType],
            sort_enum: SortedType,
            min_subscribers: int,
            max_subscribers: int,
            current_page: int,
            limit: int,
    ):
        if current_page <= 0:
            current_page = 1

        offset = (current_page - 1) * limit
        doctors = []
        params = ()
        query = ""

        base_query = f"""
            select 
                doctor_id,
                tg_subs_count,
                inst_subs_count,
                youtube_subs_count,
                coalesce(inst_subs_count, 0) + coalesce(tg_subs_count, 0) + coalesce(youtube_subs_count, 0) AS total_subscribers
            from doctors
        """

        # Все либо никаких специальностей
        if not social_networks or len(social_networks) or len(social_networks) == len(SOCIAL_NETWORK_FIELDS.keys()):
            coalesce_query = ""
            counter = 0
            for social_network in SOCIAL_NETWORK_FIELDS.values():
                counter += 1
                if counter == len(SOCIAL_NETWORK_FIELDS.keys()):
                    coalesce_query += f"coalesce({social_network}, 0) "
                    continue
                coalesce_query += f"coalesce({social_network}, 0) + "

            query = base_query + f"""
                and {coalesce_query} between %s and %s and is_active is true
                order by total_subscribers {sort_enum} 
            """

        if social_networks and len(social_networks) == 1:
            query = base_query + f"""
                and {SOCIAL_NETWORK_FIELDS[social_networks[0]]} between %s and %s and is_active is true
                order by {SOCIAL_NETWORK_FIELDS[social_networks[0]]} {sort_enum}
            """

        if social_networks and len(social_networks) != len(SOCIAL_NETWORK_FIELDS.keys()) and len(social_networks) != 1:
            coalesce_query = ""
            counter = 0
            for social_network in social_networks:
                counter += 1
                if counter == len(social_networks):
                    coalesce_query += f"coalesce({SOCIAL_NETWORK_FIELDS[social_network]}, 0)"
                    continue
                coalesce_query += f"coalesce({SOCIAL_NETWORK_FIELDS[social_network]}, 0) + "

            query = base_query + f"""
                and {coalesce_query} between %s and %s and is_active is true
                order by total_subscribers {sort_enum} 
            """

        if len(query) != 0:
            query += """
                offset %s 
            """
            params = (min_subscribers, max_subscribers, offset)

        try:
            results = self.db.select(
                query, params
            )
            for result in results:
                doctors.append(
                    DoctorSubs(
                        internal_id=0,
                        doctor_id=result[0],
                        tg_subs_count=result[1] or 0,
                        inst_subs_count=result[2] or 0,
                        youtube_subs_count=result[3] or 0,
                    )
                )

        except Exception as e:
            print("Ошибка при фильтрации каналов докторов", e)

        return doctors

    def update_doctor(
            self,
            doctor_id: int,
            instagram_channel_name: str, telegram_channel_name: str, youtube_channel_name: str
    ):
        query = f"""
        update doctors
        set 
            instagram_channel_name = %s,
            telegram_channel_name = %s,
            youtube_channel_name = %s
        where doctor_id = %s;
        """

        try:
            rows_count = self.db.execute_with_result(
                query, (instagram_channel_name, telegram_channel_name, youtube_channel_name, doctor_id))
            if rows_count == 0:
                raise DoctorNotFound(doctor_id=doctor_id)
        except DoctorNotFound as e:
            raise e
        except Exception as e:
            print("Ошибка при создании доктора в таблице", e)

    def update_doctor_is_active(self, doctor_id: int, is_active: bool):
        query = f"""
        update doctors
        set 
            is_active = %s
        where doctor_id = %s;
        """

        try:
            rows_count = self.db.execute_with_result(query, (is_active, doctor_id))
            if rows_count == 0:
                raise DoctorNotFound(doctor_id=doctor_id)
        except DoctorNotFound as e:
            raise e
        except Exception as e:
            print("Ошибка при создании доктора в таблице", e)

    def check_telegram_blacklist(self, telegram: str) -> bool:
        query = f"""
            select exists(
                select 1 from telegram_blacklist
                where is_active is true 
                and (telegram_username ilike '%{telegram}%' OR telegram_name ilike '%{telegram}%')
            )
        """
        try:
            results = self.db.select(query)
            return results[0][0]
        except Exception as e:
            print("Ошибка при поиске канала в чс", e)

    # def migrate_instagram(self, doctor_id: int, instagram_channel_name: str):
    #     query = f"""
    #     update doctors
    #     set
    #         instagram_channel_name = %s
    #     where doctor_id = %s;
    #     """
    #
    #     try:
    #         rows_count = self.db.execute_with_result(query, (instagram_channel_name, doctor_id))
    #         if rows_count == 0:
    #             raise DoctorNotFound(doctor_id=doctor_id)
    #     except DoctorNotFound as e:
    #         raise e
    #     except Exception as e:
    #         print("Ошибка при создании доктора в таблице", e)
