-- Очередь обновления ютуба
create table if not exists update_youtube_subscribers_queue
(
    id                serial primary key,
    id_in_subscribers bigint,
    last_updated_id   bigint,
    last_updated_at   timestamp
);

-- Добавление полей с ютубом
alter table doctors
    add column youtube_channel_name varchar(255),
    add column youtube_subs_count   bigint,
    add column youtube_last_updated timestamp;
