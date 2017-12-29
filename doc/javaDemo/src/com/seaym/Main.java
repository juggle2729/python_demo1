package com.seaym;

import java.net.URLDecoder;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import org.apache.http.HttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.util.EntityUtils;

import com.alibaba.fastjson.JSONObject;

@SuppressWarnings("deprecation")
public class Main {

	public static void main(String[] args) {
		
		pay(1,orderid,notifyUrl);
	}

	static String orderid = "100000001";
	
	static String notifyUrl = "http://yoururl.com";
	
	static String url = "http://47.96.154.221/api/v1/pay/submit";
	
	static String appid = "50000641";
	
	static String APP_KEY = "3708ccfeb4e6eefec330ca659b6171be";
	
	static int payType = 23;
	
	static String subject = "Test";

	@SuppressWarnings({ "deprecation", "resource" })
	public static void pay(int amount,String orderid,String notifyUrl){
        //post请求返回结果
        DefaultHttpClient httpClient = new DefaultHttpClient();
        HttpPost method = new HttpPost(url);
        
        //参数拼接
        String originStr = String.format("amount=%s&appid=%s&notifyUrl=%s&orderid=%s&payType=%s&subject=%s&key=%s", 
        		amount,appid,notifyUrl,orderid,payType,subject,APP_KEY);
        System.out.println("originStr="+originStr);
        String signature = getMd5(originStr);
        System.out.println("signature="+signature);
		JSONObject params = new JSONObject();
        params.put("amount", amount);
        params.put("appid", appid);
        params.put("orderid", orderid);
        params.put("payType", payType);
        params.put("notifyUrl", notifyUrl);
        params.put("signature", signature);
        System.out.println(params.toJSONString());
        
        try {
            if (null != params) {
            	//解决中文乱码问题
            	StringEntity entity = new StringEntity(params.toString(), "utf-8");
                entity.setContentEncoding("UTF-8");
                entity.setContentType("application/json");
                method.setEntity(entity);
            }
            HttpResponse result = httpClient.execute(method);
            url = URLDecoder.decode(url, "UTF-8");
            /**请求发送成功，并得到响应**/
            if (result.getStatusLine().getStatusCode() == 200) {
                String str = "";
                try {
                    /**读取服务器返回过来的json字符串数据**/
                    str = EntityUtils.toString(result.getEntity());
                    System.out.println("请求回来的数据："+ str);
                } catch (Exception e) {
                    System.err.println("post请求提交失败:" + url);
                }
            }else {
            	System.out.println("请求码 ="+result.getStatusLine().getStatusCode());
            }
        } catch (Exception e) {
        	System.err.println("post请求提交失败:" + url);
        }
    }
	
	public static String getMd5(String plainText) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            md.update(plainText.getBytes());
            byte b[] = md.digest();

            int i;

            StringBuffer buf = new StringBuffer("");
            for (int offset = 0; offset < b.length; offset++) {
                i = b[offset];
                if (i < 0)
                    i += 256;
                if (i < 16)
                    buf.append("0");
                buf.append(Integer.toHexString(i));
            }
            //32位加密
            return buf.toString();
            // 16位的加密
            //return buf.toString().substring(8, 24);
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
            return null;
        }

    }
}
