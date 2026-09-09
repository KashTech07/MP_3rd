from typing import TypedDict, Optional


class GroundwaterState(TypedDict , total=False):

    query: str
    state: str
    district: str
    metric: str
    data: dict
    analysis: dict
    response: str