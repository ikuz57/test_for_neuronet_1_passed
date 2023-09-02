class RecordsNotFoundError(Exception):
    """
    Исключение вызывается, если не все промты и сущности найдены в базе.
    """

    def __init__(self, not_found):
        self.not_found = not_found
        super().__init__(f"Не найдены записи: {not_found}")
