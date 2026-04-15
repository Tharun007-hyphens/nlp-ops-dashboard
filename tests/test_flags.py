import pytest
import spacy
from redactor import redactor_text

# Load SpaCy model
nlp = spacy.load("en_core_web_md")

# Helper function to create a doc object
def create_doc(text):
    return nlp(text)

# Test case for Names redaction
def test_redact_names():
    text = "Rohit Sharma is the Hitman of Cricket."
    doc = create_doc(text)
    flags = {'names': True, 'dates': False, 'phones': False, 'address': False, 'concept': None}
    file_stats = {'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0, 'emails': 0, 'concept': 0}
    
    redacted_text = redactor_text(doc, flags, None, file_stats)
    
    # Match the number of redacted characters
    expected_text = "████████████ is the Hitman of Cricket."
    
    assert redacted_text.strip() == expected_text

# Test case for Dates redaction
def test_redact_dates():
    text = "The meeting is scheduled for 10/10/2024."
    doc = create_doc(text)
    flags = {'names': False, 'dates': True, 'phones': False, 'address': False, 'concept': None}
    file_stats = {'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0, 'emails': 0, 'concept': 0}
    
    redacted_text = redactor_text(doc, flags, None, file_stats)
    assert redacted_text.strip() == "The meeting is scheduled for ██████████."
    assert file_stats['dates'] == 1

# Test case for Phones redaction
def test_redact_phones():
    text = "Call me at 4753690872."
    doc = create_doc(text)
    flags = {'names': False, 'dates': False, 'phones': True, 'address': False, 'concept': None}
    file_stats = {'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0, 'emails': 0, 'concept': 0}
    
    redacted_text = redactor_text(doc, flags, None, file_stats)
    assert redacted_text.strip() == "Call me at ██████████."
    assert file_stats['phones'] == 1

# Test case for Addresses redaction
def test_redact_address():
    text = "The address to visit him is 4300 NE Okala St 31567"
    doc = create_doc(text)
    flags = {'names': False, 'dates': False, 'phones': False, 'address': True, 'concept': None}
    file_stats = {'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0, 'emails': 0, 'concept': 0}
    
    redacted_text = redactor_text(doc, flags, None, file_stats)
    assert redacted_text.strip() == "The address to visit him is ██████████████████████"
    assert file_stats['addresses'] == 1

# Test case for Emails redaction
def test_redact_emails():
    text = "Email me at rgs_34@gmail.com."
    doc = create_doc(text)
    flags = {'names': True, 'dates': False, 'phones': False, 'address': False, 'concept': None}
    file_stats = {'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0, 'emails': 0, 'concept': 0}
    
    redacted_text = redactor_text(doc, flags, None, file_stats)
    assert redacted_text.strip() == "Email me at ████████████████."
    assert file_stats['emails'] == 1

# Test case for Custom Concept redaction
def test_redact_concept():
    text = "This is a confidential project."
    doc = create_doc(text)
    flags = {'names': False, 'dates': False, 'phones': False, 'address': False, 'concept': True}
    file_stats = {'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0, 'emails': 0, 'concept': 0}
    
    redacted_text = redactor_text(doc, flags, "confidential", file_stats)
    
    # Match the number of redacted characters
    expected_text = "██████████████████████████████."
    
    assert redacted_text.strip() == expected_text

# Run the tests
if __name__ == "__main__":
    pytest.main()