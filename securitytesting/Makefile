# Makefile for Security Testing
# Quick commands for running OWASP security assessments

.PHONY: help install test clean report advanced basic check-tools

help:
	@echo "SpendPlatform v2 Security Testing"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install security testing dependencies"
	@echo "  make test          - Run comprehensive security assessment"
	@echo "  make basic         - Run basic OWASP security tests only"
	@echo "  make advanced      - Run advanced security tests with enhanced tools"
	@echo "  make check-tools   - Check which advanced tools are available"
	@echo "  make quick         - Run quick security check"
	@echo "  make report        - Open latest HTML security report"
	@echo "  make clean         - Clean up old reports and logs"
	@echo "  make help          - Show this help message"
	@echo ""

install:
	@echo "Installing security testing dependencies..."
	@echo "Using integrated requirements from main project..."
	pip install -r ../requirements.txt
	@echo "Dependencies installed successfully!"

test:
	@echo "Running comprehensive security assessment (basic + advanced)..."
	python run_advanced_security_tests.py

basic:
	@echo "Running basic OWASP security tests..."
	python run_advanced_security_tests.py basic

advanced:
	@echo "Running advanced security tests..."
	python run_advanced_security_tests.py advanced

check-tools:
	@echo "Checking available advanced security tools..."
	python run_advanced_security_tests.py check

quick:
	@echo "Running quick security check..."
	python -c "from OWASPCheck import OWASPSecurityTester; t = OWASPSecurityTester(); print('Quick test - check logs for details'); t.test_a01_broken_access_control()"

report:
	@echo "Opening latest security report..."
	@python -c "import glob, os, webbrowser; reports = glob.glob('owasp_security_report_*.html'); webbrowser.open('file://' + os.path.abspath(max(reports, key=os.path.getctime))) if reports else print('No reports found')"

clean:
	@echo "Cleaning up old security reports and logs..."
	rm -f owasp_security_report_*.json
	rm -f owasp_security_report_*.html
	rm -f security_summary_*.json
	rm -f security_test.log
	@echo "Cleanup completed!"

status:
	@echo "Security Testing Status:"
	@echo "======================="
	@echo "Reports found: $$(ls -1 owasp_security_report_*.html 2>/dev/null | wc -l)"
	@echo "Last report: $$(ls -t owasp_security_report_*.html 2>/dev/null | head -1 | xargs basename 2>/dev/null || echo 'None')"
	@echo "Log file: $$(test -f security_test.log && echo 'Present' || echo 'Not found')"