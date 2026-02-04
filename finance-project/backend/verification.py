import os
import sys
import json

from typing import List

from alibabacloud_dypnsapi20170525.client import Client as Dypnsapi20170525Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525 import models as dypnsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from aliyun_client import sms_client
from config import settings

def send_sms(
        phone_number: str,
        code: str
    ) -> None:
        # client = Sample.create_client()
        client = sms_client
        send_sms_verify_code_request = dypnsapi_20170525_models.SendSmsVerifyCodeRequest(
            phone_number=phone_number,
            sign_name=settings.alibabacloud_sms_sign_name,
            template_code=code,
            template_param=settings.alibabacloud_sms_template_params
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.send_sms_verify_code_with_options(send_sms_verify_code_request, runtime)
            print(json.dumps(resp, default=str, indent=2))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            raise error

def verify_sms(
        phone_number: str,
        verify_code: str
    ) -> None:
        client = sms_client
        check_sms_verify_code_request = dypnsapi_20170525_models.CheckSmsVerifyCodeRequest(
             phone_number=phone_number,
             verify_code=verify_code
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = client.check_sms_verify_code_with_options(check_sms_verify_code_request, runtime)
            print(json.dumps(resp, default=str, indent=2))
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            raise error