class AppError(Exception):
    pass

class UnknownError(AppError):
    pass

class BlobError(AppError):
    pass