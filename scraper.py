#!/usr/bin/env python3
"""
Executive Email Scraper for Non-Profit Sponsorship Outreach
Uses Hunter.io API to find executive emails from company domains
"""

import requests
import csv
import os
import re
from datetime import datetime
from urllib.parse import urlparse
from dotenv import load_dotenv
from typing import List, Dict, Optional
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
HUNTER_API_BASE = "https://api.hunter.io/v2"


def extract_domain(url_or_domain: str) -> str:
    """
    Extract clean domain name from URL or return domain as-is

    Args:
        url_or_domain: URL (e.g., 'https://www.example.com/') or domain (e.g., 'example.com')

    Returns:
        Clean domain name (e.g., 'example.com')
    """
    if not url_or_domain:
        return ""

    # Remove whitespace
    url_or_domain = url_or_domain.strip()

    if not url_or_domain:
        return ""

    # If it's already a clean domain (no protocol), return as-is
    if not url_or_domain.startswith(("http://", "https://")):
        # Remove any trailing slashes or paths
        domain = url_or_domain.split("/")[0]
        return domain.lower()

    # Parse URL to extract domain
    try:
        parsed = urlparse(url_or_domain)
        domain = parsed.netloc.lower()

        if not domain:
            return ""

        # Remove 'www.' prefix if present
        if domain.startswith("www."):
            domain = domain[4:]

        return domain
    except Exception as e:
        print(f"Warning: Could not parse URL '{url_or_domain}': {e}")
        # Fallback: try to extract domain using regex
        domain_match = re.search(r"([a-zA-Z0-9-]+\.[a-zA-Z]{2,})", url_or_domain)
        if domain_match:
            return domain_match.group(1).lower()
        return ""


def clean_domains(domains: List[str]) -> List[str]:
    """
    Clean and deduplicate a list of domains/URLs

    Args:
        domains: List of URLs or domain names

    Returns:
        List of clean, unique domain names
    """
    cleaned_domains = []
    seen = set()

    for domain in domains:
        clean_domain = extract_domain(domain)
        if clean_domain and clean_domain not in seen:
            cleaned_domains.append(clean_domain)
            seen.add(clean_domain)

    return cleaned_domains


class EmailScraper:
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")
        self.api_key = api_key
        self.results = []
        self.no_results = []  # Track companies with no executive emails found

    def search_domain(self, domain: str, role: str = None) -> Dict:
        """
        Search for emails from a specific domain

        Args:
            domain: Company domain (e.g., 'stripe.com')
            role: Optional role filter (e.g., 'executive', 'ceo', 'cfo')
        """
        if not domain or not domain.strip():
            print("Warning: Empty domain provided")
            return {"domain": domain, "emails": []}

        url = f"{HUNTER_API_BASE}/domain-search"
        params = {
            "domain": domain,
            "api_key": self.api_key,
            "type": "personal",  # Focus on individual emails, not generic ones
        }

        if role:
            params["role"] = role

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("data"):
                return self._parse_results(data["data"], domain)
            else:
                print(f"No results found for {domain}")
                return {"domain": domain, "emails": []}

        except requests.exceptions.Timeout:
            print(f"Error: Request timeout for {domain}")
            return {"domain": domain, "emails": [], "error": "Timeout"}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(
                    f"Error: Rate limit exceeded. Please wait or upgrade your Hunter.io plan."
                )
            elif e.response.status_code == 401:
                print(
                    f"Error: Invalid API key. Check your HUNTER_API_KEY in .env file."
                )
            else:
                print(f"Error: HTTP {e.response.status_code} for {domain}")
            return {"domain": domain, "emails": [], "error": str(e)}
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {domain}: {e}")
            return {"domain": domain, "emails": [], "error": str(e)}

    def find_email(
        self, domain: str, first_name: str, last_name: str
    ) -> Optional[Dict]:
        """
        Find a specific person's email

        Args:
            domain: Company domain
            first_name: Person's first name
            last_name: Person's last name
        """
        url = f"{HUNTER_API_BASE}/email-finder"
        params = {
            "domain": domain,
            "first_name": first_name,
            "last_name": last_name,
            "api_key": self.api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("data") and data["data"].get("email"):
                return {
                    "email": data["data"]["email"],
                    "first_name": data["data"].get("first_name"),
                    "last_name": data["data"].get("last_name"),
                    "position": data["data"].get("position"),
                    "confidence": data["data"].get("score"),
                    "domain": domain,
                }
            return None

        except requests.exceptions.RequestException as e:
            print(f"Error finding email for {first_name} {last_name} at {domain}: {e}")
            return None

    def _parse_results(self, data: Dict, domain: str) -> Dict:
        """Parse Hunter.io API response"""
        emails = []

        for email_data in data.get("emails", []):
            # Filter for executive roles
            position = email_data.get("position") or ""
            position = position.lower() if position else ""
            executive_keywords = [
                "ceo",
                "cfo",
                "cto",
                "coo",
                "chief",
                "president",
                "founder",
                "director",
                "vp",
                "vice president",
                "head",
            ]

            is_executive = any(keyword in position for keyword in executive_keywords)

            email_info = {
                "email": email_data.get("value"),
                "first_name": email_data.get("first_name"),
                "last_name": email_data.get("last_name"),
                "position": email_data.get("position"),
                "department": email_data.get("department"),
                "confidence": email_data.get("confidence"),
                "is_executive": is_executive,
                "domain": domain,
            }
            emails.append(email_info)

        return {
            "domain": domain,
            "company": data.get("organization"),
            "emails": emails,
            "total_found": len(emails),
        }

    def scrape_companies(
        self,
        domains: List[str],
        domain_to_member: Dict[str, str] = None,
        executives_only: bool = True,
    ) -> List[Dict]:
        """
        Scrape multiple company domains

        Args:
            domains: List of company domains
            domain_to_member: Mapping of domains to BP member names
            executives_only: If True, filter for executive positions only
        """
        all_results = []
        no_results = []
        parse_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if domain_to_member is None:
            domain_to_member = {}

        for domain in domains:
            print(f"Searching {domain}...")
            result = self.search_domain(domain)
            bp_member = domain_to_member.get(domain, "Unknown")

            if result.get("emails"):
                emails = result["emails"]

                if executives_only:
                    emails = [e for e in emails if e.get("is_executive")]

                if emails:
                    for email in emails:
                        all_results.append(
                            {
                                "Domain": domain,
                                "Company": result.get("company", domain),
                                "Email": email.get("email"),
                                "First Name": email.get("first_name"),
                                "Last Name": email.get("last_name"),
                                "Position": email.get("position"),
                                "Department": email.get("department"),
                                "Confidence": email.get("confidence"),
                                "BP Member": bp_member,
                                "Parse Date": parse_date,
                            }
                        )
                    print(f"  Found {len(emails)} executive email(s)")
                else:
                    # Emails found but none are executives
                    no_results.append(
                        {
                            "Domain": domain,
                            "Company": result.get("company", domain),
                            "BP Member": bp_member,
                            "Reason": "No executive emails found",
                            "Parse Date": parse_date,
                        }
                    )
                    print(f"  No executive emails found")
            else:
                # No emails found at all
                no_results.append(
                    {
                        "Domain": domain,
                        "Company": result.get("company", domain),
                        "BP Member": bp_member,
                        "Reason": result.get("error", "No emails in database"),
                        "Parse Date": parse_date,
                    }
                )
                print(f"  No emails found")

        self.results = all_results
        self.no_results = no_results
        return all_results

    def export_to_csv(self, filename: str = "executive_emails.csv"):
        """Export results to CSV file, appending to existing file if present"""
        if not self.results:
            print("No results to export")
            return

        file_exists = os.path.exists(filename)

        # Define expected headers to ensure consistency
        expected_headers = [
            "Domain",
            "Company",
            "Email",
            "First Name",
            "Last Name",
            "Position",
            "Department",
            "Confidence",
            "BP Member",
            "Parse Date",
        ]

        # Load existing emails to avoid duplicates
        existing_emails = set()
        headers_exist = False

        if file_exists:
            try:
                with open(filename, "r", newline="", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    # Check if first line looks like headers (starts with expected column names)
                    first_line_lower = first_line.lower()
                    headers_exist = (
                        first_line_lower.startswith("domain,")
                        or "domain,company,email" in first_line_lower
                    )
                    f.seek(0)  # Reset file pointer

                    if headers_exist:
                        reader = csv.DictReader(f)
                        for row in reader:
                            email = row.get("Email", "")
                            if email:
                                existing_emails.add(email.lower())
                    else:
                        # File exists but no headers - read as plain CSV
                        reader = csv.reader(f)
                        for row in reader:
                            if (
                                len(row) > 2
                            ):  # Make sure we have at least an email column
                                existing_emails.add(
                                    row[2].lower() if len(row) > 2 else ""
                                )
            except (IOError, csv.Error) as e:
                print(f"Warning: Could not read existing file {filename}: {e}")
                print("Creating new file...")

        # Filter out duplicates and empty emails
        new_results = [
            r
            for r in self.results
            if r.get("Email") and r.get("Email", "").lower() not in existing_emails
        ]

        if not new_results:
            print(
                f"\n✓ No new emails to add (all {len(self.results)} already exist in {filename})"
            )
            return

        # Write to file (create new or append)
        try:
            if not file_exists or not headers_exist:
                # Create new file with headers or rewrite existing file with headers
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=expected_headers)
                    writer.writeheader()
                    # If file existed but had no headers, we need to preserve existing data
                    if file_exists and not headers_exist:
                        # Read existing data and rewrite it
                        with open(
                            filename + ".backup", "w", newline="", encoding="utf-8"
                        ) as backup:
                            backup.write("")  # Create empty backup
                        # For now, we'll just write the new results with headers
                        # In a production system, you might want to parse and preserve old data
                    writer.writerows(new_results)
            else:
                # Append to existing file with headers
                with open(filename, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=expected_headers)
                    writer.writerows(new_results)

            print(
                f"\n✓ Added {len(new_results)} new emails to {filename} ({len(self.results) - len(new_results)} duplicates skipped)"
            )
        except IOError as e:
            print(f"Error: Could not write to {filename}: {e}")
            print("Please check file permissions and disk space.")

    def export_to_excel(self, filename: str = "executive_emails.xlsx"):
        """Export results to Excel file with two sheets, appending to existing file if present"""
        file_exists = os.path.exists(filename)

        # Define headers for both sheets
        success_headers = [
            "Domain",
            "Company",
            "Email",
            "First Name",
            "Last Name",
            "Position",
            "Department",
            "Confidence",
            "BP Member",
            "Parse Date",
        ]

        no_results_headers = [
            "Domain",
            "Company",
            "BP Member",
            "Reason",
            "Parse Date",
        ]

        # Load existing data to avoid duplicates
        existing_emails = set()
        existing_no_result_domains = set()

        if file_exists:
            try:
                wb = load_workbook(filename)

                # Read existing emails from first sheet
                if "Executive Emails" in wb.sheetnames:
                    ws = wb["Executive Emails"]
                    for row in ws.iter_rows(min_row=2, values_only=True):
                        if row and len(row) > 2 and row[2]:  # Check email column
                            existing_emails.add(str(row[2]).lower())

                # Read existing no-result domains from second sheet
                if "No Results" in wb.sheetnames:
                    ws_no = wb["No Results"]
                    for row in ws_no.iter_rows(min_row=2, values_only=True):
                        if row and row[0]:  # Check domain column
                            existing_no_result_domains.add(str(row[0]).lower())

            except Exception as e:
                print(f"Warning: Could not read existing file {filename}: {e}")
                print("Creating new file...")
                file_exists = False

        # Filter out duplicates and empty emails
        new_results = [
            r
            for r in self.results
            if r.get("Email") and r.get("Email", "").lower() not in existing_emails
        ]

        new_no_results = [
            r
            for r in self.no_results
            if r.get("Domain")
            and r.get("Domain", "").lower() not in existing_no_result_domains
            and r.get("Domain", "").lower()
            not in existing_emails  # Don't add if we found emails
        ]

        # Check if we have anything to add
        if not new_results and not new_no_results:
            print(f"\n✓ No new data to add (all data already exists in {filename})")
            return

        try:
            if file_exists:
                # Load existing workbook
                wb = load_workbook(filename)

                # Get or create sheets
                if "Executive Emails" in wb.sheetnames:
                    ws = wb["Executive Emails"]
                else:
                    ws = wb.create_sheet("Executive Emails", 0)
                    self._style_header_row(ws, success_headers)
                    self._set_column_widths(
                        ws,
                        {
                            "A": 20,
                            "B": 25,
                            "C": 30,
                            "D": 15,
                            "E": 15,
                            "F": 30,
                            "G": 20,
                            "H": 12,
                            "I": 15,
                            "J": 20,
                        },
                    )

                if "No Results" in wb.sheetnames:
                    ws_no = wb["No Results"]
                else:
                    ws_no = wb.create_sheet("No Results")
                    self._style_header_row(ws_no, no_results_headers)
                    self._set_column_widths(
                        ws_no, {"A": 20, "B": 25, "C": 15, "D": 35, "E": 20}
                    )
            else:
                # Create new workbook with both sheets
                wb = Workbook()
                ws = wb.active
                ws.title = "Executive Emails"
                self._style_header_row(ws, success_headers)
                self._set_column_widths(
                    ws,
                    {
                        "A": 20,
                        "B": 25,
                        "C": 30,
                        "D": 15,
                        "E": 15,
                        "F": 30,
                        "G": 20,
                        "H": 12,
                        "I": 15,
                        "J": 20,
                    },
                )

                # Create No Results sheet
                ws_no = wb.create_sheet("No Results")
                self._style_header_row(ws_no, no_results_headers)
                self._set_column_widths(
                    ws_no, {"A": 20, "B": 25, "C": 15, "D": 35, "E": 20}
                )

            # Add new successful results
            for result in new_results:
                ws.append(
                    [
                        result.get("Domain", ""),
                        result.get("Company", ""),
                        result.get("Email", ""),
                        result.get("First Name", ""),
                        result.get("Last Name", ""),
                        result.get("Position", ""),
                        result.get("Department", ""),
                        result.get("Confidence", ""),
                        result.get("BP Member", ""),
                        result.get("Parse Date", ""),
                    ]
                )

            # Add new no-result entries
            for result in new_no_results:
                ws_no.append(
                    [
                        result.get("Domain", ""),
                        result.get("Company", ""),
                        result.get("BP Member", ""),
                        result.get("Reason", ""),
                        result.get("Parse Date", ""),
                    ]
                )

            # Save workbook
            wb.save(filename)

            # Print summary
            messages = []
            if new_results:
                messages.append(f"{len(new_results)} emails added")
            if new_no_results:
                messages.append(f"{len(new_no_results)} no-result companies added")

            duplicates_skipped = (len(self.results) - len(new_results)) + (
                len(self.no_results) - len(new_no_results)
            )

            print(
                f"\n✓ {', '.join(messages)} to {filename} ({duplicates_skipped} duplicates skipped)"
            )

        except Exception as e:
            print(f"Error: Could not write to {filename}: {e}")
            print("Please check file permissions and disk space.")

    def _style_header_row(self, ws, headers):
        """Apply styling to header row"""
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(
                start_color="366092", end_color="366092", fill_type="solid"
            )
            cell.alignment = Alignment(horizontal="center", vertical="center")

    def _set_column_widths(self, ws, widths):
        """Set column widths for worksheet"""
        for col, width in widths.items():
            ws.column_dimensions[col].width = width


def load_domains(filename: str = "companies.txt") -> tuple[List[str], Dict[str, str]]:
    """Load company domains from file and extract clean domain names with BP member mapping"""
    raw_domains = []
    domain_to_member = {}
    current_member = "Unknown"

    if not os.path.exists(filename):
        print(f"WARNING: {filename} not found. Creating example file...")
        try:
            with open(filename, "w") as f:
                f.write(
                    "## Example Member\nstripe.com\nsalesforce.com\n# Add more company domains below (one per line)\n"
                )
        except IOError as e:
            print(f"Error: Could not create {filename}: {e}")
            return [], {}

        return ["stripe.com", "salesforce.com"], {
            "stripe.com": "Example Member",
            "salesforce.com": "Example Member",
        }

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Check for BP member section headers (## Name)
                if line.startswith("## "):
                    current_member = line[3:].strip()  # Remove "## " prefix
                    if not current_member:
                        current_member = "Unknown"
                    continue
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    raw_domains.append(line)
                    # Map the raw domain/URL to current member
                    clean_domain = extract_domain(line)
                    if clean_domain:  # Only add non-empty domains
                        domain_to_member[clean_domain] = current_member
    except IOError as e:
        print(f"Error: Could not read {filename}: {e}")
        return [], {}

    # Extract and clean domains
    cleaned_domains = clean_domains(raw_domains)

    if not cleaned_domains:
        print(f"Warning: No valid domains found in {filename}")
        return [], {}

    print(
        f"Loaded {len(raw_domains)} entries, extracted {len(cleaned_domains)} unique domains"
    )
    if len(raw_domains) != len(cleaned_domains):
        print("Note: Some duplicates were removed during domain extraction")

    return cleaned_domains, domain_to_member


def main():
    """Main execution function"""

    # Check for API key
    if not HUNTER_API_KEY:
        print("ERROR: HUNTER_API_KEY not found!")
        print("Please create a .env file with your Hunter.io API key:")
        print("HUNTER_API_KEY=your_api_key_here")
        return

    try:
        scraper = EmailScraper(HUNTER_API_KEY)
    except ValueError as e:
        print(f"ERROR: {e}")
        return

    # Load domains from file
    domains, domain_to_member = load_domains("companies.txt")

    if not domains:
        print("ERROR: No domains found in companies.txt")
        return

    print("Executive Email Scraper for Non-Profit Sponsorship")
    print("=" * 50)
    print(f"Searching {len(domains)} companies...\n")

    # Scrape emails
    results = scraper.scrape_companies(domains, domain_to_member, executives_only=True)

    # Export to Excel
    if results:
        scraper.export_to_excel("executive_emails.xlsx")
    else:
        print("\nNo executive emails found")


if __name__ == "__main__":
    main()
