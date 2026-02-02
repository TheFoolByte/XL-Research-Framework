"""
Data export utilities for results

Migrated from xl-research/src/utils/exporter.py
Adapted for integration with main framework.
"""
import json
import csv
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import html

# Use framework logger if available, fallback to basic
try:
    from core.logger import log as logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ResultExporter:
    """Export results to various formats"""
    
    def __init__(self, output_dir: str = "results", simplified_output_dir: str = "results2"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Simplified output directory
        self.simplified_output_dir = Path(simplified_output_dir)
        self.simplified_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.json_dir = self.output_dir / "json"
        self.csv_dir = self.output_dir / "csv"
        self.html_dir = self.output_dir / "html"
        
        for directory in [self.json_dir, self.csv_dir, self.html_dir]:
            directory.mkdir(exist_ok=True)
    
    def generate_filename(self, prefix: str, extension: str) -> str:
        """Generate timestamped filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def export_json(self, data: Any, filename: str = None) -> str:
        """Export data to JSON file"""
        if filename is None:
            filename = self.generate_filename("result", "json")
        
        filepath = self.json_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return str(filepath)
            
        except Exception as e:
            if hasattr(logger, 'error'):
                logger.error(f"Failed to export JSON: {str(e)}")
            return None

    def export_simplified_json(self, data: Dict, filename: str = None) -> str:
        """Export simplified data to JSON file in results2"""
        if filename is None:
            filename = self.generate_filename("simple_result", "json")
        
        filepath = self.simplified_output_dir / filename
        
        try:
            # Extract found codes and simplify
            simplified_data = []
            found_codes = data.get('found_codes', [])
            
            if isinstance(found_codes, list):
                for item in found_codes:
                    if isinstance(item, dict):
                        simple_item = {
                            "family_code": item.get("family_code"),
                            "data": item.get("data")
                        }
                        simplified_data.append(simple_item)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(simplified_data, f, indent=2, ensure_ascii=False, default=str)
            
            return str(filepath)
            
        except Exception as e:
            if hasattr(logger, 'error'):
                logger.error(f"Failed to export simplified JSON: {str(e)}")
            return None
    
    def export_csv(self, data: List[Dict], filename: str = None) -> str:
        """Export data to CSV file"""
        if not data:
            return None
        
        if filename is None:
            filename = self.generate_filename("result", "csv")
        
        filepath = self.csv_dir / filename
        
        try:
            # Extract all unique keys
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
            
            # Write CSV
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                writer.writeheader()
                
                for item in data:
                    # Flatten nested dictionaries
                    flat_item = self._flatten_dict(item)
                    writer.writerow(flat_item)
            
            return str(filepath)
            
        except Exception as e:
            if hasattr(logger, 'error'):
                logger.error(f"Failed to export CSV: {str(e)}")
            return None
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary"""
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key, sep=sep))
            elif isinstance(v, list):
                # Convert list to string representation
                items[new_key] = json.dumps(v, ensure_ascii=False)
            else:
                items[new_key] = v
        
        return items
    
    def export_html_report(self, data: Dict, filename: str = None) -> str:
        """Export data to HTML report"""
        if filename is None:
            filename = self.generate_filename("report", "html")
        
        filepath = self.html_dir / filename
        
        try:
            html_content = self._generate_html(data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(filepath)
            
        except Exception as e:
            if hasattr(logger, 'error'):
                logger.error(f"Failed to export HTML: {str(e)}")
            return None
    
    def _generate_html(self, data: Dict) -> str:
        """Generate HTML report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Escape HTML in data
        safe_data = self._escape_html(data)
        
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>XL Research Report - {timestamp}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                }}
                .header .subtitle {{
                    opacity: 0.9;
                    font-size: 1.2em;
                }}
                .card {{
                    background: white;
                    border-radius: 10px;
                    padding: 25px;
                    margin-bottom: 25px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s;
                }}
                .card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }}
                .card h2 {{
                    color: #667eea;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-item {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .stat-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #667eea;
                }}
                .stat-label {{
                    color: #666;
                    font-size: 0.9em;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #667eea;
                    color: white;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
                .badge {{
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    font-weight: bold;
                    margin: 0 5px;
                }}
                .badge-success {{
                    background: #c6f6d5;
                    color: #22543d;
                }}
                .badge-danger {{
                    background: #fed7d7;
                    color: #742a2a;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 50px;
                    color: #666;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 XL Research Report</h1>
                <div class="subtitle">Generated: {timestamp}</div>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value" id="totalFound">0</div>
                    <div class="stat-label">Family Codes Found</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="successRate">0%</div>
                    <div class="stat-label">Success Rate</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="totalAttempts">0</div>
                    <div class="stat-label">Total Attempts</div>
                </div>
            </div>
            
            <div class="card">
                <h2>📋 Executive Summary</h2>
                <div id="summary"></div>
            </div>
            
            <div class="card">
                <h2>🔍 Found Family Codes</h2>
                <div id="familyCodes"></div>
            </div>
            
            <div class="footer">
                <p>Generated by XL Research Tools • For research purposes only</p>
            </div>
            
            <script>
                const data = {json.dumps(safe_data, indent=2, default=str)};
                
                document.getElementById('totalFound').textContent = 
                    data.found_codes ? data.found_codes.length : 0;
                
                if (data.statistics && data.statistics.success_rate) {{
                    document.getElementById('successRate').textContent = 
                        (data.statistics.success_rate * 100).toFixed(1) + '%';
                }}
                
                document.getElementById('totalAttempts').textContent = 
                    data.statistics ? data.statistics.total_attempts || 0 : 0;
                
                const summaryEl = document.getElementById('summary');
                summaryEl.innerHTML = `
                    <p>Research completed on ${{new Date().toLocaleDateString()}}.</p>
                    <p>Found <strong>${{data.found_codes ? data.found_codes.length : 0}}</strong> family codes.</p>
                `;
                
                const codesEl = document.getElementById('familyCodes');
                if (data.found_codes && data.found_codes.length > 0) {{
                    let html = '<table><tr><th>Family Code</th><th>Category</th><th>Price</th><th>Status</th></tr>';
                    
                    data.found_codes.forEach(code => {{
                        const category = code.analysis && code.analysis.patterns && code.analysis.patterns[0] 
                            ? code.analysis.patterns[0].category 
                            : 'Unknown';
                        
                        const price = code.data && code.data.price 
                            ? 'Rp ' + code.data.price.toLocaleString() 
                            : 'N/A';
                        
                        html += `
                            <tr>
                                <td><code>${{code.family_code}}</code></td>
                                <td><span class="badge badge-success">${{category}}</span></td>
                                <td>${{price}}</td>
                                <td><span class="badge badge-success">Active</span></td>
                            </tr>
                        `;
                    }});
                    
                    html += '</table>';
                    codesEl.innerHTML = html;
                }} else {{
                    codesEl.innerHTML = '<p>No family codes found.</p>';
                }}
            </script>
        </body>
        </html>
        """
        
        return html_template
    
    def _escape_html(self, data: Any) -> Any:
        """Recursively escape HTML in data"""
        if isinstance(data, str):
            return html.escape(data)
        elif isinstance(data, dict):
            return {k: self._escape_html(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._escape_html(item) for item in data]
        else:
            return data
    
    def export_all(self, data: Dict, base_name: str = None) -> Dict:
        """
        Export data to all formats
        
        Returns:
            Dict with paths to exported files
        """
        if base_name is None:
            base_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results = {}
        
        # Export JSON
        json_file = f"{base_name}.json"
        json_path = self.export_json(data, json_file)
        if json_path:
            results['json'] = json_path
        
        # Export Simplified JSON (results2)
        simple_json_path = self.export_simplified_json(data, json_file)
        if simple_json_path:
            results['simplified_json'] = simple_json_path
        
        # Export CSV (if we have array data)
        if isinstance(data, list) or ('found_codes' in data and isinstance(data['found_codes'], list)):
            csv_file = f"{base_name}.csv"
            
            if isinstance(data, list):
                csv_data = data
            else:
                csv_data = data.get('found_codes', [])
            
            csv_path = self.export_csv(csv_data, csv_file)
            if csv_path:
                results['csv'] = csv_path
        
        # Export HTML
        html_file = f"{base_name}.html"
        html_path = self.export_html_report(data, html_file)
        if html_path:
            results['html'] = html_path
        
        return results
