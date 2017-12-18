# -*- coding: utf-8 -*-

from alipay import AliPay
from Crypto.PublicKey import RSA

class AliPayKeyStr(AliPay):

    @property
    def app_private_key(self):
        """
        签名用
        """
        if not self._app_private_key:
            self._app_private_key = RSA.importKey(self._app_private_key_path)

        return self._app_private_key

    @property
    def alipay_public_key(self):
        """
        验证签名用
        """
        if not self._alipay_public_key:
            self._alipay_public_key = RSA.importKey(self._alipay_public_key_path)

        return self._alipay_public_key
