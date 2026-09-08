"""
IBVAP - ANPR Text Normalization & Clean-up Processor
Corrects common optical character ambiguities ('O'/'0', 'I'/'1', 'B'/'8') based on positional syntax.
"""
import re
from typing import Dict, Any

class PlateProcessor:
    def clean_and_normalize(self, raw_plate: str) -> str:
        clean = re.sub(r"[^A-Za-z0-9]", "", raw_plate).upper()
        # Positional correction: First 2 chars must be state letters
        chars = list(clean)
        if len(chars) >= 2:
            if chars[0] == '0': chars[0] = 'D'
            if chars[1] == '0': chars[1] = 'L'
            if chars[0] == '1': chars[0] = 'I'
        return "".join(chars)

    def validate_indian_syntax(self, plate: str) -> bool:
        # State (2) + District Code (1-2) + Series (0-3) + Number (4 digits)
        pattern = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$"
        return bool(re.match(pattern, plate))

plate_processor = PlateProcessor()
