import re
udm = ['g','kg','l','ml']
QUANTITY_UDM = r'(\d{1,4}(?:,\d{1,2})?)\s(g|kg|ml|l|cl|cc)'
QUANTITY_ONLY =  r'\b(\d{1,2})\b'
PARENTHESIS = r"\s*\([^)]*\)"
def get_quantity_udm(quantity_raw):
    # remove parenthesis if any
    quantity_raw = remove_parentheses(quantity_raw)
    # get quantity and udm
    quantity_udm_match = re.search(QUANTITY_UDM, quantity_raw, re.IGNORECASE)
    if quantity_udm_match:
        quantity = quantity_udm_match.group(1)
        quantity = re.sub(',','.',quantity)
        return [float(quantity), quantity_udm_match.group(2)]
    # get quantity only
    quantity_only_match = re.search(QUANTITY_ONLY, quantity_raw, re.IGNORECASE)
    if quantity_only_match:
        return [float(quantity_only_match.group(1)),None]
    # exceptions
    return [1,'g']

def remove_parentheses(text):
    return re.sub(PARENTHESIS, "", text).strip()