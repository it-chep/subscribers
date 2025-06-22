-- instagram queue
create table if not exists update_instagram_subscribers_queue
(
    id              serial primary key,
    id_in_subscribers bigint,
    last_updated_id bigint,
    last_updated_at timestamp
);