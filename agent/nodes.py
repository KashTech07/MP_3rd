

from database.database import get_district_data, get_districts
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from database.database import (
    get_district_data,
    get_districts,
    get_state_data
)
load_dotenv()

# ============================================================
# QUERY ANALYSIS SCHEMA
# ============================================================

class QueryAnalysis(BaseModel):

    districts: list[str] = Field(
        description="Specific districts mentioned in the user query"
    )

    states: list[str] = Field(
        description="States mentioned in the user query"
    )

    intent: list[str] = Field(
        description="""
Main purpose of the query.

Possible values:
overall_status,
extraction,
recharge,
rainfall,
groundwater_level,
comparison,
ranking,
prediction,
recommendation
"""
    )

    metrics: list[str] = Field(
        description="""
Groundwater metrics required to answer the question.

Possible values:
rainfall,
recharge,
extraction,
groundwater_level,
category
"""
    )

    comparison_tool: bool = Field(
        description="Whether the user wants a comparison"
    )

    ranking_tool: bool = Field(
        description="Whether the user wants highest, lowest, maximum, minimum, top or bottom ranking"
    )

    prediction_tool: bool = Field(
        description="Whether prediction is required"
    )

    all_districts: bool = Field(
        description="Whether the user wants all districts of a state or all available districts"
    )

    time_period: str = Field(
        description="Requested time period such as current, historical, or future"
    )

    needs_recommendation: bool = Field(
        description="Whether recommendations are requested"
    )


# ============================================================
# LLM INTEGRATION
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

query_analyzer = llm.with_structured_output(QueryAnalysis)


# ============================================================
# NODE 1: UNDERSTAND QUERY
# ============================================================

def understand_query(state):

    query = state["query"]

    # Get available districts
    districts = get_districts()

    prompt = f"""
You are the query analyzer for a Groundwater AI Analyst.

Available districts in the database:

{districts}

Analyze the user's query.

Identify:

1. Specific district(s) mentioned.
2. State(s) mentioned.
3. Main intent.
4. Required groundwater metrics.
5. Whether comparison is required.
6. Whether ranking is required.
7. Whether all districts are requested.
8. Requested time period.
9. Whether prediction is required.
10. Whether recommendations are required.

IMPORTANT RULES:

- Only select districts that exist in the database.
- Never invent district names.
- If a district is not available, do not substitute another district.
- If no available district is mentioned, return an empty districts list.
- If a state is mentioned, identify the state.
- If the user asks for all districts of a state,
  set all_districts=True.
- If the user asks for comparison,
  set comparison_tool=True.
- If the user asks for highest, lowest, maximum,
  minimum, top or bottom, set ranking_tool=True.
- If the user asks what should be done,
  set needs_recommendation=True.
- If the user asks about future groundwater conditions,
  set prediction_tool=True.

Intent possibilities:

overall_status
extraction
recharge
rainfall
groundwater_level
comparison
ranking
prediction
recommendation

User query:

{query}
"""

    result = query_analyzer.invoke(prompt)

    return {
        "districts": result.districts,
        "states": result.states,
        "intent": result.intent,
        "metrics": result.metrics,
        "comparison": result.comparison_tool,
        "ranking": result.ranking_tool,
        "all_districts": result.all_districts,
        "time_period": result.time_period,
        "needs_prediction": result.prediction_tool,
        "needs_recommendation": result.needs_recommendation
    }


# ============================================================
# NODE 2: RETRIEVE DATA
# ============================================================

def retrieve_data(state):

    districts = state.get("districts", [])
    states = state.get("states", [])
    all_districts = state.get("all_districts", False)

    all_data = []

    # ==========================================
    # STATE LEVEL QUERY
    # ==========================================

    if states and all_districts:

        for state_name in states:

            state_data = get_state_data(state_name)

            all_data.extend(state_data)

    # ==========================================
    # DISTRICT LEVEL QUERY
    # ==========================================

    else:

        for district in districts:

            data = get_district_data(district)

            if data is not None:
                all_data.append(data)

    # ==========================================
    # NO DATA
    # ==========================================

    if not all_data:

        return {
            "data": [],
            "response": (
                "I could not find groundwater data "
                "for the requested location."
            )
        }

    return {
        "data": all_data
    }


# ============================================================
# NODE 3: ANALYZE DATA
# ============================================================

def analyze_data(state):

    data = state.get("data", [])

    if not data:
        return {
            "analysis": []
        }

    analysis = []

    for district_data in data:

        recharge = district_data["recharge_mcm"]
        extraction = district_data["extraction_mcm"]

        # Avoid division by zero
        if recharge > 0:
            extraction_ratio = (extraction / recharge) * 100
        else:
            extraction_ratio = 0

        result = {
            "district": district_data["district"],
            "state": district_data["state"],
            "category": district_data["category"],
            "rainfall_mm": district_data["rainfall_mm"],
            "recharge_mcm": recharge,
            "extraction_mcm": extraction,
            "groundwater_level_m": district_data["groundwater_level_m"],
            "extraction_ratio": round(extraction_ratio, 2)
        }

        analysis.append(result)

    return {
        "analysis": analysis
    }


# ============================================================
# NODE 4: GENERATE RESPONSE
# ============================================================

# def generate_response(state):

#     data = state.get("data", [])
#     analysis = state.get("analysis", [])

#     intents = state.get("intent", [])
#     comparison = state.get("comparison", False)
#     needs_recommendation = state.get("needs_recommendation", False)
#     needs_prediction = state.get("needs_prediction", False)

#     # ==========================================
#     # NO DATA
#     # ==========================================

#     if not data:

#         existing_response = state.get("response")

#         if existing_response:
#             return {
#                 "response": existing_response
#             }

#         return {
#             "response": "I could not find groundwater data for the requested district."
#         }

#     if not analysis:

#         return {
#             "response": "I could not generate an analysis from the available data."
#         }

#     # ==========================================
#     # COMPARISON
#     # ==========================================

#     if comparison or "comparison" in intents:

#         response = "Groundwater Comparison\n\n"

#         for item in analysis:

#             response += (
#                 f"{item['district']}:\n"
#                 f"- Category: {item['category']}\n"
#                 f"- Rainfall: {item['rainfall_mm']} mm\n"
#                 f"- Recharge: {item['recharge_mcm']} MCM\n"
#                 f"- Extraction: {item['extraction_mcm']} MCM\n"
#                 f"- Groundwater Level: {item['groundwater_level_m']} m\n"
#                 f"- Extraction-to-Recharge Ratio: "
#                 f"{item['extraction_ratio']}%\n\n"
#             )

#         # Find highest extraction pressure
#         highest_extraction = max(
#             analysis,
#             key=lambda x: x["extraction_ratio"]
#         )

#         # Find highest recharge
#         highest_recharge = max(
#             analysis,
#             key=lambda x: x["recharge_mcm"]
#         )

#         # Find lowest groundwater level
#         lowest_level = min(
#             analysis,
#             key=lambda x: x["groundwater_level_m"]
#         )

#         response += "Key Findings:\n"

#         response += (
#             f"- Highest extraction pressure: "
#             f"{highest_extraction['district']} "
#             f"({highest_extraction['extraction_ratio']}%)\n"
#         )

#         response += (
#             f"- Highest recharge: "
#             f"{highest_recharge['district']} "
#             f"({highest_recharge['recharge_mcm']} MCM)\n"
#         )

#         response += (
#             f"- Lowest groundwater level: "
#             f"{lowest_level['district']} "
#             f"({lowest_level['groundwater_level_m']} m)"
#         )

#         return {
#             "response": response
#         }

#     # ==========================================
#     # RECOMMENDATION
#     # ==========================================

#     if needs_recommendation or "recommendation" in intents:

#         responses = []

#         for item in analysis:

#             ratio = item["extraction_ratio"]

#             if ratio > 100:

#                 recommendation = (
#                     "Groundwater extraction is higher than recharge. "
#                     "Extraction should be reduced and artificial recharge "
#                     "measures should be prioritized."
#                 )

#             elif ratio > 90:

#                 recommendation = (
#                     "The district is under high groundwater stress. "
#                     "Groundwater extraction should be monitored closely "
#                     "and recharge measures should be increased."
#                 )

#             elif ratio > 70:

#                 recommendation = (
#                     "The district requires careful monitoring. "
#                     "Water conservation and groundwater recharge "
#                     "measures should be encouraged."
#                 )

#             else:

#                 recommendation = (
#                     "The groundwater situation is relatively stable. "
#                     "Sustainable extraction and conservation practices "
#                     "should continue."
#                 )

#             responses.append(
#                 f"{item['district']}:\n"
#                 f"{recommendation}"
#             )

#         return {
#             "response": "\n\n".join(responses)
#         }

#     # ==========================================
#     # PREDICTION
#     # ==========================================

#     if needs_prediction or "prediction" in intents:

#         return {
#             "response": (
#                 "Prediction cannot be reliably performed with the "
#                 "current dataset because it contains only a single "
#                 "data point for each district. Historical groundwater "
#                 "data across multiple years would be required for "
#                 "forecasting."
#             )
#         }

#     # ==========================================
#     # EXTRACTION
#     # ==========================================

#     if "extraction" in intents:

#         responses = []

#         for item in analysis:

#             responses.append(
#                 f"{item['district']} has groundwater extraction of "
#                 f"{item['extraction_mcm']} MCM. "
#                 f"The extraction-to-recharge ratio is "
#                 f"{item['extraction_ratio']}%."
#             )

#         return {
#             "response": "\n".join(responses)
#         }

#     # ==========================================
#     # RECHARGE
#     # ==========================================

#     if "recharge" in intents:

#         responses = []

#         for item in analysis:

#             responses.append(
#                 f"{item['district']} has groundwater recharge of "
#                 f"{item['recharge_mcm']} MCM."
#             )

#         return {
#             "response": "\n".join(responses)
#         }

#     # ==========================================
#     # RAINFALL
#     # ==========================================

#     if "rainfall" in intents:

#         responses = []

#         for item in analysis:

#             responses.append(
#                 f"{item['district']} has rainfall of "
#                 f"{item['rainfall_mm']} mm."
#             )

#         return {
#             "response": "\n".join(responses)
#         }

#     # ==========================================
#     # GROUNDWATER LEVEL
#     # ==========================================

#     if "groundwater_level" in intents:

#         responses = []

#         for item in analysis:

#             responses.append(
#                 f"{item['district']} has a groundwater level of "
#                 f"{item['groundwater_level_m']} m."
#             )

#         return {
#             "response": "\n".join(responses)
#         }

#     # ==========================================
#     # OVERALL STATUS
#     # ==========================================

#     if "overall_status" in intents:

#         responses = []

#         for item in analysis:

#             responses.append(
#                 f"Groundwater Situation — "
#                 f"{item['district']}, {item['state']}\n"
#                 f"- Category: {item['category']}\n"
#                 f"- Rainfall: {item['rainfall_mm']} mm\n"
#                 f"- Recharge: {item['recharge_mcm']} MCM\n"
#                 f"- Extraction: {item['extraction_mcm']} MCM\n"
#                 f"- Groundwater Level: "
#                 f"{item['groundwater_level_m']} m\n"
#                 f"- Extraction-to-Recharge Ratio: "
#                 f"{item['extraction_ratio']}%"
#             )

#         return {
#             "response": "\n\n".join(responses)
#         }

#     # ==========================================
#     # FALLBACK
#     # ==========================================

#     responses = []

#     for item in analysis:

#         responses.append(
#             f"{item['district']}: "
#             f"{item['category']}, "
#             f"Recharge = {item['recharge_mcm']} MCM, "
#             f"Extraction = {item['extraction_mcm']} MCM"
#         )

#     return {
#         "response": "\n".join(responses)
#     }
def generate_response(state):

    data = state.get("data", [])
    analysis = state.get("analysis", [])

    intents = state.get("intent", [])
    comparison = state.get("comparison", False)
    ranking = state.get("ranking", False)

    needs_recommendation = state.get(
        "needs_recommendation", False
    )

    needs_prediction = state.get(
        "needs_prediction", False
    )

    # ==========================================
    # NO DATA
    # ==========================================

    if not data:

        existing_response = state.get("response")

        if existing_response:
            return {
                "response": existing_response
            }

        return {
            "response": (
                "I could not find groundwater data "
                "for the requested location."
            )
        }

    if not analysis:

        return {
            "response": (
                "I could not generate an analysis "
                "from the available groundwater data."
            )
        }

    # ==========================================
    # RANKING
    # ==========================================

    if ranking or "ranking" in intents:

        query = state.get("query", "").lower()

        # ------------------------------------------
        # EXTRACTION RANKING
        # ------------------------------------------

        if "extraction" in query:

            sorted_data = sorted(
                analysis,
                key=lambda x: x["extraction_mcm"],
                reverse=True
            )

            response = "Groundwater Extraction Ranking\n\n"

            for i, item in enumerate(sorted_data, start=1):

                response += (
                    f"{i}. {item['district']} - "
                    f"{item['extraction_mcm']} MCM\n"
                )

            return {
                "response": response
            }

        # ------------------------------------------
        # RECHARGE RANKING
        # ------------------------------------------

        if "recharge" in query:

            sorted_data = sorted(
                analysis,
                key=lambda x: x["recharge_mcm"],
                reverse=True
            )

            response = "Groundwater Recharge Ranking\n\n"

            for i, item in enumerate(sorted_data, start=1):

                response += (
                    f"{i}. {item['district']} - "
                    f"{item['recharge_mcm']} MCM\n"
                )

            return {
                "response": response
            }

        # ------------------------------------------
        # RAINFALL RANKING
        # ------------------------------------------

        if "rainfall" in query:

            sorted_data = sorted(
                analysis,
                key=lambda x: x["rainfall_mm"],
                reverse=True
            )

            response = "Rainfall Ranking\n\n"

            for i, item in enumerate(sorted_data, start=1):

                response += (
                    f"{i}. {item['district']} - "
                    f"{item['rainfall_mm']} mm\n"
                )

            return {
                "response": response
            }

        # ------------------------------------------
        # GROUNDWATER LEVEL RANKING
        # ------------------------------------------

        if "groundwater level" in query:

            sorted_data = sorted(
                analysis,
                key=lambda x: x["groundwater_level_m"],
                reverse=True
            )

            response = "Groundwater Level Ranking\n\n"

            for i, item in enumerate(sorted_data, start=1):

                response += (
                    f"{i}. {item['district']} - "
                    f"{item['groundwater_level_m']} m\n"
                )

            return {
                "response": response
            }

        # ------------------------------------------
        # DEFAULT: EXTRACTION PRESSURE
        # ------------------------------------------

        sorted_data = sorted(
            analysis,
            key=lambda x: x["extraction_ratio"],
            reverse=True
        )

        response = (
            "Groundwater Stress Ranking\n\n"
        )

        for i, item in enumerate(sorted_data, start=1):

            response += (
                f"{i}. {item['district']} - "
                f"{item['extraction_ratio']}% "
                f"extraction-to-recharge ratio\n"
            )

        return {
            "response": response
        }

    # ==========================================
    # COMPARISON
    # ==========================================

    if comparison or "comparison" in intents:

        response = "Groundwater Comparison\n\n"

        for item in analysis:

            response += (
                f"{item['district']}:\n"
                f"- Category: {item['category']}\n"
                f"- Rainfall: {item['rainfall_mm']} mm\n"
                f"- Recharge: {item['recharge_mcm']} MCM\n"
                f"- Extraction: {item['extraction_mcm']} MCM\n"
                f"- Groundwater Level: "
                f"{item['groundwater_level_m']} m\n"
                f"- Extraction-to-Recharge Ratio: "
                f"{item['extraction_ratio']}%\n\n"
            )

        highest_pressure = max(
            analysis,
            key=lambda x: x["extraction_ratio"]
        )

        highest_recharge = max(
            analysis,
            key=lambda x: x["recharge_mcm"]
        )

        response += "Key Findings:\n"

        response += (
            f"- Highest extraction pressure: "
            f"{highest_pressure['district']} "
            f"({highest_pressure['extraction_ratio']}%)\n"
        )

        response += (
            f"- Highest recharge: "
            f"{highest_recharge['district']} "
            f"({highest_recharge['recharge_mcm']} MCM)"
        )

        return {
            "response": response
        }

    # ==========================================
    # RECOMMENDATION
    # ==========================================

    if (
        needs_recommendation
        or "recommendation" in intents
    ):

        responses = []

        for item in analysis:

            ratio = item["extraction_ratio"]

            if ratio > 100:

                recommendation = (
                    "Extraction exceeds recharge. "
                    "Extraction should be reduced and "
                    "artificial recharge should be prioritized."
                )

            elif ratio > 90:

                recommendation = (
                    "The district is under high groundwater "
                    "stress. Extraction should be monitored "
                    "closely and recharge measures increased."
                )

            elif ratio > 70:

                recommendation = (
                    "The district requires monitoring. "
                    "Water conservation and groundwater "
                    "recharge measures should be encouraged."
                )

            else:

                recommendation = (
                    "The groundwater situation is relatively "
                    "stable. Sustainable extraction and "
                    "conservation should continue."
                )

            responses.append(
                f"{item['district']}:\n"
                f"{recommendation}"
            )

        return {
            "response": "\n\n".join(responses)
        }

    # ==========================================
    # PREDICTION
    # ==========================================

    if (
        needs_prediction
        or "prediction" in intents
    ):

        return {
            "response": (
                "Prediction cannot be reliably performed "
                "with the current dataset because it "
                "contains only a single data point for "
                "each district. Historical year-wise "
                "groundwater data is required for forecasting."
            )
        }

    # ==========================================
    # EXTRACTION
    # ==========================================

    if "extraction" in intents:

        responses = []

        for item in analysis:

            responses.append(
                f"{item['district']} has groundwater "
                f"extraction of {item['extraction_mcm']} MCM. "
                f"The extraction-to-recharge ratio is "
                f"{item['extraction_ratio']}%."
            )

        return {
            "response": "\n".join(responses)
        }

    # ==========================================
    # RECHARGE
    # ==========================================

    if "recharge" in intents:

        responses = []

        for item in analysis:

            responses.append(
                f"{item['district']} has groundwater "
                f"recharge of {item['recharge_mcm']} MCM."
            )

        return {
            "response": "\n".join(responses)
        }

    # ==========================================
    # RAINFALL
    # ==========================================

    if "rainfall" in intents:

        responses = []

        for item in analysis:

            responses.append(
                f"{item['district']} has rainfall of "
                f"{item['rainfall_mm']} mm."
            )

        return {
            "response": "\n".join(responses)
        }

    # ==========================================
    # GROUNDWATER LEVEL
    # ==========================================

    if "groundwater_level" in intents:

        responses = []

        for item in analysis:

            responses.append(
                f"{item['district']} has a groundwater "
                f"level of {item['groundwater_level_m']} m."
            )

        return {
            "response": "\n".join(responses)
        }

    # ==========================================
    # OVERALL STATUS
    # ==========================================

    if "overall_status" in intents:

        responses = []

        for item in analysis:

            responses.append(
                f"Groundwater Situation — "
                f"{item['district']}, {item['state']}\n"
                f"- Category: {item['category']}\n"
                f"- Rainfall: {item['rainfall_mm']} mm\n"
                f"- Recharge: {item['recharge_mcm']} MCM\n"
                f"- Extraction: {item['extraction_mcm']} MCM\n"
                f"- Groundwater Level: "
                f"{item['groundwater_level_m']} m\n"
                f"- Extraction-to-Recharge Ratio: "
                f"{item['extraction_ratio']}%"
            )

        return {
            "response": "\n\n".join(responses)
        }

    # ==========================================
    # FALLBACK
    # ==========================================

    return {
        "response": (
            "I found the groundwater data, but I "
            "could not determine the exact analysis "
            "requested."
        )
    }
