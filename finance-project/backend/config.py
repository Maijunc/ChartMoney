import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    应用配置类
    从环境变量或.env文件读取配置
    """
    
    # ========== 阿里云配置 ==========
    # 这些值会自动从环境变量或.env文件加载
    alibabacloud_access_key_id: str = Field(
        ...,  # 必填项
        alias="ALIBABA_CLOUD_ACCESS_KEY_ID",
        description="阿里云AccessKey ID"
    )
    
    alibabacloud_access_key_secret: str = Field(
        ...,
        alias="ALIBABA_CLOUD_ACCESS_KEY_SECRET", 
        description="阿里云AccessKey Secret"
    )
    
    alibabacloud_sms_sign_name: str = Field(
        "速通互联验证码",  # 默认值
        alias="ALIBABA_CLOUD_SMS_SIGN_NAME",
        description="短信签名"
    )
    
    alibabacloud_sms_template_code_rl: str = Field(
        ...,
        alias="ALIBABA_CLOUD_SMS_TEMPLATE_CODE1",
        description="短信模板CODE(登陆注册)"
    )
    alibabacloud_sms_template_code_update: str = Field(
        ...,
        alias="ALIBABA_CLOUD_SMS_TEMPLATE_CODE2",
        description="短信模板CODE(更新手机)"
    )
    alibabacloud_sms_template_code_update_password: str = Field(
        ...,
        alias="ALIBABA_CLOUD_SMS_TEMPLATE_CODE3",
        description="短信模板CODE(更新密码)"
    )
    alibabacloud_sms_template_code_verify_new: str = Field(
        ...,
        alias="ALIBABA_CLOUD_SMS_TEMPLATE_CODE4",
        description="短信模板CODE(绑定新手机，但感觉用不着)"
    )
    alibabacloud_sms_template_code_verify_phone: str = Field(
        ...,
        alias="ALIBABA_CLOUD_SMS_TEMPLATE_CODE5",
        description="短信模板CODE(验证手机)"
    )
    alibabacloud_sms_template_params: str = Field(
        ...,
        alias="ALIBABA_CLOUD_SMS_TEMPLATE_PARAMS",
        description="短信模板参数(JSON字符串)"
    )
    
    # ========== 应用配置 ==========
    debug: bool = Field(False, alias="DEBUG")
    database_url: str = Field("sqlite:///./app.db", alias="DATABASE_URL")
    
    # 验证码配置
    verify_code_expire_seconds: int = 300  # 验证码有效期5分钟
    max_attempts_per_day: int = 10  # 每日最多发送次数
    
    class Config:
        # 从.env文件读取配置（优先级高于系统环境变量）
        env_file = ".env"
        env_file_encoding = "utf-8"
        # 允许使用别名和环境变量名两种方式访问
        populate_by_name = True


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例（使用缓存提高性能）
    """
    return Settings()


# 全局配置实例
settings = get_settings()


# 快速测试函数
if __name__ == "__main__":
    # 测试配置是否加载成功（不打印敏感信息）
    s = settings
    print("✅ 配置加载成功")
    print(f"  签名: {s.alibabacloud_sms_sign_name}")
    print(f"  模板: {s.alibabacloud_sms_template_code}")
    print(f"  模板参数: {s.alibabacloud_sms_template_params}")
    print(f"  调试模式: {s.debug}")
    
    # 安全地检查AccessKey是否存在（不打印具体值）
    if s.alibabacloud_access_key_id and s.alibabacloud_access_key_secret:
        print(f"  AccessKey状态: 已配置 (ID前8位: {s.alibabacloud_access_key_id[:8]}...)")
    else:
        print("  ❌ AccessKey未配置")