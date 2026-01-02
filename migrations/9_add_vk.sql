create table if not exists update_vk_subscribers_queue
(
    id                serial primary key,
    id_in_subscribers bigint,
    last_updated_id   bigint,
    last_updated_at   timestamp
);

-- Добавление полей с вк
alter table doctors
    add column vk_channel_name varchar(255),
    add column vk_subs_count   bigint,
    add column vk_last_updated timestamp;
