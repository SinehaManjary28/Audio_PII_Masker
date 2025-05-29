# from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
# from presidio_anonymizer import AnonymizerEngine
# from geotext import GeoText
# import re

# # --- Custom Recognizers ---
# aadhaar_pattern = Pattern("Aadhaar", r"\b\d{4}[- ]?\d{4}[- ]?\d{4}\b", 0.9)
# aadhaar_recognizer = PatternRecognizer(supported_entity="AADHAAR_NUMBER", patterns=[aadhaar_pattern])

# pan_pattern = Pattern("PAN", r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", 0.9)
# pan_recognizer = PatternRecognizer(supported_entity="PAN_NUMBER", patterns=[pan_pattern])

# passport_pattern = Pattern("Passport", r"\b[A-Z]{1}[0-9]{7}\b", 0.9)
# passport_recognizer = PatternRecognizer(supported_entity="PASSPORT_NUMBER", patterns=[passport_pattern])

# ssn_pattern = Pattern("SSN", r"\b\d{3}-\d{2}-\d{4}\b", 0.9)
# ssn_recognizer = PatternRecognizer(supported_entity="US_SSN", patterns=[ssn_pattern])

# emirates_pattern = Pattern("Emirates ID", r"\b784-\d{4}-\d{7}-\d\b", 0.9)
# emirates_recognizer = PatternRecognizer(supported_entity="EMIRATES_ID", patterns=[emirates_pattern])

# # --- Initialize engines ---
# analyzer = AnalyzerEngine()
# anonymizer = AnonymizerEngine()

# # --- Register custom recognizers ---
# analyzer.registry.add_recognizer(aadhaar_recognizer)
# analyzer.registry.add_recognizer(pan_recognizer)
# analyzer.registry.add_recognizer(passport_recognizer)
# analyzer.registry.add_recognizer(ssn_recognizer)
# analyzer.registry.add_recognizer(emirates_recognizer)

# # --- Masking Function ---
# def mask_pii(text):
#     # Step 1: Analyze with Presidio
#     results = analyzer.analyze(text=text, entities=None, language="en")
    
#     # Step 2: GeoText detection for cities and countries
#     places = GeoText(text)

#     for city in places.cities:
#         for match in re.finditer(r'\b{}\b'.format(re.escape(city)), text):
#             results.append(RecognizerResult(
#                 entity_type="LOCATION",
#                 start=match.start(),
#                 end=match.end(),
#                 score=0.95
#             ))

#     for country in places.countries:
#         for match in re.finditer(r'\b{}\b'.format(re.escape(country)), text):
#             results.append(RecognizerResult(
#                 entity_type="LOCATION",
#                 start=match.start(),
#                 end=match.end(),
#                 score=0.95
#             ))

#     # Step 3: Anonymize
#     anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
#     return anonymized_text.text

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from geotext import GeoText
import re
import spacy

# Load SpaCy English model
nlp = spacy.load("en_core_web_sm")

# Initialize analyzer and anonymizer
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Custom regex recognizers for India and common PII patterns
aadhaar_pattern = Pattern("Aadhaar", r"\b\d{4}[- ]?\d{4}[- ]?\d{4}\b", 0.9)
aadhaar_recognizer = PatternRecognizer(supported_entity="AADHAAR_NUMBER", patterns=[aadhaar_pattern])

pan_pattern = Pattern("PAN", r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", 0.9)
pan_recognizer = PatternRecognizer(supported_entity="PAN_NUMBER", patterns=[pan_pattern])

passport_pattern = Pattern("Passport", r"\b[A-Z]{1}[0-9]{7}\b", 0.9)
passport_recognizer = PatternRecognizer(supported_entity="PASSPORT_NUMBER", patterns=[passport_pattern])

ssn_pattern = Pattern("SSN", r"\b\d{3}-\d{2}-\d{4}\b", 0.9)
ssn_recognizer = PatternRecognizer(supported_entity="US_SSN", patterns=[ssn_pattern])

emirates_pattern = Pattern("Emirates ID", r"\b784-\d{4}-\d{7}-\d\b", 0.9)
emirates_recognizer = PatternRecognizer(supported_entity="EMIRATES_ID", patterns=[emirates_pattern])

pin_pattern = Pattern("Indian Pincode", r"\b\d{6}\b", 0.85)
pin_recognizer = PatternRecognizer(supported_entity="IN_PINCODE", patterns=[pin_pattern])

# Register custom recognizers
analyzer.registry.add_recognizer(aadhaar_recognizer)
analyzer.registry.add_recognizer(pan_recognizer)
analyzer.registry.add_recognizer(passport_recognizer)
analyzer.registry.add_recognizer(ssn_recognizer)
analyzer.registry.add_recognizer(emirates_recognizer)
analyzer.registry.add_recognizer(pin_recognizer)

def get_geo_entities(text):
    places = GeoText(text)
    results = []
    for city in places.cities:
        for match in re.finditer(re.escape(city), text, re.IGNORECASE):
            results.append(RecognizerResult(entity_type="LOCATION", start=match.start(), end=match.end(), score=0.85))
    for country in places.countries:
        for match in re.finditer(re.escape(country), text, re.IGNORECASE):
            results.append(RecognizerResult(entity_type="LOCATION", start=match.start(), end=match.end(), score=0.85))
    return results

def get_spacy_entities(text):
    doc = nlp(text)
    results = []
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            results.append(RecognizerResult(entity_type="LOCATION", start=ent.start_char, end=ent.end_char, score=0.85))
    return results

def mask_pii(text):
    presidio_results = analyzer.analyze(text=text, entities=None, language="en")
    geo_results = get_geo_entities(text)
    spacy_results = get_spacy_entities(text)

    all_results = presidio_results + geo_results + spacy_results

    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=all_results)
    return anonymized_text.text
