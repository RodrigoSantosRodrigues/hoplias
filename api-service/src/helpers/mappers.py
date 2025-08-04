class Mapper:
  ENV_PRODUCTION = 'production'
  ENV_DEVELOPMENT = 'development'
  ENV_TESTING = 'testing'


class StatusCode:
  HTTP_OK = 200
  HTTP_CREATED = 201
  HTTP_NOT_CREATE_TOKEN = 450
  HTTP_NOT_TOKEN = 451
  HTTP_ERROR_TOKEN = 452
  HTTP_INVALID_TOKEN = 453
  HTTP_INVALID_USER = 454
  HTTP_NOT_ROLE = 455
  HTTP_NOT_FOUND = 404
  HTTP_UNAUTHORIZED = 403
  HTTP_ERROR = 400
  HTTP_INTERNAL_SERVER_ERROR = 500


class GenericMessages:
  INVALID_SECRET = 'Invalid secret'
  EXCEPTION = 'Except: '
  NOT_TOKEN = 'Authentication token is not available, please request to get one'
  EXPIRED_TOKEN = 'Token expired'
  INVALID_TOKEN = 'Invalid token'
  ERROR_GENERATE_TOKEN = 'Error in generating token'
  USER_NOT_FOUND = 'User not found'
  ROLE_NOT_FOUND = 'Role not found'
  RULE_NOT_FOUND = 'Rule not found'


class FileManagerMappers:
  TEMPLATE_EMAIL_FOLDER = 'templates/mails'
  TEMPLATE_EMAIL_FORGOT_NAME = 'validate'
  TEMPLATE_EMAIL_FORGOT_SUBJECT = 'Hoplias - Access validation'
  TEMPLATE_EMAIL_INVITE_NAME = 'invite'
  TEMPLATE_EMAIL_INVITE_SUBJECT = 'Hoplias - Hoplias invitation'


class RoutePathApiAiWithProxy:
  CATEGORY_SUGESTION = "category-sugestion"

class RoutePathApiAi:
  CATEGORY_SUGESTION = "/category-sugestion"

class RoutePathChatbotToken:
  CATEGORY_SUGESTION = "/auth-chatbot"

class RoutePathWithProxy:
  SEGMENTATION = "segmentation/json"
  IDEOGRAM = "ideogram/ideogram"
  CLASSIFICATION_CENTROMERE = "classification/centromere"
  CLASSIFICATION = "classification/classification"
  PRECLASSIFICATION = "classification/preclassification"
  CONVERT_TO_JPG = "segmentation/convert-image"

class RoutePathGateway:
  SEGMENTATION = "/segmentation/json"
  IDEOGRAM = "/ideogram/ideogram"
  CLASSIFICATION_CENTROMERE = "/classification/centromere"
  CLASSIFICATION = "/classification/classification"
  PRECLASSIFICATION = "/classification/preclassification"
  CLASSIFICATION_CENTROMERE_QUEUE = "/classification/enqueue-centromere"
  PRECLASSIFICATION_QUEUE = "/classification/enqueue-preclassification"
  CONVERT_TO_JPG = "/segmentation/convert-image"

class Bucket:
  BUCKET = 'hoplias-users-chromosomes'
  CROPED_RGB_FOLDERS = '/chromosomes/rgb/'
  CROPED_GRAY_FOLDERS = '/chromosomes/gray/'
  FOLDER_BASE = 'chromosomes'

class FilterType:
  REPORT = 'report'
