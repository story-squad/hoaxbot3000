from StSqLLMWrapper.llmwrapper import LLMRequest, LLMResponse


class StorySquadBotResponseFinalizer:
    def __init__(self, name: str = "unnamed bot finalizer"):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __call__(self, request: LLMRequest, response: LLMResponse):
        return self.apply(request, response)

    def apply(self, request: LLMRequest, response: LLMResponse):
        raise NotImplementedError("StorySquadBotResponseFinalizer.apply() not implemented")

class WordHoaxBotResponseFinalizer(StorySquadBotResponseFinalizer):
    def apply(self, request: LLMRequest, response: LLMResponse):

        if request:
            if request.documents:
                request.documents_processed_data["moderation_processor"] = \
                    [(self.get_moderation(doc), doc) for doc in request.documents]

            if request.prompt:
                request.prompt_processed_data["moderation_processor"] = \
                    (self.get_moderation(request.prompt), request.prompt)

            if request.context:
                request.context_processed_data["moderation_processor"] = \
                    (self.get_moderation(request.context), request.context)
        if response:
            if response.text:
                if type(response.text) is str:
                    response.text_processed_data["moderation_processor"] = \
                        (self.get_moderation(response.text), response.text)

                if type(response.text) is list:
                    response.text_processed_data["moderation_processor"] = \
                        [(self.get_moderation(comp.text), comp) for comp in response.text]

