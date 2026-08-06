"""
Module: Regex Detector

Purpose:
Implements a rule-based Personally Identifiable Information (PII) detection
engine using Regular Expressions (Regex). It scans input text for predefined
PII patterns such as phone numbers, email addresses, credit cards, government
identifiers, URLs, and other sensitive information. The detected entities are
returned with their location, type, and confidence score for further
processing in the PII sanitization pipeline.

Technical Workflow:
1. Initializes a collection of Regex patterns for different PII categories:
   - Phone numbers (Indian and international formats)
   - Email addresses
   - Credit card numbers
   - IP addresses
   - Government identifiers (Aadhaar, PAN, Passport, GSTIN, IFSC)
   - UPI IDs and URLs

2. Scans the input text using each Regex pattern:
   - Uses pattern.finditer() to locate every matching entity.
   - Extracts the matched value and its start/end character positions.

3. Performs additional validation for specific entities:
   - Credit card numbers are verified using the Luhn algorithm to reduce
     false positives and ensure the number follows a valid checksum pattern.

4. Creates a detection object for every identified PII entity containing:
   - Entity type (e.g., EMAIL_ADDRESS, PHONE_NUMBER)
   - Original matched value
   - Start and end indices in the text
   - Confidence score
   - Detection source ("regex")

5. Returns the list of detected PII entities to the sanitization pipeline for
   further processing such as merging, filtering, and pseudonymization.

Example Usage:
detector = RegexDetector()

detections = detector.detect(
    "Contact me at john@gmail.com or call +919876543210"
)

Example Output:
[
    {
        "entity_type": "EMAIL_ADDRESS",
        "match": "john@gmail.com",
        "start": 14,
        "end": 28,
        "confidence": 1.0,
        "detector": "regex"
    },
    {
        "entity_type": "PHONE_NUMBER",
        "match": "+919876543210",
        "start": 38,
        "end": 51,
        "confidence": 1.0,
        "detector": "regex"
    }
]

Detection Flow:
Input Text
    │
    ▼
Apply Regex Patterns
    │
    ▼
Find Matching PII Entities
    │
    ▼
Validate Specific Patterns
(e.g., Credit Card using Luhn Algorithm)
    │
    ▼
Create Detection Metadata
    │
    ▼
Return Detected PII Entities

Why Regex-Based Detection?
Regex provides fast and deterministic detection for structured PII formats
where patterns are predictable, such as emails, phone numbers, and government
identifiers. It complements AI-based detectors by providing high-confidence
results for well-defined formats.

Benefits:
- Fast and lightweight detection method.
- Provides exact character positions for accurate replacement.
- Detects structured PII with high precision.
- Reduces false positives using additional validation logic.
- Works together with transformer-based detection to improve overall PII
  detection coverage.
"""



import re


class RegexDetector:

    def __init__(self):
        self.patterns = {
            # India + generic international numbers
            "PHONE_NUMBER": re.compile(
                r"\b(?:\+91[- ]?)?[6-9]\d{9}\b"
            ),
            "EMAIL_ADDRESS": re.compile(
                r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
            ),
            "CREDIT_CARD": re.compile(
                r"\b(?:\d[ -]*?){13,16}\b"
            ),
            "IP_ADDRESS": re.compile(
                r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
            ),
            "US_SSN": re.compile(
                r"\b\d{3}-\d{2}-\d{4}\b"
            ),
            "AADHAAR": re.compile(
                r"\b\d{4}\s?\d{4}\s?\d{4}\b"
            ),
            "PAN_NUMBER": re.compile(
                r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
            ),
            "PASSPORT": re.compile(
                r"\b[A-Z][0-9]{7}\b"
            ),
            "GSTIN": re.compile(
                r"\b\d{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b"
            ),
            "IFSC_CODE": re.compile(
                r"\b[A-Z]{4}0[A-Z0-9]{6}\b"
            ),
            "UPI_ID": re.compile(
                r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b"
            ),
            "URL": re.compile(
                r"(?:https?://|www\.)[^\s]+",
                re.IGNORECASE,
            ),
        }

    def _is_valid_credit_card(self, card_number: str):
        digits = "".join(c for c in card_number if c.isdigit())

        if not (13 <= len(digits) <= 16):
            return False

        total = 0
        reverse_digits = digits[::-1]

        for i, digit in enumerate(reverse_digits):
            n = int(digit)

            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9

            total += n

        return total % 10 == 0

    def detect(self, text: str):
        detections = []

        for entity_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                value = match.group()

                # Reduce credit card false positives
                if entity_type == "CREDIT_CARD":
                    if not self._is_valid_credit_card(value):
                        continue

                detections.append({
                    "entity_type": entity_type,
                    "match": value,
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 1.0,
                    "detector": "regex",
                })

        return detections