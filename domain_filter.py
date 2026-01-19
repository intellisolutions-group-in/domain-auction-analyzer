#!/usr/bin/env python3
"""
Interactive Domain Filter & Analysis Tool
Processes GoDaddy auction data to identify top investment opportunities
"""

import csv
import os
import re
from typing import Dict, List, Tuple, Set

# ============================================================================
# CONFIGURATION
# ============================================================================

CURRENT_YEAR = 2025

INDUSTRY_KEYWORDS = {
    "IT / Software": [
        "tech", "software", "digital", "cloud", "web", "system", "dev",
        "app", "platform", "code", "api", "saas", "solution", "cyber",
        "data", "net", "host", "server", "online", "site", "media"
    ],
    "Manufacturing": [
        "manufacture", "factory", "production", "industrial", "machinery",
        "assembly", "plant", "fabrication", "automation"
    ],
    "Healthcare": [
        "health", "care", "medical", "clinic", "pharma", "bio", "med",
        "hospital", "therapy", "wellness", "diagnostic", "patient", "doctor"
    ],
    "Engineering": [
        "engineer", "mechanical", "civil", "design", "rd", "cad",
        "construction", "structural", "technical", "consult", "architect"
    ],
    "HR / Recruitment": [
        "hr", "job", "recruit", "talent", "staff", "career", "hire",
        "employment", "workforce", "personnel", "resume"
    ],
    "Analytics": [
        "analytics", "insight", "metrics", "intelligence",
        "dashboard", "report", "visualization", "ml", "algorithm"
    ],
    "Cybersecurity": [
        "secure", "shield", "protect", "defense", "security",
        "firewall", "encryption", "audit", "compliance", "risk"
    ],
    "Wellness / Education Tech": [
        "wellness", "edu", "learn", "school", "fitness", "training",
        "course", "academy", "teaching", "student", "nutrition", "yoga"
    ]
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_domain(domain: str) -> str:
    """Extract clean domain name without TLD"""
    domain = domain.lower().strip()
    domain_name = re.sub(r'\.(com|net|org|info|biz|co|io|ai|tech|cc|tv|us|ws)$', '', domain)
    return domain_name

def get_tld(domain: str) -> str:
    """Extract TLD from domain"""
    match = re.search(r'\.([a-z]+)$', domain.lower())
    return f".{match.group(1)}" if match else ".com"

def match_industry(domain_name: str) -> Tuple[str, float]:
    """Match domain against industry keywords"""
    best_industry = None
    best_score = 0
    
    for industry, keywords in INDUSTRY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in domain_name:
                if domain_name == keyword or domain_name.startswith(keyword) or domain_name.endswith(keyword):
                    score = 1.0
                else:
                    score = 0.7
                
                if score > best_score:
                    best_score = score
                    best_industry = industry
    
    return best_industry, best_score

def calculate_combined_score(domain_data: Dict, max_age: int, max_backlinks: int, max_traffic: int) -> float:
    """Calculate weighted domain score (0-100)"""
    
    age_score = min(domain_data['age'] / max_age, 1.0) if max_age > 0 else 0
    
    tf_cf_score = (domain_data['tf'] + domain_data['cf']) / 100
    
    backlink_total = domain_data['backlinks'] + domain_data['referring_domains']
    backlink_score = min(backlink_total / max(max_backlinks, 1), 1.0) if max_backlinks > 0 else 0
    
    traffic_score = min(domain_data['traffic'] / max(max_traffic, 1), 1.0) if max_traffic > 0 else 0
    
    industry_weight = domain_data['industry_match_quality']
    
    combined_score = (
        0.25 * industry_weight +
        0.20 * age_score +
        0.20 * tf_cf_score +
        0.20 * backlink_score +
        0.15 * traffic_score
    ) * 100
    
    tld_bonus = 1.0 if domain_data['tld'] == '.com' else 0.85
    
    health_ratio = domain_data['tf'] / max(domain_data['cf'], 1) if domain_data['cf'] > 0 else 1.0
    health_bonus = 1.0 if health_ratio >= 0.7 else 0.9
    
    combined_score *= tld_bonus * health_bonus
    
    return round(min(combined_score, 100), 2)

def generate_brand_name(domain_name: str, domain: str) -> str:
    """Generate professional brand name from domain"""
    clean_name = re.sub(r'[-_\d]', ' ', domain_name)
    
    words = clean_name.split()
    if len(words) == 1:
        brand = words[0].capitalize()
    else:
        brand = ' '.join(word.capitalize() for word in words if len(word) > 2)
    
    if len(brand) < 3:
        brand = domain.split('.')[0].capitalize()
    
    return brand

def generate_menu_navigation(industry: str) -> str:
    """Generate professional navigation structure based on industry"""
    base_menu = ["Home", "About", "Contact"]
    
    industry_specific = {
        "Manufacturing": ["Products", "Solutions", "Industries", "Resources"],
        "IT / Software": ["Solutions", "Products", "Pricing", "Resources", "Developers"],
        "Healthcare": ["Services", "Solutions", "Resources", "Patients"],
        "Engineering": ["Services", "Projects", "Solutions", "Resources"],
        "HR / Recruitment": ["Jobs", "Employers", "Candidates", "Resources"],
        "Analytics": ["Platform", "Solutions", "Insights", "Resources"],
        "Cybersecurity": ["Solutions", "Services", "Resources", "Partners"],
        "Wellness / Education Tech": ["Courses", "Programs", "Resources", "Community"]
    }
    
    middle_items = industry_specific.get(industry, ["Products", "Services", "Resources"])
    menu_items = [base_menu[0]] + middle_items + base_menu[1:]
    menu_items = menu_items[:7]
    
    return " | ".join(menu_items)

def generate_comment(domain_data: Dict) -> str:
    """Generate investment rationale comment"""
    score = domain_data['combined_score']
    age = domain_data['age']
    tf = domain_data['tf']
    cf = domain_data['cf']
    traffic = domain_data['traffic']
    price = domain_data['price']
    
    comments = []
    
    if age >= 15:
        comments.append(f"Established {age}-year domain provides strong authority")
    elif age >= 10:
        comments.append(f"Mature {age}-year domain with proven history")
    
    if tf > 10:
        comments.append(f"Excellent Trust Flow ({tf}) indicates quality backlinks")
    elif tf > 0 and cf > 0:
        ratio = tf / cf
        if ratio >= 0.7:
            comments.append(f"Healthy TF/CF ratio ({tf}/{cf}) shows natural profile")
    
    if traffic > 20:
        comments.append(f"Existing traffic ({traffic}/mo) demonstrates audience")
    
    if price < 1000:
        comments.append("Attractive entry price point")
    
    if score >= 75:
        comments.append("STRONG BUY recommendation")
    elif score >= 60:
        comments.append("Good investment opportunity")
    
    if len(comments) >= 2:
        return f"{comments[0]}. {comments[1]}."
    elif comments:
        return f"{comments[0]}."
    else:
        return "Solid domain with industry relevance and clean metrics."

def load_excluded_domains(filepath: str) -> Set[str]:
    """Load domains that should be excluded"""
    excluded = set()
    if not filepath or not os.path.exists(filepath):
        return excluded
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                domain = row['Domain Name'].strip().lower()
                excluded.add(domain)
        print(f"  Loaded {len(excluded)} domains to exclude from: {filepath}")
    except Exception as e:
        print(f"  Warning: Could not load exclusion file: {e}")
    
    return excluded

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def load_csv_files(folder_path: str, excluded_domains: Set[str]) -> List[Dict]:
    """Load all CSV files from folder"""
    all_domains = []
    seen_domains = set()
    
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    print(f"\n{'='*80}")
    print(f"LOADING DATA FROM {len(csv_files)} CSV FILES")
    print(f"{'='*80}\n")
    
    excluded_count = 0
    
    for filename in csv_files:
        filepath = os.path.join(folder_path, filename)
        print(f"  Loading: {filename}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    domain_name = row['Domain Name'].strip()
                    domain_lower = domain_name.lower()
                    
                    if domain_lower in seen_domains:
                        continue
                    
                    if domain_lower in excluded_domains:
                        excluded_count += 1
                        continue
                    
                    seen_domains.add(domain_lower)
                    
                    domain_data = {
                        'domain': domain_name,
                        'price': float(row['Price']) if row['Price'] else 0,
                        'age': int(row['Domain Age']) if row['Domain Age'] else 0,
                        'tf': int(row['Majestic TF']) if row['Majestic TF'] else 0,
                        'cf': int(row['Majestic CF']) if row['Majestic CF'] else 0,
                        'traffic': int(row['Traffic']) if row['Traffic'] else 0,
                        'backlinks': int(row['Backlinks']) if row['Backlinks'] else 0,
                        'referring_domains': int(row['Referring Domains']) if row['Referring Domains'] else 0,
                    }
                    all_domains.append(domain_data)
                except (ValueError, KeyError) as e:
                    continue
    
    print(f"\n  Total unique domains loaded: {len(all_domains)}")
    if excluded_count > 0:
        print(f"  Domains excluded: {excluded_count}")
    
    return all_domains

def filter_and_score_domains(domains: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Score and separate IT vs Other industry domains"""
    
    print(f"\n{'='*80}")
    print("INDUSTRY MATCHING & SCORING")
    print(f"{'='*80}\n")
    
    it_domains = []
    other_domains = []
    excluded_org = 0
    excluded_horizon = 0
    
    for domain_data in domains:
        domain_name = clean_domain(domain_data['domain'])
        industry, match_quality = match_industry(domain_name)
        
        if industry:
            domain_data['domain_name_clean'] = domain_name
            domain_data['tld'] = get_tld(domain_data['domain'])
            domain_data['industry'] = industry
            domain_data['industry_match_quality'] = match_quality
            domain_data['register_date'] = CURRENT_YEAR - domain_data['age']
            
            # Exclude .org domains
            if domain_data['tld'] == '.org':
                excluded_org += 1
                continue
            
            # Exclude domains containing "horizon"
            if 'horizon' in domain_name:
                excluded_horizon += 1
                continue
            
            if industry == "IT / Software":
                it_domains.append(domain_data)
            else:
                other_domains.append(domain_data)
    
    all_matched = it_domains + other_domains
    
    if not all_matched:
        return it_domains, other_domains
    
    max_age = max((d['age'] for d in all_matched), default=26)
    max_backlinks = max((d['backlinks'] + d['referring_domains'] for d in all_matched), default=500)
    max_traffic = max((d['traffic'] for d in all_matched), default=100)
    
    for domain_data in all_matched:
        score = calculate_combined_score(domain_data, max_age, max_backlinks, max_traffic)
        domain_data['combined_score'] = score
    
    it_domains.sort(key=lambda x: x['combined_score'], reverse=True)
    other_domains.sort(key=lambda x: x['combined_score'], reverse=True)
    
    print(f"  IT / Software domains found: {len(it_domains)}")
    print(f"  Other industry domains found: {len(other_domains)}")
    if excluded_org > 0:
        print(f"  .org domains excluded: {excluded_org}")
    
    return it_domains, other_domains

def select_top_domains(it_domains: List[Dict], other_domains: List[Dict], 
                      total_count: int, it_percentage: float) -> List[Dict]:
    """Select top domains based on counts and percentages"""
    
    it_count = int(total_count * it_percentage)
    other_count = total_count - it_count
    
    print(f"\n{'='*80}")
    print(f"SELECTING TOP {total_count} DOMAINS ({it_count} IT + {other_count} Other)")
    print(f"{'='*80}\n")
    
    selected_it = it_domains[:it_count]
    selected_other = other_domains[:other_count]
    
    print(f"  Selected IT domains: {len(selected_it)}")
    if selected_it:
        print(f"    Score range: {selected_it[0]['combined_score']:.2f} - {selected_it[-1]['combined_score']:.2f}")
    
    print(f"  Selected Other domains: {len(selected_other)}")
    if selected_other:
        print(f"    Score range: {selected_other[0]['combined_score']:.2f} - {selected_other[-1]['combined_score']:.2f}")
    
    # Fill gaps if we don't have enough
    it_gap = it_count - len(selected_it)
    other_gap = other_count - len(selected_other)
    
    if it_gap > 0 and len(other_domains) > other_count:
        print(f"\n  Filling {it_gap} IT domain gap with Other industry domains...")
        extra_other = other_domains[other_count:other_count + it_gap]
        selected_other.extend(extra_other)
        print(f"    Added {len(extra_other)} more Other domains")
    
    if other_gap > 0 and len(it_domains) > it_count:
        print(f"\n  Filling {other_gap} Other domain gap with IT domains...")
        extra_it = it_domains[it_count:it_count + other_gap]
        selected_it.extend(extra_it)
        print(f"    Added {len(extra_it)} more IT domains")
    
    all_selected = selected_it + selected_other
    all_selected.sort(key=lambda x: x['combined_score'], reverse=True)
    
    return all_selected

def generate_analysis_csv(domains: List[Dict], output_path: str):
    """Generate final CSV with business analysis"""
    
    print(f"\n{'='*80}")
    print(f"GENERATING OUTPUT CSV")
    print(f"{'='*80}\n")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'Suggested Brand Name Based On Domain',
            'Domain Name',
            'Domain Register Date',
            'Industry',
            'Menu Navigation',
            'Price',
            'Domain Age',
            'Majestic TF',
            'Majestic CF',
            'Traffic',
            'Combined Score',
            'Comment'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for domain_data in domains:
            brand_name = generate_brand_name(domain_data['domain_name_clean'], domain_data['domain'])
            menu_nav = generate_menu_navigation(domain_data['industry'])
            comment = generate_comment(domain_data)
            
            row = {
                'Suggested Brand Name Based On Domain': brand_name,
                'Domain Name': domain_data['domain'],
                'Domain Register Date': domain_data['register_date'],
                'Industry': domain_data['industry'],
                'Menu Navigation': menu_nav,
                'Price': f"${domain_data['price']:.2f}",
                'Domain Age': domain_data['age'],
                'Majestic TF': domain_data['tf'],
                'Majestic CF': domain_data['cf'],
                'Traffic': domain_data['traffic'],
                'Combined Score': domain_data['combined_score'],
                'Comment': comment
            }
            
            writer.writerow(row)
    
    print(f"  [OK] Exported {len(domains)} domains to: {output_path}")

def display_results(domains: List[Dict], it_percentage: float):
    """Display results grouped by industry"""
    
    print(f"\n{'='*80}")
    print(f"TOP {len(domains)} DOMAINS - INDUSTRY BREAKDOWN")
    print(f"{'='*80}\n")
    
    by_industry = {}
    for domain in domains:
        industry = domain['industry']
        if industry not in by_industry:
            by_industry[industry] = []
        by_industry[industry].append(domain)
    
    for industry, industry_domains in sorted(by_industry.items()):
        print(f"\n{industry} ({len(industry_domains)} domains)")
        print(f"{'-'*80}")
        print(f"{'Rank':<6} {'Score':<8} {'Domain':<40} {'Price':<12}")
        print(f"{'-'*6} {'-'*8} {'-'*40} {'-'*12}")
        
        for i, domain in enumerate(industry_domains[:10], 1):  # Show top 10 per industry
            print(f"{i:<6} {domain['combined_score']:<8.2f} {domain['domain']:<40} ${domain['price']:<11.2f}")
        
        if len(industry_domains) > 10:
            print(f"  ... and {len(industry_domains) - 10} more")
    
    it_count = len(by_industry.get('IT / Software', []))
    other_count = len(domains) - it_count
    
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"  Total domains exported:      {len(domains)}")
    print(f"  IT / Software:               {it_count} ({it_count/len(domains)*100:.1f}%)")
    print(f"  Other industries:            {other_count} ({other_count/len(domains)*100:.1f}%)")
    print(f"  Average score:               {sum(d['combined_score'] for d in domains) / len(domains):.2f}")
    print(f"  Score range:                 {domains[0]['combined_score']:.2f} - {domains[-1]['combined_score']:.2f}")
    print(f"{'='*80}\n")

# ============================================================================
# USER INPUT
# ============================================================================

def get_user_inputs():
    """Get configuration from user"""
    
    print("\n" + "="*80)
    print("INTERACTIVE DOMAIN FILTER & ANALYSIS TOOL")
    print("="*80 + "\n")
    
    # Input folder
    default_folder = './unfiltered-domains-csv'
    input_folder = input(f"Enter input folder path (default: {default_folder}): ").strip()
    if not input_folder:
        input_folder = default_folder
    
    if not os.path.exists(input_folder):
        print(f"\nERROR: Folder '{input_folder}' not found!")
        return None
    
    # Number of domains
    while True:
        try:
            domain_count = input("\nHow many domains do you want to filter? (default: 50): ").strip()
            domain_count = int(domain_count) if domain_count else 50
            if domain_count <= 0:
                print("  Please enter a positive number.")
                continue
            break
        except ValueError:
            print("  Please enter a valid number.")
    
    # IT percentage
    while True:
        try:
            it_percent = input("\nIT / Software percentage (0-100, default: 80): ").strip()
            it_percent = float(it_percent) if it_percent else 80
            if it_percent < 0 or it_percent > 100:
                print("  Please enter a value between 0 and 100.")
                continue
            it_percent = it_percent / 100
            break
        except ValueError:
            print("  Please enter a valid number.")
    
    # Exclusion file
    exclude_file = input("\nExclude domains from file (press Enter to skip): ").strip()
    if exclude_file and not os.path.exists(exclude_file):
        print(f"  Warning: File '{exclude_file}' not found. Continuing without exclusions.")
        exclude_file = None
    
    # Output file
    default_output = f"filtered_domains_{domain_count}.csv"
    output_file = input(f"\nOutput filename (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output
    
    if not output_file.endswith('.csv'):
        output_file += '.csv'
    
    return {
        'input_folder': input_folder,
        'domain_count': domain_count,
        'it_percentage': it_percent,
        'exclude_file': exclude_file,
        'output_file': output_file
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    # Get user inputs
    config = get_user_inputs()
    
    if not config:
        return
    
    print(f"\n{'='*80}")
    print("CONFIGURATION")
    print(f"{'='*80}")
    print(f"  Input folder:      {config['input_folder']}")
    print(f"  Domain count:      {config['domain_count']}")
    print(f"  IT percentage:     {config['it_percentage']*100:.0f}%")
    print(f"  Other percentage:  {(1-config['it_percentage'])*100:.0f}%")
    print(f"  Exclusion file:    {config['exclude_file'] or 'None'}")
    print(f"  Output file:       {config['output_file']}")
    print(f"{'='*80}")
    
    # Load excluded domains
    excluded_domains = load_excluded_domains(config['exclude_file'])
    
    # Load data
    all_domains = load_csv_files(config['input_folder'], excluded_domains)
    
    if not all_domains:
        print("\nERROR: No domains loaded.")
        return
    
    # Filter and score
    it_domains, other_domains = filter_and_score_domains(all_domains)
    
    if not it_domains and not other_domains:
        print("\nERROR: No domains matched industry criteria.")
        return
    
    # Select top domains
    selected_domains = select_top_domains(
        it_domains, 
        other_domains, 
        config['domain_count'],
        config['it_percentage']
    )
    
    if len(selected_domains) < config['domain_count']:
        print(f"\nWarning: Only found {len(selected_domains)} domains (target: {config['domain_count']})")
    
    if not selected_domains:
        print("\nERROR: No domains selected.")
        return
    
    # Generate CSV
    generate_analysis_csv(selected_domains, config['output_file'])
    
    # Display results
    display_results(selected_domains, config['it_percentage'])
    
    print(f"\n  File saved: {config['output_file']}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
