-- черный список телеграм каналов
create table if not exists telegram_blacklist
(
    id                bigserial primary key,
    telegram_username text,
    telegram_name     text,
    is_active         bool default true
)