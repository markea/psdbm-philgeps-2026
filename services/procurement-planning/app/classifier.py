"""
UNSPSC (United Nations Standard Products and Services Code) Classifier.
Designed as a pluggable module: operates locally via heuristic/dictionary lookup,
with an architectural interface ready for Gemini 2.0 Flash / Vertex AI integration.
"""
from typing import Optional

UNSPSC_DICTIONARY = {
    "paper": "14111507",
    "copy paper": "14111507",
    "multicopy": "14111507",
    "folder": "44122011",
    "envelope": "44121506",
    "pen": "44121704",
    "ballpoint": "44121704",
    "marker": "44121708",
    "stapler": "44121615",
    "staple wire": "44122107",
    "toner": "44103103",
    "ink": "44103103",
    "cartridge": "44103103",
    "flash drive": "43202005",
    "usb": "43202005",
    "alcohol": "53131626",
    "sanitizer": "53131626",
    "disinfectant": "47131805",
    "soap": "53131608"
}

def classify_item_unspsc(description: str, item_code: Optional[str] = None) -> str:
    """
    Classifies a raw item description to its closest UNSPSC code.
    Fallback: '44120000' (Office supplies and accessories).
    """
    desc_clean = description.lower()
    for keyword, unspsc in UNSPSC_DICTIONARY.items():
        if keyword in desc_clean:
            return unspsc
    return "44120000"
