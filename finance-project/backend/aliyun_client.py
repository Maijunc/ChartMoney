from typing import Optional
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dypnsapi20170525.client import Client as DypnsClient

from config import settings


class AliyunSMSClient:
    """
    阿里云短信客户端封装
    """
    
    _client_instance: Optional[DypnsClient] = None
    
    @classmethod
    def get_client(cls) -> DypnsClient:
        """
        获取阿里云短信客户端单例
        """
        if cls._client_instance is None:
            cls._client_instance = cls._create_client()
        return cls._client_instance
    
    @classmethod
    def _create_client(cls) -> DypnsClient:
        """
        创建阿里云客户端
        """
        try:
            # 方法1：使用阿里云凭据链（自动从环境变量读取）
            # 这是最推荐的方式，SDK会自动读取 ALIBABA_CLOUD_ACCESS_KEY_ID 等环境变量
            # credential = CredentialClient()
            
            # 方法2：如果上述方法不工作，可以显式传入
            from alibabacloud_credentials.models import Config as CredentialConfig
            credential_config = CredentialConfig(
                type='access_key',
                access_key_id=settings.alibabacloud_access_key_id,
                access_key_secret=settings.alibabacloud_access_key_secret
            )
            credential = CredentialClient(credential_config)
            
            config = open_api_models.Config(
                credential=credential,
                endpoint='dypnsapi.aliyuncs.com',  # 号码认证服务Endpoint
                read_timeout=10000,  # 10秒超时
                connect_timeout=5000,  # 5秒连接超时
            )
            
            client = DypnsClient(config)
            return client
            
        except Exception as e:
            raise


# 全局客户端实例
sms_client = AliyunSMSClient.get_client()