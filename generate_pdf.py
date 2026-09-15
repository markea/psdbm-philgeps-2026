import subprocess
import os

md_path = "/usr/local/google/home/markea/Desktop/psdbm-philgeps-2026/mPhilGEPS_Production_BOM.md"
html_path = "/tmp/mPhilGEPS_Production_BOM.html"
pdf_path = "/usr/local/google/home/markea/Desktop/psdbm-philgeps-2026/mPhilGEPS_Production_BOM.pdf"
pdf_path_gemini = "/usr/local/google/home/markea/Desktop/psdbm-philgeps-gemini-2026/mPhilGEPS_Production_BOM.pdf"

css_content = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

@page {
    size: A4 portrait;
    margin: 16mm 14mm 16mm 14mm;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    color: #1f2937;
    background-color: #ffffff;
    line-height: 1.5;
    font-size: 9pt;
}

h1 {
    font-size: 18pt;
    font-weight: 800;
    color: #0f2b48;
    margin-top: 0;
    margin-bottom: 4px;
    border-bottom: 3px solid #1a73e8;
    padding-bottom: 6px;
}

h2 {
    font-size: 12.5pt;
    font-weight: 700;
    color: #1e3a8a;
    margin-top: 18px;
    margin-bottom: 8px;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 4px;
    page-break-after: avoid;
}

h3 {
    font-size: 10.5pt;
    font-weight: 600;
    color: #0f2b48;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 8px;
    text-align: justify;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 12px 0;
    font-size: 7.8pt;
    page-break-inside: avoid;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    border-radius: 4px;
    overflow: hidden;
}

thead {
    background-color: #0f2b48;
    color: #ffffff;
    font-weight: 600;
}

th {
    padding: 6px 7px;
    text-align: left;
    border: 1px solid #1e3a8a;
    font-size: 7.8pt;
}

td {
    padding: 5px 7px;
    border: 1px solid #e5e7eb;
    vertical-align: top;
}

tbody tr:nth-child(even) {
    background-color: #f9fafb;
}

/* Highlighting subtotals and totals */
tr:has(strong) {
    background-color: #eff6ff !important;
    font-weight: 600;
}

/* Code & Preformatted */
pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 9px 12px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.2pt;
    line-height: 1.35;
    overflow-x: auto;
    page-break-inside: avoid;
    margin: 8px 0;
}

code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 7.8pt;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 1px 4px;
    border-radius: 3px;
}

pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
}

/* Blockquotes & Notes */
blockquote {
    border-left: 4px solid #1a73e8;
    background-color: #eff6ff;
    margin: 8px 0;
    padding: 8px 12px;
    font-size: 8.2pt;
    color: #1e3a8a;
    border-radius: 0 4px 4px 0;
    page-break-inside: avoid;
}

hr {
    border: 0;
    height: 1px;
    background-color: #e5e7eb;
    margin: 14px 0;
}

/* Metadata styling */
p:has(strong:first-child) {
    line-height: 1.6;
}
"""

with open("/tmp/style.css", "w") as f:
    f.write(css_content)

# Run pandoc without title metadata to avoid duplicate header block
cmd_pandoc = [
    "pandoc",
    md_path,
    "-s",
    "--css=/tmp/style.css",
    "-o", html_path
]
subprocess.run(cmd_pandoc, check=True)

# Run headless chrome with --no-pdf-header-footer
cmd_chrome = [
    "google-chrome",
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--no-pdf-header-footer",
    "--print-to-pdf=" + pdf_path,
    html_path
]
subprocess.run(cmd_chrome, check=True)

# Copy to gemini folder as well
subprocess.run(["cp", pdf_path, pdf_path_gemini], check=True)

print("PDF successfully updated at:")
print(" -", pdf_path)
print(" -", pdf_path_gemini)
