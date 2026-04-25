from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_files_batch.application import BatchService, GroupService, QueryBatchService
from deps_files_batch.constants import PROJECT_NAME
from deps_files_batch.domain.model import (
    ICommandBatchRepository,
    IQueryBatchRepository,
    IQueryGroupRepository,
)
from deps_files_batch.extras import DatabaseSession
from deps_files_batch.infrastructure.access_management import user
from deps_files_batch.infrastructure.repositories import (
    QueryBatchRepository,
    QueryGroupRepository,
    UoWCommandBatchRepository,
)
from deps_files_batch.infrastructure.unit_of_work import (
    AbstractUnitOfWork,
    SqlAlchemyUnitOfWork,
)
from deps_files_batch.messaging.dispatcher import make_message_dispatcher

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_session: providers.Provider[DatabaseSession] = providers.Singleton(
        DatabaseSession,
        config.user,
        config.password,
        config.host,
        config.port,
        config.db,
        config.dialect,
        config.driver,
        require_secure_transport=config.require_secure_transport,
        pool_size=config.pool_size,
    )


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()
    datasources = providers.DependenciesContainer()

    query_group: providers.Singleton[IQueryGroupRepository] = providers.Singleton(
        QueryGroupRepository,
        database=datasources.postgres_session,
    )

    query_batch: providers.Singleton[IQueryBatchRepository] = providers.Singleton(
        QueryBatchRepository,
        datasources.postgres_session,
    )
    command_batch: providers.Singleton[ICommandBatchRepository] = providers.Singleton(
        UoWCommandBatchRepository,
        datasources.postgres_session,
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)
    current_user_tenant = providers.Callable(lambda: user.get()["organisation"])

    datasources: providers.Container[Datasources] = providers.Container(
        Datasources,
        config=config.database,
    )

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        config=config,
        datasources=datasources,
    )

    core: providers.Container[Core] = providers.Container(Core, config=config)
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )

    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )

    command_producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )

    domain_event_publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )

    message_dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )

    unit_of_work: providers.Singleton[AbstractUnitOfWork] = providers.Singleton(
        SqlAlchemyUnitOfWork,
        database_session=datasources.postgres_session,
    )

    group_service: providers.Singleton[GroupService] = providers.Singleton(
        GroupService,
        unit_of_work=unit_of_work,
        command_producer=command_producer,
    )
    batch_service: providers.Singleton[BatchService] = providers.Singleton(
        BatchService,
        unit_of_work=unit_of_work,
        command_producer=command_producer,
        domain_event_publisher=domain_event_publisher,
    )
    query_batch_service: providers.Singleton[QueryBatchService] = providers.Singleton(
        QueryBatchService,
        query_batch_repository=repositories.query_batch,
    )
