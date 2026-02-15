def trim(text, max_chars=3000):
    """
    Safely trim large text to prevent context overflow.
    """
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    return text[-max_chars:]


def safe_get(state_dict, key, default=""):
    """
    Safely extract key from state dictionary.
    Prevents KeyError and NoneType issues.
    """
    if not isinstance(state_dict, dict):
        return default
    return state_dict.get(key, default)


def safe_memory_extract(memory_result, max_chars=1000):
    """
    Extract recommendation safely from Chroma memory query.
    Works whether result is dict or unexpected format.
    """
    if not memory_result:
        return ""

    output = ""

    # Standard Chroma structure
    if isinstance(memory_result, dict) and "metadatas" in memory_result:
        metadata_list = memory_result["metadatas"][0]

        for rec in metadata_list:
            if isinstance(rec, dict) and "recommendation" in rec:
                output += rec["recommendation"] + "\n\n"

    # Fallback: if list of strings
    elif isinstance(memory_result, list):
        for rec in memory_result:
            if isinstance(rec, dict) and "recommendation" in rec:
                output += rec["recommendation"] + "\n\n"
            elif isinstance(rec, str):
                output += rec + "\n\n"

    return trim(output, max_chars)
