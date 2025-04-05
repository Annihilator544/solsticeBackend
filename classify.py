def classify_transaction(receiver):
    receiver_lower = receiver.lower()
    if any(x in receiver_lower for x in ["zomato", "eatclub", "swiggy", "food", "restaurant"]):
        return "food"
    if any(x in receiver_lower for x in ["academy", "education", "bill", "electricity", "gas", "recharge"]):
        return "bills"
    if any(x in receiver_lower for x in ["movie", "theatre", "ticket", "pvr", "game", "bowling", "club"]):
        return "leisure"
    if any(x in receiver_lower for x in ["private limited", "enterprise", "enterprises"]):
        return "merchant"
    return "other"