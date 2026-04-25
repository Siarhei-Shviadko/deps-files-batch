from typing import Any

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import BaseSettings, Field, validator

from deps_files_batch.extras import DatabaseSettings, ServiceInfoSettings


class Settings(BaseSettings):
    env: str = "development"
    version: str = "1.0"

    logger_level: str = Field("INFO", env="LOG_LEVEL")

    info: ServiceInfoSettings = ServiceInfoSettings()
    database: DatabaseSettings = DatabaseSettings()

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, env="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, env="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str

    documentation_enabled: bool = True
    instrumentation_enabled: bool = False

    class Config:
        use_enum_values = True

    @validator("messaging_driver_settings")
    def validate_messaging_driver_settings(cls, v, values):  # noqa: N805
        messaging_driver = values.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().dict()  # TODO: use BaseSettings

        raise ValueError(f"Driver {driver} is not implemented")
