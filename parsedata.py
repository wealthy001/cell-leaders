import csv
import re

# Define files
input_file_path = "large_data.txt"
output_file_path = "extracted_contacts.csv"

extracted_data = []

try:
    with open(input_file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split data by date or newline to isolate individual records
    records = re.split(r"\d{4}-\d{2}-\d{2},?|\n", content)

    for record in records:
        record = record.strip()
        if not record:
            continue

        # Look for the email address in this chunk
        email_match = re.search(r"([\w\.-]+@[\w\.-]+\.\w+)", record)
        if email_match:
            email = email_match.group(1)

            # Extract the raw text chunk before the email address
            text_before_email = record.split(email)[0].strip()

            # Fix 1: Separate Zone from Name using the hidden Tab character (\t)
            if "\t" in text_before_email:
                name_part = text_before_email.split("\t")[1]
            else:
                name_part = text_before_email

            # Fix 2: Strip any brackets and whatever text is inside them (e.g., (Cell Leader), (Others))
            name_part = re.sub(r"\(.*?\)", "", name_part).strip()

            # Fix 3: Filter out leftover raw code strings or placeholder tags
            if (
                not name_part
                or re.match(r"^[a-z0-9]+$", name_part)
                or name_part.lower() == "please select a zone"
            ):
                name_part = "()"

            extracted_data.append({"Name": name_part, "Email": email})

    # Save to your clean CSV file
    with open(output_file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["Name", "Email"])
        writer.writeheader()
        writer.writerows(extracted_data)

    print(
        f"Successfully cleaned! Extracted {len(extracted_data)} flawless records to '{output_file_path}'."
    )

except FileNotFoundError:
    print(f"Error: Could not find '{input_file_path}'.")
except Exception as e:
    print(f"An error occurred: {e}")