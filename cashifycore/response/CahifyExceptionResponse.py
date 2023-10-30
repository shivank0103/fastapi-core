from cashifycore.response.CashifyBaseResponse import CashifyResponse


class CashifyExceptionResponse(CashifyResponse):
    """
    Cashify Exception Response Class
    """
    message: str
    code: int

    class Config:
        validate_assignment = True
