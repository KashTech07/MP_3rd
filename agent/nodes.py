from database.database import get_district_data , get_districts


def retrieve_data(state):

    district = state.get("district")

    if not district:
        return {
            "data": {},
            "response": "District was not provided."
        }

    data = get_district_data(district)

    if data is None:
        return {
            "data": {},
            "response": f"No groundwater data found for {district}."
        }

    return {
        "data": data
    }


def analyze_data(state):

    data = state.get("data", {})

    if not data:
        return {
            "analysis": {}
        }

    recharge = data["recharge_mcm"]
    extraction = data["extraction_mcm"]

    extraction_ratio = (extraction / recharge) * 100

    analysis = {
        "extraction_ratio": round(extraction_ratio, 2)
    }

    return {
        "analysis": analysis
    }

def generate_response(state) :
    data = state.get("data" , {})
    analysis = state.get("analysis" , {})

    if not data :
        return {
            "response" : "I could not find groundwater data for the requested district."
        }
    district = data["district"]
    state_name = data["state"]
    category = data["category"]
    rainfall = data["rainfall_mm"]
    extraction = data["extraction_mcm"]
    recharge = data["recharge_mcm"]
    groundwater_level = data["groundwater_level_m"]
    extraction_ratio = analysis["extraction_ratio"]
    response = f"""
Groundwater Analysis for {district} ,{state_name}
Groundwater Category: {category}

Rainfall: {rainfall} mm
Groundwater Recharge: {recharge} MCM
Groundwater Extraction: {extraction} MCM
Groundwater Level: {groundwater_level} m

The groundwater extraction is approximately {extraction_ratio}% of the groundwater recharge.

Based on the available data, {district} is classified as {category}.

"""
    return {
        "response" : response.strip()
    }

def understand_query(state):
    query = state["query"]
    query_lower = query.lower()
    districts = get_districts()
    for d in districts :
        if d.lower() in query_lower:
            return{
                "district" : d 
            }
    return{
        "response" : "I could not identify the district from your query."
    }