from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, code: str, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(
            status_code=status_code,
            detail={"error": {"code": code, "message": message}},
        )


class NotFoundError(AppError):
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            code=f"{resource.upper()}_NOT_FOUND",
            message=f"{resource} not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ForbiddenError(AppError):
    def __init__(self):
        super().__init__(
            code="FORBIDDEN",
            message="You do not have permission to access this resource.",
            status_code=status.HTTP_403_FORBIDDEN,
        )
