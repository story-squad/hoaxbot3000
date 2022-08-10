class BaseContextProcessor:
    """ parent class for all context processors"""
    supports = -1

    def __init__(self,context_doc:str, name: str = "unnamed context processor"):
        self.name = name
        self.context_doc = context_doc

    def processor(self):
        raise NotImplementedError("processor() must be implemented by a child class")


class V0Processor(BaseContextProcessor):
    supports = 0

    def processor(self, prompt: str):
        return self.context_doc


class V1Processor(BaseContextProcessor):
    supports = 1

    def processor(self, prompt: str):
        return self.context_doc.replace("[CONTEXT_PROMPT_TOKEN]", prompt)


def get_processor(version: int):
    """
    returns a function that processes the context document of a given format version
    """
    # find the correct context processor class
    list_of_processes = [l for l in globals() if "processor" in l.lower()]
    supported = {
        getattr(globals()[l], "supports"): globals()[l]
        for l in list_of_processes if "supports" in dir(globals()[l])}

    loader_class = supported[version]
    # return the function
    return loader_class


def is_context_processor_supported(type_code_int):
    list_of_loaders = [l for l in globals() if "processor" in l]
    supported = [
        getattr(globals()[l], "supports")
        for l in list_of_loaders]
    if type_code_int in supported:
        return True
