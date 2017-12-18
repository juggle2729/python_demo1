/ **
记录测试环境数据的增删改，上线时同步到线上数据库
*/

-- 海羽毛-客达 支付宝D1 扫码付包装为H5
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    1, 100002, '880357ccd28db91f6f0f88d54889c34c', '00000000353000000042', 22, 1, 2, '海羽毛', '308584000013', 'D1', 40
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name,  fee_rate)
values(
    1, 100002, '880357ccd28db91f6f0f88d54889c34c', '170822211012020', 22, 1, 1, '海羽毛', 40
);

-- 海南零卖 幸运三张 微信H5支付
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, sceneInfo) values (
    9, 30000057, '537896a7057a267f087e5505503f8276', '170824215216255', 1, 1, 1, '海南翎麦', 100,
    '{"wap_url": "http://www.allgo-game.com/", "type": "Wap", "wap_name": "海南翎麦"}'
);

-- 上海桔梗 支付宝H5 D1  --- 客达
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    18, 30000101, '14899c0c0a2803a4c0138c5c432d697a', '00000000353000000052', 22, 1, 2, '上海桔梗', '308584000013', 'D1', 200
);

-- 梦工厂 支付宝H5 D1  --- 客达
/* 未注册账号，暂时不开通
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    18, 30000102, '7913118cc7c409411788930d86804cbd', '00000000353000000051', 22, 1, 2, '上海桔梗', '308584000013', 'D1', 120
);
*/

-- 深圳缘游
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    32, 30000201, '295bff0773b265ac9e1f1aac5ddfad4e', '00000000353000000051', 22, 1, 2, '深圳缘游', '308584000013', 'D1', 150
);


-- 武汉趣享 光大支付宝扫码转H5 1.5% --> 武汉亿昆(改名了)
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    32, 30000301, '7ca1aea0f1dcd64b641d2b242e8d743f', '00000000353000000082', 22, 1, 2, '武汉亿昆科技', '308584000013', 'D1', 150
);


-- 测试数据 轮询
insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    1, 100003, '880357ccd28db91f6f0f88d54889c34c', 21, 1, 1, '海羽毛', 40, 1
);
insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    1, 100005, '880357ccd28db91f6f0f88d54889c34c', 2, 1, 2, '海羽毛轮询', 40, 1
);
insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    1, 100006, '880357ccd28db91f6f0f88d54889c34c', 11, 1, 5, '海羽毛轮询', 40, 1
);
insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    1, 100007, '880357ccd28db91f6f0f88d54889c34c', 21, 1, 2, '海羽毛轮询', 40, 1
);


-- 快易付信息
insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    1, 100008, '215a7ab33f4a479cb12a7ac0996f7fb3', 2, 1, 5, '快易付信息', 0, 1
);
insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    1, 100008, '215a7ab33f4a479cb12a7ac0996f7fb3', 21, 1, 5, '快易付信息', 0, 1
);
insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    1, 100008, '215a7ab33f4a479cb12a7ac0996f7fb3', 11, 1, 5, '快易付信息', 0, 1
);


-- 海羽毛-原生支付宝测试
insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    1, 100009, '115a7ab33f4a479cb12a7ac0996f7fb1', 23, 1, 6, '海羽毛原生支付宝测试', 0, 1
);


insert into polling_custid(
    appid, custid, pay_type, real_pay, valid, mch_name, father_mch_name)
values (
    100003, 170822211012020, 21, 1, 1, '轮询商户1', '海羽毛'
);


-- 海羽毛-杉德 微信扫码
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name,  fee_rate)
values(
    1, 100004, '6e8981acf8db427890456d63d2c7a448', 'P47428', 2, 1, 3, '海羽毛', 40
);

-- 海羽毛-杉德 支付宝扫码
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name,  fee_rate)
values(
    1, 100004, '6e8981acf8db427890456d63d2c7a448', 'P47428', 21, 1, 3, '海羽毛', 40
);


insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000501,'5f247c528511c56770bb8499a9681074', '00000000353000000105', 2, 1, 2, "广州莱双", 80, '310290000013', 'D0'
);


insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000501,'5f247c528511c56770bb8499a9681074', '00000000353000000105', 21, 1, 2, "广州莱双", 80, '310290000013', 'D0'
);

-- 广州莱双浦发D0
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000502,'5f247c528511c56770bb8499a9681074', '00000000353000000105', 21, 1, 2, "广州莱双", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000502,'5f247c528511c56770bb8499a9681074', '00000000353000000105', 2, 1, 2, "广州莱双", 80, '308584000013', 'D1'
);

-- 广州莱双招行D1
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000502,'5f247c528511c56770bb8499a9681074', '00000000353000000105', 21, 1, 2, "广州莱双", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000502,'5f247c528511c56770bb8499a9681074', '00000000353000000105', 2, 1, 2, "广州莱双", 80, '308584000013', 'D1'
);


-- 湖南马总 35 招行

-- 深圳市南山区牛牛乐贸易商行  2c2d8b8b496a4ccdb84f70d5ac6ef2c3
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000503,'2c2d8b8b496a4ccdb84f70d5ac6ef2c3', '00000000353000000086', 2, 1, 2, "牛牛乐", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000503,'2c2d8b8b496a4ccdb84f70d5ac6ef2c3', '00000000353000000086', 21, 1, 2, "牛牛乐", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000503,'2c2d8b8b496a4ccdb84f70d5ac6ef2c3', '00000000353000000086', 22, 1, 2, "牛牛乐", 80, '308584000013', 'D1'
);

-- 保定市徐水区东丽网络科技工作室  0698d94594b049789dae573f09564eaf
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000504,'0698d94594b049789dae573f09564eaf', '00000000353000000097', 2, 1, 2, "东丽网络科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000504,'0698d94594b049789dae573f09564eaf', '00000000353000000097', 21, 1, 2, "东丽网络科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000504,'0698d94594b049789dae573f09564eaf', '00000000353000000097', 22, 1, 2, "东丽网络科技", 80, '308584000013', 'D1'
);

-- 丰宁满族自治县鹏夏商贸有限公司  195203f38cee4d47b0a6c8a44d6b081c
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000505,'195203f38cee4d47b0a6c8a44d6b081c', '00000000353000000120', 2, 1, 2, "鹏夏商贸", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000505,'195203f38cee4d47b0a6c8a44d6b081c', '00000000353000000120', 21, 1, 2, "鹏夏商贸", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000505,'195203f38cee4d47b0a6c8a44d6b081c', '00000000353000000120', 22, 1, 2, "鹏夏商贸", 80, '308584000013', 'D1'
);

-- 顺平梦飞日化店  f6222da57b4d4eadbcc95568062e1d36

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000506,'f6222da57b4d4eadbcc95568062e1d36', '00000000353000000121', 2, 1, 2, "顺平梦飞日化店", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000506,'f6222da57b4d4eadbcc95568062e1d36', '00000000353000000121', 21, 1, 2, "顺平梦飞日化店", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000506,'f6222da57b4d4eadbcc95568062e1d36', '00000000353000000121', 22, 1, 2, "顺平梦飞日化店", 80, '308584000013', 'D1'
);

-- 成都赢丰无线科技有限公司  8078325f52604b4cb75743891308c3a3

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000507,'8078325f52604b4cb75743891308c3a3', '00000000353000000122', 2, 1, 2, "赢丰无线科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000507,'8078325f52604b4cb75743891308c3a3', '00000000353000000122', 21, 1, 2, "赢丰无线科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000507,'8078325f52604b4cb75743891308c3a3', '00000000353000000122', 22, 1, 2, "赢丰无线科技", 80, '308584000013', 'D1'
);


-- 湖南马总 35 浦发 D0

-- 深圳市南山区牛牛乐贸易商行  9906d1e8ac624c8ab16413e15ee1ed42
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000508,'9906d1e8ac624c8ab16413e15ee1ed42', '00000000353000000086', 2, 1, 2, "牛牛乐", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000508,'9906d1e8ac624c8ab16413e15ee1ed42', '00000000353000000086', 21, 1, 2, "牛牛乐", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000508,'9906d1e8ac624c8ab16413e15ee1ed42', '00000000353000000086', 22, 1, 2, "牛牛乐", 80, '310290000013', 'D0'
);

-- 保定市徐水区东丽网络科技工作室  efd947a6627046ecb1d1fcdc6c6075a6
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000509,'efd947a6627046ecb1d1fcdc6c6075a6', '00000000353000000097', 2, 1, 2, "东丽网络科技", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000509,'efd947a6627046ecb1d1fcdc6c6075a6', '00000000353000000097', 21, 1, 2, "东丽网络科技", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000509,'efd947a6627046ecb1d1fcdc6c6075a6', '00000000353000000097', 22, 1, 2, "东丽网络科技", 80, '310290000013', 'D0'
);

-- 丰宁满族自治县鹏夏商贸有限公司  140c89a4dab241c2afb37e2fa9b7ab83
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000510,'140c89a4dab241c2afb37e2fa9b7ab83', '00000000353000000120', 2, 1, 2, "鹏夏商贸", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000510,'140c89a4dab241c2afb37e2fa9b7ab83', '00000000353000000120', 21, 1, 2, "鹏夏商贸", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000510,'140c89a4dab241c2afb37e2fa9b7ab83', '00000000353000000120', 22, 1, 2, "鹏夏商贸", 80, '310290000013', 'D0'
);

-- 顺平梦飞日化店  1f068a4e79b94ccda63023d397bad325

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000511,'1f068a4e79b94ccda63023d397bad325', '00000000353000000121', 2, 1, 2, "顺平梦飞日化店", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000511,'1f068a4e79b94ccda63023d397bad325', '00000000353000000121', 21, 1, 2, "顺平梦飞日化店", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000511,'1f068a4e79b94ccda63023d397bad325', '00000000353000000121', 22, 1, 2, "顺平梦飞日化店", 80, '310290000013', 'D0'
);

-- 成都赢丰无线科技有限公司  bb8a51dc20214bc188ed1a4eed665523

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000512,'bb8a51dc20214bc188ed1a4eed665523', '00000000353000000122', 2, 1, 2, "赢丰无线科技", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000512,'bb8a51dc20214bc188ed1a4eed665523', '00000000353000000122', 21, 1, 2, "赢丰无线科技", 80, '310290000013', 'D0'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000512,'bb8a51dc20214bc188ed1a4eed665523', '00000000353000000122', 22, 1, 2, "赢丰无线科技", 80, '310290000013', 'D0'
);


-- 11.13 湖南马总过审N多件  招商
-- 合肥驰景信息科技有限公司 8381177c247543ceb5d354c9fe2bcbd0  30000520 00000000353000000115
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000520,'8381177c247543ceb5d354c9fe2bcbd0', '00000000353000000115', 2, 1, 2, "驰景信息科技", 80, '308584000013', 'D1'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000520,'8381177c247543ceb5d354c9fe2bcbd0', '00000000353000000115', 21, 1, 2, "驰景信息科技", 80, '308584000013', 'D1'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000520,'8381177c247543ceb5d354c9fe2bcbd0', '00000000353000000115', 22, 1, 2, "驰景信息科技", 80, '308584000013', 'D1'
);

-- 广州熙桐生物科技有限公司 23b4c4b5b3be4497ad1b381ccb2ac267  30000521  00000000353000000094
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000521,'23b4c4b5b3be4497ad1b381ccb2ac267', '00000000353000000094', 2, 1, 2, "熙桐生物科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000521,'23b4c4b5b3be4497ad1b381ccb2ac267', '00000000353000000094', 21, 1, 2, "熙桐生物科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000521,'23b4c4b5b3be4497ad1b381ccb2ac267', '00000000353000000094', 22, 1, 2, "熙桐生物科技", 80, '308584000013', 'D1'
);

-- 北京华盛恒力商贸有限公司 ef1293127cac42b4b33f07bce679d3a1  30000522 00000000353000000088
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000522,'ef1293127cac42b4b33f07bce679d3a1', '00000000353000000088', 2, 1, 2, "熙桐生物科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000522,'ef1293127cac42b4b33f07bce679d3a1', '00000000353000000088', 21, 1, 2, "熙桐生物科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000522,'ef1293127cac42b4b33f07bce679d3a1', '00000000353000000088', 22, 1, 2, "熙桐生物科技", 80, '308584000013', 'D1'
);

-- 北京云海新越科技有限公司 050100b28b07466d85189466e8c298fe  30000523 00000000353000000091
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000523,'050100b28b07466d85189466e8c298fe', '00000000353000000091', 2, 1, 2, "云海新越科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000523,'050100b28b07466d85189466e8c298fe', '00000000353000000091', 21, 1, 2, "云海新越科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000523,'050100b28b07466d85189466e8c298fe', '00000000353000000091', 22, 1, 2, "云海新越科技", 80, '308584000013', 'D1'
);

-- 北京赛烁科技有限公司 9451ece76e54449284aa1eaada4d8b8b  30000524 00000000353000000095

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000524,'9451ece76e54449284aa1eaada4d8b8b', '00000000353000000095', 2, 1, 2, "赛烁科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000524,'9451ece76e54449284aa1eaada4d8b8b', '00000000353000000095', 21, 1, 2, "赛烁科技", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000524,'9451ece76e54449284aa1eaada4d8b8b', '00000000353000000095', 22, 1, 2, "赛烁科技", 80, '308584000013', 'D1'
);

-- 成华区基强达商务信息咨询服务部 041cbac6dd0b4ece98c1b18e99a92b8f 30000525 00000000353000000102

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000525,'041cbac6dd0b4ece98c1b18e99a92b8f', '00000000353000000102', 2, 1, 2, "基强达商务信息咨询", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000525,'041cbac6dd0b4ece98c1b18e99a92b8f', '00000000353000000102', 21, 1, 2, "基强达商务信息咨询", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000525,'041cbac6dd0b4ece98c1b18e99a92b8f', '00000000353000000102', 22, 1, 2, "基强达商务信息咨询", 80, '308584000013', 'D1'
);

-- 成都惠彩商贸有限公司 b15599746ded43c5ab1034eb7c2c6af8 30000526 00000000353000000099

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000526,'b15599746ded43c5ab1034eb7c2c6af8', '00000000353000000099', 2, 1, 2, "惠彩商贸", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000526,'b15599746ded43c5ab1034eb7c2c6af8', '00000000353000000099', 21, 1, 2, "惠彩商贸", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000526,'b15599746ded43c5ab1034eb7c2c6af8', '00000000353000000099', 22, 1, 2, "惠彩商贸", 80, '308584000013', 'D1'
);

-- 北京达兴腾商贸有限公司 e2cf4e264fba43579051ed81a2e61796 30000527  00000000353000000117

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000527,'e2cf4e264fba43579051ed81a2e61796', '00000000353000000117', 2, 1, 2, "达兴腾商贸", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000527,'e2cf4e264fba43579051ed81a2e61796', '00000000353000000117', 21, 1, 2, "达兴腾商贸", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000527,'e2cf4e264fba43579051ed81a2e61796', '00000000353000000117', 22, 1, 2, "达兴腾商贸", 80, '308584000013', 'D1'
);


-- 沈阳金鸿鑫盛商贸有限公司 7191a4676d004d4a95449c286c39c0e0 30000528  00000000353000000118
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000528,'7191a4676d004d4a95449c286c39c0e0', '00000000353000000118', 2, 1, 2, "金鸿鑫盛商贸", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000528,'7191a4676d004d4a95449c286c39c0e0', '00000000353000000118', 21, 1, 2, "金鸿鑫盛商贸", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000528,'7191a4676d004d4a95449c286c39c0e0', '00000000353000000118', 22, 1, 2, "金鸿鑫盛商贸", 80, '308584000013', 'D1'
);

-- 淄博优浦贸易有限公司 20bf3c5818334c96a87e9edbfd73ff9d 30000529 00000000353000000119

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000529,'20bf3c5818334c96a87e9edbfd73ff9d', '00000000353000000119', 2, 1, 2, "优浦贸易", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000529,'20bf3c5818334c96a87e9edbfd73ff9d', '00000000353000000119', 21, 1, 2, "优浦贸易", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000529,'20bf3c5818334c96a87e9edbfd73ff9d', '00000000353000000119', 22, 1, 2, "优浦贸易", 80, '308584000013', 'D1'
);

-- 深圳市优贝尔婴童用品有限公司 03b1c13253184d04a8f5a4b4664915a1 30000530  00000000353000000100

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000530,'03b1c13253184d04a8f5a4b4664915a1', '00000000353000000100', 2, 1, 2, "优贝尔婴童", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000530,'03b1c13253184d04a8f5a4b4664915a1', '00000000353000000100', 21, 1, 2, "优贝尔婴童", 80, '308584000013', 'D1'
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000530,'03b1c13253184d04a8f5a4b4664915a1', '00000000353000000100', 22, 1, 2, "优贝尔婴童", 80, '308584000013', 'D1'
);


-- 11.14下参数

-- 长沙市雨花区王佳妮小吃店  招行 D1  5b4f3a73c6b340b7961a787db3ba202e  30000540  00000000353000000108
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000540,'5b4f3a73c6b340b7961a787db3ba202e', '00000000353000000108', 2, 1, 2, "王佳妮小吃店", 80, '308584000013', 'D1'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000540,'5b4f3a73c6b340b7961a787db3ba202e', '00000000353000000108', 21, 1, 2, "王佳妮小吃店", 80, '308584000013', 'D1'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000540,'5b4f3a73c6b340b7961a787db3ba202e', '00000000353000000108', 22, 1, 2, "王佳妮小吃店", 80, '308584000013', 'D1'
);
-- 盱眙杨娟酒业有限公司 浦发 D0 8f721e6515674fe6bfab2a00eaf771c0  30000541  00000000353000000125
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000541,'8f721e6515674fe6bfab2a00eaf771c0', '00000000353000000125', 2, 1, 2, "杨娟酒业", 80, '310290000013', 'D0'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000541,'8f721e6515674fe6bfab2a00eaf771c0', '00000000353000000125', 21, 1, 2, "杨娟酒业", 80, '310290000013', 'D0'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000541,'8f721e6515674fe6bfab2a00eaf771c0', '00000000353000000125', 22, 1, 2, "杨娟酒业", 80, '310290000013', 'D0'
);
-- 广州莱双信息科技有限公司 浦发 D0 0fc6a488424942ae92b50d20b80b657c ~30000542~  00000000353000000105  已进
-- 新罗区冬平伊便利店 浦发 D0 0c21a683d2e0423ab73895b7d6c8472e 30000543  00000000353000000106
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000543,'0c21a683d2e0423ab73895b7d6c8472e', '00000000353000000106', 2, 1, 2, "冬平伊便利店", 80, '310290000013', 'D0'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000543,'0c21a683d2e0423ab73895b7d6c8472e', '00000000353000000106', 21, 1, 2, "冬平伊便利店", 80, '310290000013', 'D0'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000543,'0c21a683d2e0423ab73895b7d6c8472e', '00000000353000000106', 22, 1, 2, "冬平伊便利店", 80, '310290000013', 'D0'
);
-- 博罗县福田镇钟锦荣水产养殖场 浦发 D0 748e6830873344ba9d9bb9a0d938c72a 30000544  00000000353000000111
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000544,'748e6830873344ba9d9bb9a0d938c72a', '00000000353000000111', 2, 1, 2, "钟锦荣水产养殖场", 80, '310290000013', 'D0'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000544,'748e6830873344ba9d9bb9a0d938c72a', '00000000353000000111', 21, 1, 2, "钟锦荣水产养殖场", 80, '310290000013', 'D0'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000544,'748e6830873344ba9d9bb9a0d938c72a', '00000000353000000111', 22, 1, 2, "钟锦荣水产养殖场", 80, '310290000013', 'D0'
);


-- 11.14 湖南马总

-- 北京达书亮科技有限公司  b60963fb7fbb494fa8779df266670fd3 30000545  招行 D1
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000545,'b60963fb7fbb494fa8779df266670fd3', '00000000353000000101', 2, 1, 2, "达书亮科技", 80, '308584000013', 'D1'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000545,'b60963fb7fbb494fa8779df266670fd3', '00000000353000000101', 21, 1, 2, "达书亮科技", 80, '308584000013', 'D1'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    35,  30000545,'b60963fb7fbb494fa8779df266670fd3', '00000000353000000101', 22, 1, 2, "达书亮科技", 80, '308584000013', 'D1'
);


-- 11.15
-- 长沙市雨花区王佳妮小吃店  浦发 D0  1386157083764f518ed612fb9f58503e 30000546  00000000353000000108
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000546,'1386157083764f518ed612fb9f58503e', '00000000353000000108', 2, 1, 2, "王佳妮小吃店", 80, '310290000013', 'D0'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000546,'1386157083764f518ed612fb9f58503e', '00000000353000000108', 21, 1, 2, "王佳妮小吃店", 80, '310290000013', 'D0'
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, fee_rate, banklinknumber, paymenttype
)values(
    38,  30000546,'1386157083764f518ed612fb9f58503e', '00000000353000000108', 22, 1, 2, "王佳妮小吃店", 80, '310290000013', 'D0'
);


-- 武汉亿昆 招行 D1  00000000353000000114  b1bccea3a1834169a1bdb648bc4ba97a  30000550
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    32, 30000550, 'b1bccea3a1834169a1bdb648bc4ba97a', '00000000353000000114', 22, 1, 2, '武汉亿昆科技', '308584000013', 'D1', 150
);

-- 11.15 湖南马总 招商 D1

-- 北京鸣远凯利贸易有限公司  00000000353000000113 9b3c275cfaaf4c65a71995388169419d  30000551
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000551, '9b3c275cfaaf4c65a71995388169419d', '00000000353000000113', 2, 1, 2, '鸣远凯利贸易', '308584000013', 'D1', 80 
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000551, '9b3c275cfaaf4c65a71995388169419d', '00000000353000000113', 21, 1, 2, '鸣远凯利贸易', '308584000013', 'D1', 80 
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000551, '9b3c275cfaaf4c65a71995388169419d', '00000000353000000113', 22, 1, 2, '鸣远凯利贸易', '308584000013', 'D1', 80 
);

-- 桂林洛克网络科技有限公司  00000000353000000123 728b36bfded34b57a0bc77f77bf82e07  30000552
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000552, '728b36bfded34b57a0bc77f77bf82e07', '00000000353000000123', 2, 1, 2, '洛克网络科技', '308584000013', 'D1', 80 
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000552, '728b36bfded34b57a0bc77f77bf82e07', '00000000353000000123', 21, 1, 2, '洛克网络科技', '308584000013', 'D1', 80 
);

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000552, '728b36bfded34b57a0bc77f77bf82e07', '00000000353000000123', 22, 1, 2, '洛克网络科技', '308584000013', 'D1', 80 
);

-- 11.17 湖南马总 招商 D1 

-- 深圳市桂春贸易有限公司 30000553  c6b77f3f53b5484887c61d901f211574  00000000353000000127
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000553, 'c6b77f3f53b5484887c61d901f211574', '00000000353000000127', 2, 1, 2, '桂春贸易', '308584000013', 'D1', 80 
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000553, 'c6b77f3f53b5484887c61d901f211574', '00000000353000000127', 21, 1, 2, '桂春贸易', '308584000013', 'D1', 80 
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000553, 'c6b77f3f53b5484887c61d901f211574', '00000000353000000127', 22, 1, 2, '桂春贸易', '308584000013', 'D1', 80 
);
-- 广州珐嘉贸易有限公司  30000554  0e03007ab9674602a6f35572663fe355  00000000353000000128

insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000554, '0e03007ab9674602a6f35572663fe355', '00000000353000000128', 2, 1, 2, '珐嘉贸易', '308584000013', 'D1', 80 
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000554, '0e03007ab9674602a6f35572663fe355', '00000000353000000128', 21, 1, 2, '珐嘉贸易', '308584000013', 'D1', 80 
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    35, 30000554, '0e03007ab9674602a6f35572663fe355', '00000000353000000128', 22, 1, 2, '珐嘉贸易', '308584000013', 'D1', 80 
);

-- 11.24 武汉趣享 杉德
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    41, 30000555, 'e179a74b11f348eca4248f069663b132', 'Z7743381', 2, 1, 3, '武汉亿昆科技', '', '', 150
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    41, 30000555, 'e179a74b11f348eca4248f069663b132', 'Z7743381', 21, 1, 3, '武汉亿昆科技', '', '', 150
);
insert into account_appid(
    accountid, appid, appkey, custid, pay_type, valid, real_pay, mch_name, banklinknumber, paymenttype, fee_rate)
values(
    41, 30000555, 'e179a74b11f348eca4248f069663b132', 'Z7743381', 22, 1, 3, '武汉亿昆科技', '', '', 150
);

insert into account_appid(
    accountid, appid, appkey, pay_type, valid, real_pay, mch_name,  fee_rate, polling)
values(
    41, 30000556, '13ac71eb1af54f118dd99096f395fe55', 11, 1, 5, '武汉亿昆科技', 40, 0
);
