# Security Testing Directory

This directory contains OWASP-based security testing tools for the SpendPlatform v2 application.

## Overview

The security testing suite implements automated security assessments based on the **OWASP Top 10 2021** vulnerabilities:

- **A01:2021** – Broken Access Control
- **A02:2021** – Cryptographic Failures  
- **A03:2021** – Injection
- **A04:2021** – Insecure Design
- **A05:2021** – Security Misconfiguration
- **A06:2021** – Vulnerable and Outdated Components
- **A07:2021** – Identification and Authentication Failures
- **A08:2021** – Software and Data Integrity Failures
- **A09:2021** – Security Logging and Monitoring Failures
- **A10:2021** – Server-Side Request Forgery (SSRF)

## Files

### Core Files
- **`OWASPCheck.py`** - Main security testing module with comprehensive OWASP tests
- **`run_security_tests.py`** - Test runner script with application integration
- **`requirements.txt`** - Python dependencies for security testing
- **`config.ini`** - Configuration file for test parameters

### Generated Reports
- **`owasp_security_report_YYYYMMDD_HHMMSS.json`** - Detailed JSON security report
- **`owasp_security_report_YYYYMMDD_HHMMSS.html`** - Human-readable HTML report
- **`security_summary_YYYYMMDD_HHMMSS.json`** - Summary for API integration
- **`security_test.log`** - Test execution log

## Prerequisites

1. **Application Running**: Ensure the SpendPlatform backend is running on `http://localhost:8000`
2. **Python Dependencies**: Install required packages
3. **Test Data**: Have test users in the database with known credentials

## Installation

1. Install dependencies:
```bash
# From project root - installs all dependencies including security testing
pip install -r requirements.txt

# OR from securitytesting directory - uses integrated requirements
cd securitytesting
pip install -r requirements.txt
```

2. Configure test parameters (optional):
```bash
# Edit config.ini to customize test settings
nano config.ini
```

## Usage

### Quick Start
```bash
# Install dependencies (from project root or securitytesting directory)
pip install -r requirements.txt

# Run complete security assessment
python run_security_tests.py
```

### Advanced Usage
```python
# Custom security testing
from OWASPCheck import OWASPSecurityTester

tester = OWASPSecurityTester(base_url="http://localhost:8000")
report = tester.run_comprehensive_security_test()
tester.generate_report("custom_security_report.json")
```

## Integration with Main Application

The security reports are integrated with the main SpendPlatform reporting system:

### API Endpoint
- **GET** `/reports/security-assessment` - Get latest security report
- **GET** `/reports/security-assessment/{date}` - Get specific date report

### Access Control
- Only `superadmin` and `client_admin` roles can access security reports
- Reports are client-isolated for multi-tenant security

## Security Test Categories

### 1. Access Control Tests
- Vertical privilege escalation
- Horizontal privilege escalation  
- Role-based access validation
- Client data isolation

### 2. Authentication Tests
- Weak password policies
- Session management
- Account enumeration
- Default credentials

### 3. Injection Tests
- SQL injection patterns
- NoSQL injection (if applicable)
- Command injection
- LDAP injection

### 4. Configuration Tests
- Error message disclosure
- Default configurations
- Security headers
- Version disclosure

### 5. Cryptographic Tests
- Password hashing strength
- HTTP vs HTTPS usage
- Token security
- Data encryption

## Report Interpretation

### Severity Levels
- 🔴 **CRITICAL** - Immediate security risk requiring urgent attention
- 🟠 **HIGH** - Significant security risk, should be addressed soon
- 🟡 **MEDIUM** - Moderate security risk, address in next release
- 🟢 **LOW** - Minor security concern, address when convenient
- ℹ️ **INFO** - Informational finding, no immediate risk

### HTML Report Features
- Executive summary with severity breakdown
- Detailed findings with evidence and recommendations
- OWASP category mapping
- CWE (Common Weakness Enumeration) references
- Actionable remediation guidance

## Automation & CI/CD

### Automated Testing
```bash
# Add to CI/CD pipeline
python run_security_tests.py
if [ $? -ne 0 ]; then
    echo "Security tests failed - blocking deployment"
    exit 1
fi
```

### Scheduled Assessments
```bash
# Add to crontab for weekly security scans
0 2 * * 1 cd /path/to/spendplatform-v2/securitytesting && python run_security_tests.py
```

## Best Practices

### Before Testing
1. Ensure you have authorization to test
2. Use dedicated test environment
3. Backup data if running destructive tests
4. Review test credentials and scope

### After Testing
1. Review all findings carefully
2. Prioritize critical and high severity issues
3. Track remediation progress
4. Schedule regular follow-up assessments
5. Share findings with development team

### Continuous Security
1. Run security tests before releases
2. Monitor for new OWASP vulnerabilities
3. Update test cases based on new threats
4. Maintain security testing documentation

## Customization

### Adding Custom Tests
```python
def test_custom_vulnerability(self) -> List[SecurityIssue]:
    """Custom security test"""
    issues = []
    # Your custom test logic here
    return issues
```

### Custom Payloads
- Create payload files for specific attack vectors
- Configure in `config.ini` under `custom_payloads_file`
- Support for SQL, XSS, and other injection payloads

### Environment-Specific Tests
- Modify URLs in `config.ini`
- Adjust test credentials for different environments
- Configure proxy settings for testing through security tools

## Troubleshooting

### Common Issues

**Application Not Running**
```
✗ Backend application is not running on http://localhost:8000
```
**Solution**: Start the backend server first

**Missing Dependencies**
```
✗ Missing required dependencies
```
**Solution**: Run `pip install -r requirements.txt`

**Permission Errors**
```
Error loading security report: Permission denied
```
**Solution**: Check file permissions in securitytesting directory

**Test Failures**
- Check network connectivity
- Verify test credentials
- Review application logs
- Check security testing logs

## Security Considerations

- **Test Environment**: Never run against production without explicit authorization
- **Credentials**: Use dedicated test accounts, not production credentials
- **Data Protection**: Security reports may contain sensitive information
- **Access Control**: Restrict access to security reports and testing tools
- **Logging**: Security test activities are logged for audit purposes

## Contributing

When adding new security tests:
1. Follow OWASP Top 10 categorization
2. Include proper evidence collection
3. Provide actionable recommendations
4. Add appropriate severity levels
5. Update documentation and examples

## Support

For security testing support:
- Review the generated HTML reports for detailed findings
- Check the security_test.log for execution details
- Refer to OWASP documentation for vulnerability details
- Consult with security team for complex findings

---

**⚠️ Important**: This tool is for authorized security testing only. Ensure you have proper authorization before running security tests against any application.