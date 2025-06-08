-- Таблица подписчиков
create table if not exists doctors
(
    id                     serial primary key,
    doctor_id              bigint unique,
    instagram_channel_name varchar(255),
    telegram_channel_name  varchar(255),
    inst_subs_count        int,
    tg_subs_count          int,
    inst_last_updated      timestamp,
    tg_last_updated        timestamp
);

-- Таблица доступных соц сетей
create table if not exists social_media
(
    id      serial primary key,
    name    varchar(255),
    enabled bool
);