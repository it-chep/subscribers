alter table doctors
    add column manual_inst_upgrade bool not null default false,
    add column is_active           bool not null default false;