#!/usr/bin/env python3
"""
Executive Email Scraper for Non-Profit Sponsorship Outreach
Uses Hunter.io API to find executive emails from company domains
"""

import requests
import csv
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
HUNTER_API_BASE = "https://api.hunter.io/v2"


class EmailScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.results = []

    def search_domain(self, domain: str, role: str = None) -> Dict:
        """
        Search for emails from a specific domain

        Args:
            domain: Company domain (e.g., 'stripe.com')
            role: Optional role filter (e.g., 'executive', 'ceo', 'cfo')
        """
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
            position = email_data.get("position", "").lower()
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
        self, domains: List[str], executives_only: bool = True
    ) -> List[Dict]:
        """
        Scrape multiple company domains

        Args:
            domains: List of company domains
            executives_only: If True, filter for executive positions only
        """
        all_results = []

        for domain in domains:
            print(f"Searching {domain}...")
            result = self.search_domain(domain)

            if result.get("emails"):
                emails = result["emails"]

                if executives_only:
                    emails = [e for e in emails if e.get("is_executive")]

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
                        }
                    )

                print(f"  Found {len(emails)} executive email(s)")
            else:
                print(f"  No emails found")

        self.results = all_results
        return all_results

    def export_to_csv(self, filename: str = "executive_emails.csv"):
        """Export results to CSV file, appending to existing file if present"""
        if not self.results:
            print("No results to export")
            return

        file_exists = os.path.exists(filename)

        # Load existing emails to avoid duplicates
        existing_emails = set()
        if file_exists:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_emails.add(row.get('Email', '').lower())

        # Filter out duplicates
        new_results = [r for r in self.results if r.get('Email', '').lower() not in existing_emails]

        if not new_results:
            print(f"\n✓ No new emails to add (all {len(self.results)} already exist in {filename})")
            return

        # Append to file
        with open(filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
            if not file_exists:
                writer.writeheader()
            writer.writerows(new_results)

        print(f"\n✓ Added {len(new_results)} new emails to {filename} ({len(self.results) - len(new_results)} duplicates skipped)")


def load_domains(filename: str = "companies.txt") -> List[str]:
    """Load company domains from file"""
    domains = []

    if not os.path.exists(filename):
        print(f"WARNING: {filename} not found. Creating example file...")
        with open(filename, 'w') as f:
            f.write("stripe.com\nsalesforce.com\n# Add more company domains below (one per line)\n")
        return ["stripe.com", "salesforce.com"]

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                domains.append(line)

    return domains


def main():
    """Main execution function"""

    # Check for API key
    if not HUNTER_API_KEY:
        print("ERROR: HUNTER_API_KEY not found!")
        print("Please create a .env file with your Hunter.io API key:")
        print("HUNTER_API_KEY=your_api_key_here")
        return

    scraper = EmailScraper(HUNTER_API_KEY)

    # Load domains from file
    domains = load_domains("companies.txt")

    if not domains:
        print("ERROR: No domains found in companies.txt")
        return

    print("Executive Email Scraper for Non-Profit Sponsorship")
    print("=" * 50)
    print(f"Searching {len(domains)} companies...\n")

    # Scrape emails
    results = scraper.scrape_companies(domains, executives_only=True)

    # Export to CSV
    if results:
        scraper.export_to_csv("executive_emails.csv")
    else:
        print("\nNo executive emails found")


if __name__ == "__main__":
    main()
