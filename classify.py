def classify_transaction(receiver, categories=None):
    if categories is None:
        categories = {
            "food": [
                "zomato", "eatclub", "swiggy", "food", "restaurant",
                "domino", "pizza", "mcdonald", "kfc"
            ],
            "bills": [
                "bill", "electricity", "gas", "recharge", "academy",
                "education", "insurance", "loan", "water", "broadband", "wifi"
            ],
            "leisure": [
                "movie", "theatre", "ticket", "pvr", "game", "bowling",
                "club", "netflix", "prime", "hotstar", "spotify"
            ],
            "travel": [
                "uber", "ola", "irctc", "makemytrip", "goibibo", "flight",
                "booking", "airbnb", "hotel"
            ],
            "shopping": [
                "amazon", "flipkart", "myntra", "snapdeal", "nykaa",
                "tatacliq", "store"
            ],
            "merchant": [
                "private limited", "enterprise", "enterprises", "merchant", "biz"
            ]
        }

    receiver_lower = receiver.lower()
    for category, keywords in categories.items():
        if any(k in receiver_lower for k in keywords):
            return category
    return "other"
