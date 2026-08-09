def build_candidate_query(candidate_information):
    """
    Build a search query from candidate information.
    """

    query_parts = []

    # Add Role
    role = candidate_information.get("role", "").strip()
    if role:
        query_parts.append(role)

    # Add Skills
    skills = candidate_information.get("skills", [])

    if skills:
        query_parts.extend(skills)

    # Remove duplicates while preserving order
    query_parts = list(dict.fromkeys(query_parts))

    return " ".join(query_parts)