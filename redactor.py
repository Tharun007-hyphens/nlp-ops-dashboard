import sys
import spacy
import argparse
import re
import glob
import nltk
from pathlib import Path
from nltk.corpus import wordnet

_WORDNET_READY = False


def _ensure_wordnet():
    global _WORDNET_READY
    if _WORDNET_READY:
        return
    try:
        wordnet.synsets("example")
    except LookupError:
        nltk.download("wordnet", quiet=True)
    _WORDNET_READY = True


# Load the SpaCy model
nlp = spacy.load("en_core_web_md")

def redactor_text(doc, flags, concept, file_stats):
    redacted_text = doc.text

    # Redacting addresses using regex for typical address structures
    if flags.get('address', False):
        # Updated pattern to match a broader range of addresses
        address_pattern = r'\b\d{1,5}\s+(?:[A-Za-z]+\s*){1,5}(?:,?\s+Suite\s+\d{1,5})?,?\s*(?:[A-Za-z]+\s*){1,3},?\s*(?:[A-Za-z]{2})\s+\d{5}(?:-\d{4})?\b'
        
        address_matches = re.findall(address_pattern, redacted_text, re.IGNORECASE)
        for match in address_matches:
            redacted_text = redacted_text.replace(match, '█' * len(match))
            file_stats['addresses'] += 1

    # Redacting names using SpaCy entities
    if flags.get('names', False):
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Create a pattern to match the name along with trailing punctuation and spaces
                # Use a lookahead to handle following punctuation (commas, semicolons, etc.)
                name_pattern = r'\b' + re.escape(ent.text) + r'(?=[\s,;.\n]|$)'
                
                # Count occurrences for statistics
                occurrences = len(re.findall(name_pattern, redacted_text))
                
                # Redact each occurrence of the name with trailing punctuation
                redacted_text = re.sub(name_pattern, '█' * len(ent.text), redacted_text)
                file_stats['names'] += occurrences

    # Redacting dates using SpaCy entities and a fallback regex for additional date formats
    if flags.get('dates', False):
        # Using SpaCy to redact dates identified as DATE entities
        for ent in doc.ents:
            if ent.label_ == "DATE":
                occurrences = redacted_text.count(ent.text)
                redacted_text = re.sub(r'\b' + re.escape(ent.text) + r'\b', '█' * len(ent.text), redacted_text)
                file_stats['dates'] += occurrences

        # Fallback regex for capturing additional date formats not recognized by SpaCy
        fallback_date_pattern = re.compile(
            r'\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|'   # Matches MM/DD/YY or MM-DD-YYYY
            r'\d{1,2}\s+(?:st|nd|rd|th)?\s+(?:[A-Za-z]+)\s+\d{2,4}|'  # Matches 9 April 2025 or 9th April 2025
            r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?'  # Matches day names
            r',?\s*\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|'
            r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}|'  # Matches Wednesday, 31 October 2024
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|'
            r'Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{1,2},?\s*\d{4})\b',  # Matches April 9, 2025 or 9 April 2025
            re.IGNORECASE
        )

        # Applying fallback regex to capture and redact any remaining date patterns
        date_matches = fallback_date_pattern.finditer(redacted_text)
        for match in date_matches:
            match_text = match.group()
            redacted_text = redacted_text.replace(match_text, '█' * len(match_text))
            file_stats['dates'] += 1

    # Redact phone numbers (regex for various phone number formats)
    if flags.get('phones', False):
        # Expanded regex pattern to capture various phone number formats
        phone_pattern = r'(\b\d{10}\b|\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b|\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b)'  
        # Matches formats like 1234567890, 123-456-7890, 123.456.7890, (123) 456-7890, or 123 456 7890
        
        phone_matches = re.findall(phone_pattern, redacted_text)
        for match in phone_matches:
            redacted_text = redacted_text.replace(match.strip(), '█' * len(match.strip()))
            file_stats['phones'] += 1


    # Handle names in email addresses
    if flags.get('names', False):
        email_name_pattern = r'([A-Za-z]+(?:\s[A-Za-z]\.)?)\s*<([A-Za-z0-9._%+-]+)@[A-Za-z0-9.-]+\.[A-Za-z]{2,}>'
        email_matches = re.findall(email_name_pattern, redacted_text)
        for name, email in email_matches:
            # Redact the name part in email addresses
            redacted_text = redacted_text.replace(name, '█' * len(name))
            file_stats['names'] += 1  # Increment count for each name found in emails
    
    # Redact the entire email address
    if flags.get('names', False) or flags.get('emails', False):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        email_matches = re.findall(email_pattern, redacted_text)
        for match in email_matches:
            redacted_text = redacted_text.replace(match, '█' * len(match))
            file_stats['emails'] += 1

    # Redact whole sentences if the concept or its synonyms are found
    if concept:
        redacted_text = redact_concept_sentences(redacted_text, concept, file_stats)
    return redacted_text if redacted_text else ""  # Ensure the function always returns a string

def redact_concept_sentences(redacted_text, concept, file_stats):
    _ensure_wordnet()
    # Get synonyms and related terms for the concept
    synonyms = set()
    for syn in wordnet.synsets(concept):
        # Add synonyms
        synonyms.update(lemma.name().lower() for lemma in syn.lemmas())
        
        # Include broader terms (hypernyms) and specific terms (hyponyms)
        for hypernym in syn.hypernyms():
            synonyms.update(lemma.name().lower() for lemma in hypernym.lemmas())
        for hyponym in syn.hyponyms():
            synonyms.update(lemma.name().lower() for lemma in hyponym.lemmas())
        
        # Add derivationally related forms (captures words like "lodging" related to "house")
        for lemma in syn.lemmas():
            for related_lemma in lemma.derivationally_related_forms():
                synonyms.add(related_lemma.name().lower())
                
    # Add the concept itself to ensure it's included
    synonyms.add(concept.lower())

    # Create a pattern to match any of the synonyms within sentences
    concept_pattern = re.compile(r'\b(' + '|'.join(re.escape(syn) for syn in synonyms) + r')\b', re.IGNORECASE)

    # Split text into sentences
    sentences = re.findall(r'[^.!?]*[.!?]', redacted_text)
    for sentence in sentences:
        # If the sentence contains any of the concept-related words, redact the sentence content only
        if concept_pattern.search(sentence):
            # Preserve punctuation at the end of the sentence
            punctuation = sentence[-1] if sentence[-1] in ".!?" else ""
            redacted_sentence = '█' * (len(sentence) - len(punctuation)) + punctuation
            redacted_text = redacted_text.replace(sentence, redacted_sentence)
            file_stats['concept'] += 1

    return redacted_text

def read_files(input_pattern, output_dir, flags, concept):
    stats = {}
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    files = glob.glob(input_pattern)
    for file_path in files:
        file_stats = {'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0, 'emails': 0, 'concept': 0}
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        doc = nlp(text)
        redacted_text = redactor_text(doc, flags, concept, file_stats)
        output_file_path = Path(output_dir) / f"{Path(file_path).stem}.censored"
        with open(output_file_path, 'w', encoding='utf-8') as censored_file:
            censored_file.write(redacted_text)
        stats[file_path] = {'length': len(redacted_text), 'stats': file_stats}
    return stats


def redact_string(text, flags, concept=None):
    """Run redaction on a single string; returns (redacted_text, file_stats dict)."""
    file_stats = {'names': 0, 'dates': 0, 'phones': 0, 'addresses': 0, 'emails': 0, 'concept': 0}
    doc = nlp(text or "")
    redacted_text = redactor_text(doc, flags, concept, file_stats)
    return redacted_text, file_stats


def print_stats(stats, output):
    for file, data in stats.items():
        if isinstance(data, dict):
            stat_str = (
                f"File: {file}, \n"
                f"Length: {data['length']}, \n"
                f"Names: {data['stats']['names']}, \n"
                f"Dates: {data['stats']['dates']}, \n"
                f"Phones: {data['stats']['phones']}, \n"
                f"Addresses: {data['stats']['addresses']}, \n"
                f"Emails: {data['stats']['emails']}, \n"
                f"Concept: {data['stats']['concept']}"
            )
            print(stat_str, file=output, end="")
        else:
            print(f"Invalid data for file {file}", file=output, end="")

def main():
    parser = argparse.ArgumentParser(description="Censor sensitive information from text files.")
    parser.add_argument("--input", type=str, required=True, help="Glob pattern for input files")
    parser.add_argument("--output", type=str, required=True, help="Output directory for censored files")
    parser.add_argument("--names", action='store_true', help="Flag to censor names")
    parser.add_argument("--dates", action='store_true', help="Flag to censor dates")
    parser.add_argument("--phones", action='store_true', help="Flag to censor phone numbers")
    parser.add_argument("--emails", action='store_true', help="Flag to censor Gmail usernames")
    parser.add_argument("--address", action='store_true', help="Flag to censor addresses")
    parser.add_argument("--concept", type=str, help="Specific concept to censor")
    parser.add_argument("--stats", type=str, help="Output stats to stderr, stdout, or a file path")
    args = parser.parse_args()

    flags = {
        'names': args.names,
        'dates': args.dates,
        'phones': args.phones,
        'address': args.address,
        'emails': args.emails,
        'concept': args.concept
    }

    stats = read_files(args.input, args.output, flags, args.concept)

    if args.stats == 'stderr':
        print_stats(stats, sys.stderr)
    elif args.stats == 'stdout':
        print_stats(stats, sys.stdout)
    else:
        stats_file = Path(args.output) / f"{Path(args.input).stem}.stats"
        with open(stats_file, 'w', encoding='utf-8') as f:
            print_stats(stats, f)

if __name__ == "__main__":
    main()