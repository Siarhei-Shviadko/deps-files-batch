PROJECT_NAME = "files-batch"
DESCRIPTION = "Short description of project"
V1_PREFIX = "/v1"
BASE_API_PREFIX = "/api/files-batch"
V1_API_PREFIX = BASE_API_PREFIX + V1_PREFIX
INTERNAL_API_PREFIX = "/api-internal/files-batch"
SWAGGER_DOC_URL = "/docs"

DOCUMENTS_EXCHANGER = "Documents"

EVENTS_QUEUE = "files-batch-events"
COMMANDS_QUEUE = "files-batch-commands"

COMMANDS_CHANNEL = "BatchCommands"
COMMANDS_REPLIES_CHANNEL = "BatchCommandsReplies"
DOCUMENT_COMMANDS_CHANNEL = "DocumentCommands"
CLASSIFICATION_COMMANDS_CHANNEL = "ClassificationCommands"

USER_DESTINATION = "User"
GROUP_DESTINATION = "Group"
DOCUMENT_TYPE_EXCHANGER = "DocumentType"

DEFAULT_PAGE = 0
DEFAULT_PER_PAGE = 10

METADATA_BATCH_ID_KEY = "batch_id"
METADATA_BATCH_FILE_ID_KEY = "batch_file_id"
