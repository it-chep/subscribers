-- Таблица подписчиков
create table if not exists doctors
(
    id                     serial primary key,
    doctor_id              bigint unique,
    -- каналы
    instagram_channel_name varchar(255),
    telegram_channel_name  varchar(255),
    -- количество подписчиков
    inst_subs_count        int,
    tg_subs_count          int,
    -- время обновления
    inst_last_updated      timestamp,
    tg_last_updated        timestamp
);

-- Таблица доступных соц сетей
create table if not exists social_media
(
    id      serial primary key,
    -- name - отображение для пользователя
    name    varchar(255),
    -- slug - enum на стороне бекенда, гарантирует связь бд и бэка
    slug    varchar(255),
    -- включена интеграция или нет
    enabled bool
);