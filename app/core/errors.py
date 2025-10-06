class AppError(Exception):
    pass


class UnknownError(AppError):
    pass


class ExternalServiceError(AppError):
    pass


class BlobError(ExternalServiceError):
    pass


class ConnectionError(AppError):
    pass
