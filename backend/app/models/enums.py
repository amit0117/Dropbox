
from enum import Enum


class FileStatus(str, Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    FAILED = "failed"


class AllowedMimeType(str, Enum):   
    TEXT_PLAIN = "text/plain"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    APPLICATION_JSON = "application/json"
    APPLICATION_PDF = "application/pdf"


class SupabaseOperatorType(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    LIKE = "like"
    ILIKE = "ilike"
    IN = "in_"
    IS = "is_"
    IS_NOT_NULL = "is_not_null"
