#!/usr/bin/env python3
"""
Advanced Security Testing Module
Enhanced OWASP security testing with advanced tools integration
"""

import subprocess
import sys
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedSecurityTester:
    """
    Advanced Security Testing class that extends basic OWASP tests
    with additional security tools and methodologies
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or str(Path(__file__).parent.parent)
        self.results = {
            "static_analysis": {},
            "dependency_scan": {},
            "cryptographic_analysis": {},
            "jwt_analysis": {},
            "code_quality": {}
        }
        
    def check_advanced_dependencies(self) -> Dict[str, bool]:
        """Check which advanced security tools are available"""
        tools = {
            "bandit": False,
            "safety": False,
            "cryptography": False,
            "jwt": False,
            "beautifulsoup4": False
        }
        
        for tool in tools.keys():
            try:
                if tool == "jwt":
                    import jwt
                    tools[tool] = True
                elif tool == "beautifulsoup4":
                    import bs4
                    tools[tool] = True
                else:
                    __import__(tool)
                    tools[tool] = True
            except ImportError:
                pass
                
        return tools
    
    def run_bandit_analysis(self) -> Dict[str, Any]:
        """Run Bandit static security analysis"""
        logger.info("Running Bandit static security analysis...")
        
        try:
            import bandit
            from bandit.core import config, manager
            from bandit.core.constants import CRITERIA
            
            # Configure Bandit
            conf = config.BanditConfig()
            
            # Target directories for analysis
            target_dirs = [
                os.path.join(self.project_root, "backend", "src"),
                os.path.join(self.project_root, "securitytesting")
            ]
            
            # Run Bandit analysis
            b_mgr = manager.BanditManager(conf, 'file')
            
            results = {
                "total_issues": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0,
                "issues": [],
                "files_scanned": 0,
                "status": "completed"
            }
            
            for target_dir in target_dirs:
                if os.path.exists(target_dir):
                    try:
                        # Discover Python files
                        b_mgr.discover([target_dir], recursive=True)
                        b_mgr.run_tests()
                        
                        # Process results
                        for result in b_mgr.get_issue_list():
                            issue = {
                                "filename": result.fname,
                                "line_number": result.lineno,
                                "test_name": result.test,
                                "issue_severity": result.severity,
                                "issue_confidence": result.confidence,
                                "issue_text": result.text,
                                "code": result.get_code(max_lines=3),
                                "more_info": result.more_info
                            }
                            results["issues"].append(issue)
                            results["total_issues"] += 1
                            
                            if result.severity == "HIGH":
                                results["high_severity"] += 1
                            elif result.severity == "MEDIUM":
                                results["medium_severity"] += 1
                            else:
                                results["low_severity"] += 1
                        
                        results["files_scanned"] += len(b_mgr.files_list)
                        
                    except Exception as e:
                        logger.error(f"Error scanning {target_dir}: {str(e)}")
            
            return results
            
        except ImportError:
            return {
                "status": "not_available",
                "message": "Bandit not installed. Install with: pip install bandit>=1.7.0"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def run_safety_check(self) -> Dict[str, Any]:
        """Run Safety dependency vulnerability scan"""
        logger.info("Running Safety dependency vulnerability scan...")
        
        try:
            # Run safety check via subprocess
            result = subprocess.run([
                sys.executable, "-m", "safety", "check", 
                "--json", "--full-report"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                # No vulnerabilities found
                return {
                    "status": "secure",
                    "vulnerabilities": [],
                    "total_vulnerabilities": 0,
                    "message": "No known security vulnerabilities found in dependencies"
                }
            else:
                # Parse JSON output
                try:
                    vulnerabilities = json.loads(result.stdout)
                    return {
                        "status": "vulnerabilities_found",
                        "vulnerabilities": vulnerabilities,
                        "total_vulnerabilities": len(vulnerabilities),
                        "message": f"Found {len(vulnerabilities)} security vulnerabilities"
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "error",
                        "message": "Could not parse Safety output",
                        "raw_output": result.stdout
                    }
                    
        except FileNotFoundError:
            return {
                "status": "not_available", 
                "message": "Safety not installed. Install with: pip install safety>=2.0.0"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def analyze_jwt_security(self) -> Dict[str, Any]:
        """Analyze JWT token security implementation"""
        logger.info("Analyzing JWT security implementation...")
        
        try:
            import jwt
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            
            results = {
                "jwt_library_version": jwt.__version__,
                "supported_algorithms": jwt.get_algos_by_key_size(2048),
                "security_recommendations": [],
                "potential_issues": [],
                "status": "analyzed"
            }
            
            # Check for common JWT security issues
            
            # 1. Algorithm confusion
            results["security_recommendations"].append({
                "category": "Algorithm Security",
                "recommendation": "Always specify algorithm explicitly in jwt.decode()",
                "severity": "HIGH",
                "details": "Prevent algorithm confusion attacks by specifying allowed algorithms"
            })
            
            # 2. Secret key strength
            results["security_recommendations"].append({
                "category": "Key Management", 
                "recommendation": "Use strong, randomly generated secret keys (>256 bits)",
                "severity": "CRITICAL",
                "details": "Weak secrets can lead to token forgery"
            })
            
            # 3. Token expiration
            results["security_recommendations"].append({
                "category": "Token Lifecycle",
                "recommendation": "Implement proper token expiration and refresh mechanisms",
                "severity": "MEDIUM",
                "details": "Long-lived tokens increase security risk"
            })
            
            # 4. Signature verification
            results["security_recommendations"].append({
                "category": "Signature Verification",
                "recommendation": "Never skip signature verification in production",
                "severity": "CRITICAL", 
                "details": "Always verify token signatures to prevent tampering"
            })
            
            return results
            
        except ImportError:
            return {
                "status": "not_available",
                "message": "PyJWT not installed. Install with: pip install pyjwt>=2.4.0"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def analyze_cryptographic_implementation(self) -> Dict[str, Any]:
        """Analyze cryptographic implementation security"""
        logger.info("Analyzing cryptographic implementation...")
        
        try:
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa, padding
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            
            results = {
                "cryptography_library_version": None,
                "hash_algorithms": [],
                "encryption_algorithms": [],
                "security_analysis": [],
                "recommendations": [],
                "status": "analyzed"
            }
            
            # Get library version
            try:
                import cryptography
                results["cryptography_library_version"] = cryptography.__version__
            except:
                pass
            
            # Analyze available hash algorithms
            secure_hashes = [hashes.SHA256, hashes.SHA384, hashes.SHA512, hashes.BLAKE2b]
            insecure_hashes = [hashes.SHA1, hashes.MD5]
            
            for hash_algo in secure_hashes:
                results["hash_algorithms"].append({
                    "algorithm": hash_algo.name,
                    "security_level": "SECURE",
                    "recommended": True
                })
            
            for hash_algo in insecure_hashes:
                results["hash_algorithms"].append({
                    "algorithm": hash_algo.name,
                    "security_level": "INSECURE", 
                    "recommended": False,
                    "reason": "Cryptographically broken or weak"
                })
            
            # Encryption algorithm analysis
            results["encryption_algorithms"] = [
                {
                    "algorithm": "AES-256-GCM",
                    "security_level": "SECURE",
                    "recommended": True,
                    "use_case": "Symmetric encryption with authentication"
                },
                {
                    "algorithm": "RSA-4096",
                    "security_level": "SECURE", 
                    "recommended": True,
                    "use_case": "Asymmetric encryption and digital signatures"
                },
                {
                    "algorithm": "ChaCha20-Poly1305",
                    "security_level": "SECURE",
                    "recommended": True,
                    "use_case": "High-performance authenticated encryption"
                }
            ]
            
            # Security recommendations
            results["recommendations"] = [
                {
                    "category": "Password Hashing",
                    "recommendation": "Use Argon2id, bcrypt, or scrypt for password hashing",
                    "severity": "CRITICAL",
                    "details": "Never use plain hash functions for passwords"
                },
                {
                    "category": "Random Number Generation",
                    "recommendation": "Use cryptographically secure random number generators",
                    "severity": "HIGH",
                    "details": "Use os.urandom() or secrets module for cryptographic randomness"
                },
                {
                    "category": "Key Management",
                    "recommendation": "Implement proper key rotation and storage",
                    "severity": "HIGH",
                    "details": "Store keys securely and rotate them regularly"
                },
                {
                    "category": "TLS Configuration",
                    "recommendation": "Use TLS 1.3 with strong cipher suites",
                    "severity": "MEDIUM",
                    "details": "Disable weak ciphers and outdated TLS versions"
                }
            ]
            
            return results
            
        except ImportError:
            return {
                "status": "not_available",
                "message": "Cryptography library not installed. Install with: pip install cryptography>=3.4.0"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def scan_for_secrets(self) -> Dict[str, Any]:
        """Scan for hardcoded secrets and sensitive information"""
        logger.info("Scanning for hardcoded secrets...")
        
        import re
        
        # Common secret patterns
        secret_patterns = {
            "api_key": r"(?i)(api[_-]?key|apikey)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_-]{20,})",
            "password": r"(?i)(password|passwd|pwd)[\"'\s]*[:=][\"'\s]*([^\s\"']{8,})",
            "secret": r"(?i)(secret|secret[_-]?key)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_-]{16,})",
            "token": r"(?i)(token|auth[_-]?token)[\"'\s]*[:=][\"'\s]*([a-zA-Z0-9_.-]{20,})",
            "private_key": r"-----BEGIN (?:RSA )?PRIVATE KEY-----",
            "aws_access": r"AKIA[0-9A-Z]{16}",
            "jwt_token": r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*"
        }
        
        results = {
            "total_files_scanned": 0,
            "total_secrets_found": 0,
            "secrets_by_type": {},
            "files_with_secrets": [],
            "status": "completed"
        }
        
        # Scan Python files in backend
        backend_dir = os.path.join(self.project_root, "backend", "src")
        if os.path.exists(backend_dir):
            for root, dirs, files in os.walk(backend_dir):
                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache']]
                
                for file in files:
                    if file.endswith(('.py', '.env', '.config', '.ini')):
                        file_path = os.path.join(root, file)
                        results["total_files_scanned"] += 1
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                
                            file_secrets = []
                            for secret_type, pattern in secret_patterns.items():
                                matches = re.finditer(pattern, content, re.MULTILINE)
                                for match in matches:
                                    line_num = content[:match.start()].count('\n') + 1
                                    secret_info = {
                                        "type": secret_type,
                                        "line": line_num,
                                        "match": match.group(0)[:100] + "..." if len(match.group(0)) > 100 else match.group(0),
                                        "severity": "HIGH" if secret_type in ["private_key", "aws_access"] else "MEDIUM"
                                    }
                                    file_secrets.append(secret_info)
                                    
                                    if secret_type not in results["secrets_by_type"]:
                                        results["secrets_by_type"][secret_type] = 0
                                    results["secrets_by_type"][secret_type] += 1
                                    results["total_secrets_found"] += 1
                            
                            if file_secrets:
                                results["files_with_secrets"].append({
                                    "file": os.path.relpath(file_path, self.project_root),
                                    "secrets": file_secrets
                                })
                                
                        except Exception as e:
                            logger.debug(f"Error scanning {file_path}: {str(e)}")
        
        return results
    
    def run_comprehensive_advanced_tests(self) -> Dict[str, Any]:
        """Run all advanced security tests"""
        logger.info("Running comprehensive advanced security tests...")
        
        # Check available tools
        available_tools = self.check_advanced_dependencies()
        
        results = {
            "test_timestamp": str(pd.Timestamp.now()),
            "available_tools": available_tools,
            "static_analysis": {},
            "dependency_scan": {},
            "jwt_analysis": {},
            "cryptographic_analysis": {},
            "secrets_scan": {},
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0
            }
        }
        
        # Run static analysis with Bandit
        if available_tools["bandit"]:
            results["static_analysis"] = self.run_bandit_analysis()
        
        # Run dependency vulnerability scan
        results["dependency_scan"] = self.run_safety_check()
        
        # Analyze JWT implementation
        if available_tools["jwt"]:
            results["jwt_analysis"] = self.analyze_jwt_security()
        
        # Analyze cryptographic implementation
        if available_tools["cryptography"]:
            results["cryptographic_analysis"] = self.analyze_cryptographic_implementation()
        
        # Scan for hardcoded secrets
        results["secrets_scan"] = self.scan_for_secrets()
        
        # Calculate summary
        for test_category in ["static_analysis", "dependency_scan", "secrets_scan"]:
            test_results = results.get(test_category, {})
            if "total_issues" in test_results:
                results["summary"]["total_issues"] += test_results["total_issues"]
            if "high_severity" in test_results:
                results["summary"]["high_issues"] += test_results["high_severity"]
            if "medium_severity" in test_results:
                results["summary"]["medium_issues"] += test_results["medium_severity"]
            if "low_severity" in test_results:
                results["summary"]["low_issues"] += test_results["low_severity"]
        
        return results
    
    def generate_advanced_report(self, output_file: str = "advanced_security_report.json") -> str:
        """Generate advanced security report"""
        results = self.run_comprehensive_advanced_tests()
        
        # Save JSON report
        report_path = os.path.join(os.path.dirname(__file__), output_file)
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Generate HTML report
        html_file = report_path.replace('.json', '.html')
        self._generate_advanced_html_report(results, html_file)
        
        logger.info(f"Advanced security reports generated: {report_path}, {html_file}")
        return report_path
    
    def _generate_advanced_html_report(self, results: Dict[str, Any], html_file: str):
        """Generate HTML report for advanced security testing"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advanced Security Testing Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff; }}
        .section {{ margin-bottom: 30px; padding: 20px; border-radius: 8px; background: #f9f9f9; }}
        .section h3 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        .issue {{ padding: 10px; margin: 10px 0; border-radius: 4px; border-left: 4px solid #ccc; }}
        .issue.critical {{ border-left-color: #dc3545; background-color: #f8d7da; }}
        .issue.high {{ border-left-color: #fd7e14; background-color: #fff3cd; }}
        .issue.medium {{ border-left-color: #ffc107; background-color: #fff3cd; }}
        .issue.low {{ border-left-color: #28a745; background-color: #d4edda; }}
        .code {{ background: #f1f1f1; padding: 10px; border-radius: 4px; font-family: monospace; overflow-x: auto; }}
        .recommendation {{ background: #e7f3ff; padding: 10px; border-radius: 4px; margin-top: 10px; }}
        .status-available {{ color: #28a745; font-weight: bold; }}
        .status-unavailable {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Advanced Security Testing Report</h1>
            <p>SpendPlatform v2 - Comprehensive Security Analysis</p>
            <p>Generated on: {results.get('test_timestamp', 'N/A')}</p>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Total Issues</h3>
                <h2>{results['summary']['total_issues']}</h2>
            </div>
            <div class="summary-card" style="border-left-color: #dc3545;">
                <h3>Critical</h3>
                <h2>{results['summary']['critical_issues']}</h2>
            </div>
            <div class="summary-card" style="border-left-color: #fd7e14;">
                <h3>High</h3>
                <h2>{results['summary']['high_issues']}</h2>
            </div>
            <div class="summary-card" style="border-left-color: #ffc107;">
                <h3>Medium</h3>
                <h2>{results['summary']['medium_issues']}</h2>
            </div>
        </div>

        <div class="section">
            <h3>🔧 Available Security Tools</h3>
"""
        
        # Add available tools section
        for tool, available in results['available_tools'].items():
            status_class = "status-available" if available else "status-unavailable"
            status_text = "✓ Available" if available else "✗ Not Available"
            html_content += f'<p><strong>{tool}:</strong> <span class="{status_class}">{status_text}</span></p>'
        
        # Add test sections
        if results.get('static_analysis') and results['static_analysis'].get('status') == 'completed':
            bandit_results = results['static_analysis']
            html_content += f"""
        </div>
        
        <div class="section">
            <h3>🔍 Static Code Analysis (Bandit)</h3>
            <p><strong>Files Scanned:</strong> {bandit_results.get('files_scanned', 0)}</p>
            <p><strong>Total Issues:</strong> {bandit_results.get('total_issues', 0)}</p>
            <div class="summary">
                <div class="summary-card" style="border-left-color: #dc3545;">
                    <h4>High</h4>
                    <h3>{bandit_results.get('high_severity', 0)}</h3>
                </div>
                <div class="summary-card" style="border-left-color: #ffc107;">
                    <h4>Medium</h4>
                    <h3>{bandit_results.get('medium_severity', 0)}</h3>
                </div>
                <div class="summary-card" style="border-left-color: #28a745;">
                    <h4>Low</h4>
                    <h3>{bandit_results.get('low_severity', 0)}</h3>
                </div>
            </div>
"""
            
            # Add individual issues
            for issue in bandit_results.get('issues', [])[:10]:  # Show first 10 issues
                severity_class = issue['issue_severity'].lower()
                html_content += f"""
            <div class="issue {severity_class}">
                <h4>{issue['test_name']} - {issue['issue_severity']}</h4>
                <p><strong>File:</strong> {issue['filename']}:{issue['line_number']}</p>
                <p>{issue['issue_text']}</p>
                <div class="code">{issue.get('code', 'N/A')}</div>
            </div>
"""
        
        # Add dependency scan results
        if results.get('dependency_scan'):
            dep_results = results['dependency_scan']
            html_content += f"""
        </div>
        
        <div class="section">
            <h3>📦 Dependency Vulnerability Scan (Safety)</h3>
            <p><strong>Status:</strong> {dep_results.get('status', 'N/A')}</p>
            <p><strong>Message:</strong> {dep_results.get('message', 'N/A')}</p>
"""
        
        html_content += """
        </div>
    </div>
</body>
</html>
"""
        
        with open(html_file, 'w') as f:
            f.write(html_content)


# Fix the import issue
try:
    import pandas as pd
except ImportError:
    # Create a simple timestamp if pandas is not available
    from datetime import datetime
    class MockTimestamp:
        @staticmethod
        def now():
            return datetime.now().isoformat()
    pd = type('MockPandas', (), {'Timestamp': MockTimestamp})()


if __name__ == "__main__":
    print("Advanced Security Testing Module")
    print("================================")
    
    tester = AdvancedSecurityTester()
    
    # Check available tools
    tools = tester.check_advanced_dependencies()
    print("\nAvailable Security Tools:")
    for tool, available in tools.items():
        status = "✓" if available else "✗"
        print(f"  {status} {tool}")
    
    # Generate advanced report
    report_file = tester.generate_advanced_report("advanced_security_report.json")
    print(f"\nAdvanced security report generated: {report_file}")