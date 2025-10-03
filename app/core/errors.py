class AppError(Exception):
    pass

class UnknownError(AppError):
    pass

class BlobError(AppError):
    pass

class ConnectionError(AppError):
    pass

class ExternalServiceError(AppError):
    pass