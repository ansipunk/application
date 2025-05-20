import pydantic


class RequestError(pydantic.BaseModel):
    detail: str


def gen_responses(responses):
    return {
        status_code: {
            "description": description,
            "model": RequestError,
        }
        for status_code, description in responses.items()
    }
