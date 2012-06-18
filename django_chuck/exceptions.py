class TemplateError(Exception):
    """
    General template error
    """
    __msg = ""

    def __init__(self, what):
        super(TemplateError, self).__init__()
        self.__msg = what

    def __str__(self):
        return str(self.__msg)


class ModuleError(Exception):
    """
    General module error
    """
    __msg = ""

    def __init__(self, what):
        super(ModuleError, self).__init__()
        self.__msg = what

    def __str__(self):
        return str(self.__msg)
