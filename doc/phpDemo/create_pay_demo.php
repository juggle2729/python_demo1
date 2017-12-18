<?php
    $url = "http://p.51paypay.net/api/v1/pay/submit";
    $appid = "100000";  // 测试appid
    $appkey = "a1223b981e74cfd29bcb628877b08b17"; // 测试appkey
    $p = array(
        "amount" => "1",
        "appid" => $appid,
        "orderid" => date('YmdHis'),
        "payType" => "2",
        "notifyUrl" => "127.0.0.1",
        "orderInfo" => "支付测试",
    );
    $s = "";
    ksort($p);
    foreach($p as $k => $v){
        $s .= $k ."=" .$v ."&";
    }
    $s .= "key=".$appkey;
    $p["signature"] = md5($s);

    $p = json_encode($p);

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $p);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            'Content-Type: application/json; charset=utf-8',
        )
    );
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $result = curl_exec($ch);

    echo $result;
