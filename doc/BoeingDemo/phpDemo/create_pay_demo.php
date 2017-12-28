<?php
    $url = "http://47.96.154.221/api/v1/pay/submit";
    $appid = "50000641";  // 测试appid
    $appkey = "3708ccfeb4e6eefec330ca659b6171be"; // 测试appkey
    $p = array(
        "amount" => "1",
        "appid" => $appid,
        "orderid" => date('YmdHis'),
        "payType" => "23",
        "subject" => "Test",
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
