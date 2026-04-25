from enum import Enum

__all__ = ["DocumentState"]


class DocumentState(str, Enum):
    NEW = "new"
    PREPROCESSING = "preprocessing"
    IDENTIFICATION = "identification"
    DATA_EXTRACTION = "dataExtraction"
    VALIDATION = "validation"
    IN_REVIEW = "inReview"
    FAILED = "failed"
    COMPLETED = "completed"
    UNIFICATION = "unification"
    IMAGE_PREPROCESSING = "imagePreprocessing"
    PARSING = "parsing"
    VERSION_IDENTIFICATION = "versionIdentification"
    POSTPROCESSING = "postprocessing"
    NEEDS_REVIEW = "needsReview"
    EXPORTING = "exporting"
    EXPORTED = "exported"
    EXCEPTIONAL_QUEUE = "exceptionalQueue"
    POSTPONED = "postponed"
