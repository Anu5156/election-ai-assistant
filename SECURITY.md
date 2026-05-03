# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of CivicGuide AI seriously. If you believe you have found a security vulnerability, please report it to us by opening a confidential GitHub Issue or contacting the maintainers directly.

### Our Security Measures:
- **Input Sanitization:** Multi-layer regex-based filtering for all user inputs.
- **Rate Limiting:** Session-based cooldowns on all AI and Maps API calls.
- **Data Privacy:** Minimal PII collection; all geospatial data is processed in-memory.
- **Secure Headers:** Implementation of CSP and XSS protection headers.
