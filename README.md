# Domain Filter & Analysis Tool

Optimized single-file tool to filter and analyze GoDaddy auction domains.

## Features

- Interactive command-line interface
- Flexible domain count selection
- Customizable IT/Other industry ratio
- Exclude previously selected domains
- Full business analysis with brand names and navigation menus
- Industry-based categorization and scoring

## Usage

### Interactive Mode

```bash
python domain_filter.py
```

Then answer the prompts:
1. **Input folder**: Path to CSV files (default: `./unfiltered-domains-csv`)
2. **Domain count**: How many domains to filter (default: `50`)
3. **IT percentage**: Percentage of IT/Software domains (default: `80`)
4. **Exclusion file**: Optional CSV file with domains to exclude
5. **Output filename**: Name for the output file (default: `filtered_domains_X.csv`)

### Example Session

```
Enter input folder path (default: ./unfiltered-domains-csv): 
  [Press Enter for default]

How many domains do you want to filter? (default: 50): 100
  [Enter 100 for 100 domains]

IT / Software percentage (0-100, default: 80): 70
  [Enter 70 for 70% IT, 30% Other]

Exclude domains from file (press Enter to skip): top_50_domains_filtered.csv
  [Enter filename to exclude already selected domains]

Output filename (default: filtered_domains_100.csv): my_domains.csv
  [Enter custom filename or press Enter for default]
```

## Output

The tool generates a CSV file with:
- Suggested Brand Name
- Domain Name
- Registration Date
- Industry Category
- Menu Navigation Structure
- Price
- Domain Age
- SEO Metrics (Majestic TF/CF)
- Traffic
- Combined Quality Score
- Investment Comment

## Industry Categories

- IT / Software
- Manufacturing
- Healthcare
- Engineering
- HR / Recruitment
- Analytics
- Cybersecurity
- Wellness / Education Tech

## Scoring Algorithm

Domains are scored (0-100) based on:
- Industry relevance (25%)
- Domain age (20%)
- SEO metrics - TF/CF (20%)
- Backlinks quality (20%)
- Traffic (15%)
- TLD bonus (.com preferred)
- Profile health ratio

## Requirements

- Python 3.6+
- CSV files in GoDaddy export format

## Tips

1. **First Run**: Select 50 domains with 80% IT
2. **Second Run**: Exclude first batch, select another 50
3. **Custom Mix**: Adjust IT percentage based on your needs
4. **Quality Filter**: Higher scored domains appear at the top

## File Structure

```
project/
├── domain_filter.py              # Main tool (optimized single file)
├── unfiltered-domains-csv/       # Input CSV files
├── filtered_domains_50.csv       # Output files
└── README.md                     # This file
```

## Legacy Files

The following files are superseded by `domain_filter.py`:
- `analyze_domains.py` (original analyzer)
- `filter_top50_domains.py` (first 50 filter)
- `filter_next_50_domains.py` (next 50 filter)

You can keep them for reference or delete them.
