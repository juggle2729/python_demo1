create table transaction(
    id int auto_increment,
    accountid int,
    trans_type tinyint,
    charge_type tinyint,   -- 充值类型, QQ, 网银
    amount decimal(10, 5),
    recharge_id bigint default null,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp on update current_timestamp,
    primary key(id),
);
