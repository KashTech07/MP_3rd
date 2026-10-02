from typing import TypedDict


class GroundwaterState(TypedDict, total=False):

    # User's original question
    query: str

    # Query understanding
    districts: list[str]
    states: list[str]

    intent: list[str]
    metrics: list[str]

    comparison: bool
    ranking: bool

    all_districts: bool

    time_period: str

    needs_prediction: bool
    needs_recommendation: bool

    # Data retrieved from SQLite
    data: list[dict]

    # Analysis performed by Python
    analysis: list[dict]

    # Final response
    response: str

