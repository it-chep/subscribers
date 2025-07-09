create table if not exists instagram_api_settings
(
    id                 serial primary key,
    req_capacity       bigint,       -- количество объем запросов, которые вообще можно сделать
    filled_capacity    bigint,       -- сколько запросов было произведено
    last_updated_time  timestamp,    -- когда был сброшен счетчик запросов
    long_access_token  varchar(255), -- долгий токен доступа к аккаунту
    short_access_token varchar(255), -- долгий токен доступа к аккаунту
    is_active          bool          -- активен ли токен
);