# cis6930fa24 -- Project1

Name: Venkata Tharun Seemakurthi

# Assignment Description 

This project is centered around developing a Python-based redaction system that automates the identification and censoring of sensitive information within text files. The application leverages a glob pattern to ingest multiple input files, with options to censor personal names, dates, phone numbers, and addresses based on specified command-line flags. For named entity recognition (NER), the system integrates SpaCy's `en_core_web_md` NLP model, allowing precise detection and redaction of PERSON and DATE entity types. Additionally, users can define custom concepts for redaction, which are matched using regular expressions. The processed text is outputted to new files with a `.censored` extension, stored in a designated output directory. The program also generates statistical reports, detailing the extent of redaction, such as the number of characters or entities censored, with the option to output these statistics to `stderr` or `stdout`. This project provides a modular, scalable solution for handling sensitive information in large datasets, focusing on ensuring data privacy compliance.

**Assignment Objective:**
The objective of this project is to develop a Python-based application capable of:
1) Accepts text files based on a provided glob pattern (e.g., *.txt) and processes each file for censoring sensitive information.
2) Redacts personal `names`, `dates`, `phone numbers`, and `addresses` based on flags provided in the command-line interface.
3) Includes additional censoring of a specific concept (such as `kids` or `prison`) by recognizing associated terms in the text.
4) Generates new files for censored content by appending `.censored` to the original filename. All output files are stored in the specified output directory.
5) Provides a summary of the censored content, including the length of the censored text, written to either stderr, stdout or a file based on the user's preference.
6) Utilizes the SpaCy NLP library to identify and redact sensitive information from the text, ensuring accurate detection of named entities, dates, and other patterns defined in the project.
   
**Requirements:**
1) Input Pattern: Specify an input pattern for text files using a glob (e.g. *.txt).
2) Redaction Flags: Implement redaction flags for `names (--names)`, `dates (--dates)`, `phone numbers (--phones)`, `addresses (--address)`, and a custom `concept (--concept)`.
3) SpaCy NLP Model: Use the SpaCy en_core_web_md model to detect and redact personal names and dates.
4) Output Directory: Censored files should be stored in the specified output directory with the .censored extension appended to their names.
5) Stats Output: Provide statistics related to the redaction process, including the number of characters censored, either to stderr, stdout or a file.

# How to install
Install pipenv using the command: 

      pip install pipenv

Install spacy library using the command: 

      pipenv install spacy

Install en_core_web_md pipeline using the command: 

      pipenv run python -m spacy download en_core_web_md

Install pytest testing framework using the command: 

      pipenv install pytest 

**Full project (CLI + API + tests):** From the repository root, install everything declared in the `Pipfile` / `Pipfile.lock` (spaCy, NLTK, FastAPI, Uvicorn, pytest, etc.):

      pipenv install

The `Pipfile` pins the `en_core_web_md` model wheel. If the model fails to load, run:

      pipenv run python -m spacy download en_core_web_md

### Dashboard (Node.js)

The React UI lives in `dashboard/`. Install its dependencies once:

      cd dashboard
      npm install

## How to run
To execute the project, navigate to the project directory and run the following commands:

1) To get the output under the files directory, use command:

         pipenv run python redactor.py --input 'testing_files/<file_name>' --names --dates --phones --address --concept '<concept to censor>' --output 'files/' --stats stderr

   For instance (command used in my local):

         pipenv run python redactor.py --input 'testing_files/sample_file_1' --names --dates --phones --address --concept 'cricket' --output 'files/' --stats stderr

## Web dashboard (React + FastAPI)

The repository includes a **browser UI** (`dashboard/`) backed by a small **FastAPI** app (`api/app.py`) that calls the same `redactor.py` logic via `redact_string()`.

### Run the API (terminal 1)

From the project root (Python 3.11 + Pipenv):

      pipenv run uvicorn api.app:app --reload --host 127.0.0.1 --port 8765

- **`GET /api/health`** — quick health check.
- **`POST /api/redact`** — JSON body: `text` (string), `flags` (`names`, `dates`, `phones`, `address`, `emails` booleans), optional `concept` (string). Returns `redacted_text`, `stats`, and `original_length`.

If binding fails on Windows (`WinError 10013`), try another port (e.g. `8888`) and set the same URL in `dashboard/vite.config.js` under `server.proxy['/api'].target`.

### Run the React app (terminal 2)

      cd dashboard
      npm run dev

Open **http://localhost:5173**. Vite proxies `/api/*` to the backend URL in `vite.config.js` (default `http://127.0.0.1:8765`).

### Production notes

- **CORS:** `api/app.py` currently allows only local Vite preview origins. For a public frontend host, add your site origin to `allow_origins` or use a reverse proxy so the UI and API share one origin.
- **Static build:** `npm run build` in `dashboard/` writes to `dashboard/dist/`. Serve that folder from any static host and point the UI at your deployed API URL (the dev proxy is not used in production).

## Output Scenario

Text before Redactor:

        Hello all, Rohit Sharma is going to provide a speech on tuesday, 10/12/2024. He is going to provide a lecture on cricketing knowledge and on kids cricket practice. Also a speech on October 19th and 25 October 2024 and 31 Oct 2024.
        His mail id is rohitg@gmail.com and you can contact him through his mobile number 3769876542.
        Cricket is a source of knowledge and rohit sharma is going to tell you about cricket through zoom meeting .
        Credentials for zoom meeting is rgs_34@gmail.com.
        The address to visit him is 4300 NE Okala St 31567. To visit his office then the address is 3690 Malcolm St 51206.
        
Text after Redaction:

        Hello all, ████████████ is going to provide a speech on ███████████████████.███████████████████████████████████████████████████████████████████████████████████████ Also a speech on ████████████ and ███████████████ and ███████████.
        His mail id is ████████████████ and you can contact him through his mobile number ██████████.████████████████████████████████████████████████████████████████████████████████████████████████████████████
        Credentials for zoom meeting is ████████████████.
        The address to visit him is ██████████████████████. To visit his office then the address is █████████████████████.

## Test Cases Run
Running the following pipenv command runs the pytest cases. This project have 6 test cases.
command to run test cases: 

      pipenv run python -m pytest -v

## Functions
### redactor.py

1) **main()**
    
    Main function to handle argument parsing and initiate the redaction process.

    This function uses argparse to collect command-line arguments for specifying input files, output directories, and redaction flags (for names, dates,phones, addresses, and a custom concept). It passes these flags and parameters to the `read_files` function to process and censor the input files.
    Additionally, it handles the output of redaction statistics, either to stderr, stdout, or a specified file.

    - Function Flow:
        - Parses command-line arguments using argparse.
        - Constructs a dictionary (`flags`) to specify which types of information (e.g., names, dates) should be redacted
        - Calling `read_files` to process the input files and apply redactions.
        - Outputs the redaction statistics based on the `--stats` argument:
            - If `--stats stderr` is passed, statistics are printed to `stderr`.
            - If `--stats stdout` is passed, statistics are printed to `stdout`.
            - If a file path is provided for `--stats`, statistics are written to that file.
    
    - Arguments collected via argparse:
        - `--input`: Glob pattern for selecting input text files. Required.
        - `--output`: Directory to store censored output files. Required.
        - `--names`: Flag to indicate censoring of names (PERSON entities detected by SpaCy).
        - `--dates`: Flag to indicate censoring of dates (DATE entities detected by SpaCy).
        - `--phones`: Flag to indicate censoring of phone numbers (using a regex pattern for 10-digit phone numbers).
        - `--address`: Flag to indicate censoring of addresses (using a regex pattern).
        - `--concept`: Custom concept and its synonyms to censor the whole sentence. The function will redact the sentence based on the occurrences of the concept and its synonyms.
        - `--stats`: Defines where to output redaction statistics. Choices include:
            - `stderr`: Output statistics to stderr.
            - `stdout`: Output statistics to stdout.
            - File path: Output statistics to a specified file.

2) **redactor_text(doc, flags, concept, file_stats)**
    - Redacts sensitive information based on the flags and updates the statistics in `file_stats`.
    - Parameters:
        - doc (spacy.tokens.Doc): The SpaCy document object containing the text to be censored.
        - flags (dict): A dictionary of flags indicating which types of information to censor. 
          The keys in the flags dictionary include:
            - 'names': Whether to redact names (PERSON entities detected by SpaCy).
            - 'dates': Whether to redact dates (DATE entities detected by SpaCy).
            - 'phones': Whether to redact phone numbers using a regex pattern.
            - 'address': Whether to redact addresses using a regex pattern.
            - 'concept': Whether to redact a custom concept or keyword, provided separately.
        - The script redacts both names and full `email addresses`. If the names flag is set, only the username part of the email (before the @) will be censored, while the domain remains intact. If the emails flag is set, the entire email address will be redacted for confidentiality.
        - concept (str or None): A custom string or concept to censor, if provided. The function will redact all occurrences of this concept in a case-insensitive manner.
        - file_stats (dict): A dictionary that keeps track of the number of occurrences of each type of redacted information (e.g., 'names', 'dates', 'phones', 'addresses', 'emails', 'concept'). This dictionary is updated each time a piece of sensitive information is redacted.
    - Returns: 
        - str: The redacted version of the input text, where sensitive information has been replaced by block characters (█).

    This function processes a given SpaCy document (`doc`) to redact sensitive information such as names, dates, phone numbers, addresses, and custom concepts. It uses SpaCy's NLP model to detect named entities and applies regular expressions to detect phone numbers and addresses. For each 
    type of sensitive information, it replaces the identified content with block characters (█) and updates the statistics in the `file_stats` dictionary.

    **Steps:**
    1) Redacts addresses using a regular expression before processing other entities. The regex matches addresses that contain numbers or letters, and common street types (e.g., St, Ave, Rd). Each address is replaced by '█████' and the count is incremented in `file_stats['addresses']`.
    2) Redacts names (PERSON entities) and dates (DATE entities) using SpaCy's named entity recognition. Each occurrence is replaced by block characters and the count is updated in `file_stats['names']` and `file_stats['dates']`.
    3) Redacts phone numbers using a regular expression for 10-digit phone numbers. Each match is replaced with block characters and the count is updated in `file_stats['phones']`.
    4) Redacts the whole email addresses (eg: the mail id "rohitg@gmail.com" gets completely redacted). Whole email is replaced with block characters and the count is updated in `file_stats['emails']`.
    5) Redacts occurrences of a custom concept (case-insensitive) if provided. If matched with the concept and its synonyms, whole sentence it is replaced with block characters and the count is updated in `file_stats['concept']`.

3) **read_files(input_pattern, output_dir, flags, concept)**
    - Reads text files from the specified input pattern, applies redaction to sensitive information, and saves the redacted files to the output directory. It also gathers and returns statistics about the redaction process for each file.
    - Parameters:
        - input_pattern (str): A glob pattern to match input text files (e.g. '*.txt'). This allows for batch processing of files by matching multiple files with a single pattern.
        - output_dir (str): The directory where the redacted files will be saved. The output files will have the same name as the original but with a `.censored` extension.
        - flags (dict): A dictionary of flags indicating which types of information to censor.
          The keys include:
            - 'names': Whether to redact names (PERSON entities detected by SpaCy).
            - 'dates': Whether to redact dates (DATE entities detected by SpaCy).
            - 'phones': Whether to redact phone numbers using a regex pattern.
            - 'address': Whether to redact addresses using a regex pattern.
            - 'concept': Whether to redact a custom concept, if provided.
        - concept (str or None): A custom string or concept to censor the senetence.
      The function will censor all occurrences of this concept if provided.
    - Returns: 
        - dict: A dictionary containing statistics for each processed file.
          The key is the file path, and the value is a dictionary with two entries:
            - 'length': The number of characters in the redacted text.
            - 'stats': A dictionary containing the count of redacted names, dates, phones, addresses, emails, and concepts.

    - Function Flow:
        - Uses the `glob` module to match the input pattern and find all files matching the pattern.
        - For each file:
            - Reads the file content.
            - Calls the `redactor_text()` function to redact sensitive information based on the provided flags.
            - Writes the redacted text to a new file with a `.censored` extension in the output directory.
            - Collects statistics about the redaction (number of names, dates, addresses, etc.) and stores them in the `file_stats` dictionary.
        - Returns the overall redaction statistics for all processed files.

    The `glob` module is used to match the input pattern, allowing the user to select multiple files by specifying a pattern (e.g., '*.txt'). This helps in processing a batch of files at once without needing to specify each file manually.

4) **redact_concept_sentences(redacted_text, concept, file_stats)**
    - I use WordNet in NLTK to expand the concept's synonyms and catch related words more accurately. 
    - Redacts entire sentences in the given text that contain a specified concept or any related terms.
    - Parameters:
        - redacted_text (str): The input text to be processed and redacted.
        - concept (str): The main concept to search for in the text. Sentences containing this concept or its synonyms will be redacted.
        - file_stats (dict): A dictionary to store statistics about the redaction process, particularly the count of redacted sentences.

    - Returns:
        - str: The modified text with sentences containing the concept or its synonyms redacted.

5) **print_stats(stats, output)**
    - Prints redaction statistics for each processed file to the specified output (stderr, stdout, or a file).
    - Parameters:
        - stats (dict): A dictionary containing statistics for each processed file.
          The keys in the dictionary are file paths, and the values are dictionaries containing:
            - 'length': The length (number of characters) of the redacted text.
            - 'stats': A dictionary with the following keys:
            - 'names': Number of redacted names (PERSON entities).
            - 'dates': Number of redacted dates (DATE entities).
            - 'phones': Number of redacted phone numbers (identified via regex).
            - 'addresses': Number of redacted addresses (identified via regex).
            - 'emails': Number of redacted emails (email parts).
            - 'concept': Number of redacted occurrences of the custom concept.
        - output (io.TextIOWrapper): The output stream where the statistics will be printed. This could be `stderr`, `stdout`, or a file stream, depending on how the user invokes the script.

    - Function Flow:
        - Iterates through each file and its corresponding statistics in the `stats` dictionary.
        - For each file:
            - Verifies that the data is in the correct dictionary format.
            - Constructs a formatted string containing the file path, redacted text length, and counts of each type of redacted entity (names, dates, phones, addresses, emails, custom concept).
        - Prints the formatted string to the specified output (stderr, stdout, or a file).
        - If the data for a file is not in the expected format (i.e. not a dictionary), prints an error message indicating invalid data for that file.

    - Example Output:

      For each file, the following will be printed:
      
                File: path/to/<file.txt>, 
                Length: 500, 
                Names: 2, 
                Dates: 1, 
                Phones: 1, 
                Addresses: 1, 
                Emails: 2, 
                Concept: 2

6) **redact_string(text, flags, concept=None)**  
    Runs the same redaction pipeline as the CLI on a **single string**. Returns `(redacted_text, file_stats)` where `file_stats` matches the per-category counts used elsewhere. Used by **`api/app.py`** for the React dashboard (`POST /api/redact`).
  
## Example Usage to run commands
- To get the output under the files directory, use the following command:

      pipenv run python redactor.py --input 'testing_files/sample_file_1' --names --dates --phones --address --concept 'cricket' --output 'files/' --stats stderr

## The stdout/stderr/file format
The stats structure will be outputted in the following format after running the file using the above command.

**Format:**

                File: path/to/<file.txt>, 
                Length: 0, 
                Names: 0, 
                Dates: 0, 
                Phones: 0, 
                Addresses: 0, 
                Emails: 0, 
                Concept: 0

**Sample Output:**

                File: testing_files/sample_file_1, 
                Length: 470, 
                Names: 2, 
                Dates: 1, 
                Phones: 1, 
                Addresses: 2, 
                Emails: 2, 
                Concept: 2

### test_flags.py
1) **create_doc(text)**
    - Converts the provided text string into a SpaCy document object.
    - Parameters:
        - text (str): The input text to convert into a SpaCy Doc object.
    - Returns:
        - spacy.tokens.Doc: A SpaCy Doc object containing the parsed text.

2) **test_redact_names()**
    - Tests the redaction of names in a given text.
    - This function ensures that all detected PERSON entities (names) are properly redacted when the 'names' flag is set to True. The file_stats dictionary tracks the number of redacted names.
    - Asserts:
        - The redacted text matches the expected output.
        - No other entities are redacted when the 'names' flag is enabled.

3) **test_redact_dates()**
    - Tests the redaction of dates in a given text.
    - This function checks that all detected DATE entities are redacted when the 'dates' flag is enabled. The file_stats dictionary tracks the number of redacted dates.
    - Asserts:
        - The redacted text matches the expected output.
        - The number of redacted dates is correctly tracked.

4) **test_redact_phones()**
    - Tests the redaction of phone numbers in a given text.
    - This function verifies that phone numbers are correctly redacted when the 'phones' flag is enabled. It also tracks the count of redacted phone numbers using the file_stats dictionary.
    - Asserts:
        - The redacted text matches the expected output.
        - The number of redacted phone numbers is correctly tracked.

5) **test_redact_address()** 
    - Tests the redaction of addresses in a given text.
    - This function ensures that addresses are correctly detected and redacted based on a regex pattern when the 'address' flag is enabled. The count of redacted addresses is tracked using the file_stats dictionary.
    - Asserts:
        - The redacted text matches the expected output.
        - The number of redacted addresses is correctly tracked.

6) **test_redact_emails()**
    - Tests the redaction of email addresses in a given text.
    - This function checks that the email addresses is redacted when the flag is enabled. The count of redacted email addresses is tracked using the file_stats dictionary.
    - Asserts:
        - The redacted text matches the expected output.
        - The number of redacted email addresses is correctly tracked.

7) **test_redact_concept()**
    - Tests the redaction of a custom concept (word or phrase) in a given text.
    - This function ensures that all occurrences of a specified custom concept are redacted when the 'concept' flag is enabled. The count of redacted concepts is tracked using the file_stats dictionary.
    - Asserts:
        - The redacted text matches the expected output.
        - The custom concept is redacted as expected.

## Bugs and Assumptions
1) The detection of custom concepts relies on exact string matching, which could miss variations of the concept (e.g., plurals or words with slight variations). Additionally, redaction of custom concepts might not perform well with complex concepts that span multiple words or phrases.
2) Assumption: The input text is assumed to be well-formed, meaning it follows standard rules for punctuation, spacing, and capitalization. Non-standard input may not be properly redacted.
3) The redaction of custom concepts is case-insensitive, but the detection of other entities such as names and addresses might still be case-sensitive depending on SpaCy’s entity recognition. This may cause inconsistencies between detected and redacted text.
4) The current regular expression for address redaction assumes a strict pattern for street names and postal codes. Addresses that don't follow this pattern or are formatted differently (e.g. missing postal code, abbreviated street names) might not be redacted.
5) Assumption: The project assumes that all input text files are encoded in UTF-8. Files with different encodings might cause issues during the reading and redaction process.
6) Assumption: This project assumes that the sensitive information to be redacted is embedded in plain textual content. It does not account for non-text formats (e.g. PDFs with images, non-extractable content) or structured documents like HTML or JSON.