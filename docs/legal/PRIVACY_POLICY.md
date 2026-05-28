# Novahiz OS — Privacy Policy (RGPD/GDPR Compliant)

**Version:** 1.0  
**Last Updated:** 2026-05-27  
**Effective Date:** 2026-05-27

---

## 1. Data Controller

**Novahiz OS**  
Contact: privacy@novahiz-os.local  
Address: Local installation (user-controlled)

---

## 2. Data We Collect

### 2.1 Usage Data (Opt-in Only)

| Data Type | Purpose | Retention | Legal Basis |
|-----------|---------|-----------|-------------|
| Model usage metrics (tier, tokens) | Service improvement | 90 days | Consent (Art. 6.1a) |
| Execution logs | Debugging, analytics | 30 days | Legitimate interest (Art. 6.1f) |
| Error reports | Bug fixes | 90 days | Legitimate interest (Art. 6.1f) |

### 2.2 Data NOT Collected

- ❌ Personal identifiers (name, email, IP)
- ❌ Payment information
- ❌ Browsing history
- ❌ Location data
- ❌ Biometric data

---

## 3. Legal Basis for Processing

| Processing Activity | Legal Basis (GDPR) |
|---------------------|-------------------|
| Core functionality | Contract performance (Art. 6.1b) |
| Usage analytics | Consent (Art. 6.1a) |
| Error tracking | Legitimate interest (Art. 6.1f) |
| Security monitoring | Legitimate interest (Art. 6.1f) |

---

## 4. Your Rights (GDPR Chapter 3)

You have the right to:

| Right | Article | How to Exercise |
|-------|---------|-----------------|
| Access | Art. 15 | Request data export |
| Rectification | Art. 16 | Request correction |
| Erasure | Art. 17 | Request deletion |
| Portability | Art. 20 | Request data export (JSON) |
| Object | Art. 21 | Opt-out of analytics |
| Restrict | Art. 18 | Request processing pause |

**Contact:** privacy@novahiz-os.local  
**Response Time:** 30 days maximum

---

## 5. Data Storage & Security

### 5.1 Storage Location

- **Primary:** Local machine (`~/.opencode/`)
- **Backups:** Local (`~/.opencode-backups/`)
- **Cloud:** None (unless user configures external backup)

### 5.2 Security Measures

| Measure | Implementation |
|---------|---------------|
| Encryption at rest | Optional (user-configured) |
| Encryption in transit | TLS 1.3 (OpenRouter API) |
| Access control | File permissions (600/700) |
| Audit logging | Enabled by default |
| Data minimization | Only essential data collected |

---

## 6. Data Sharing

**We do NOT sell or share your data.**

| Third Party | Purpose | Data Shared | Safeguards |
|-------------|---------|-------------|------------|
| OpenRouter | LLM inference | Task prompts only | TLS encryption |
| GitHub (optional) | Updates | None | User opt-in |

---

## 7. International Transfers

| Transfer | Mechanism |
|----------|-----------|
| OpenRouter API | Standard Contractual Clauses (SCC) |
| Cloud backups (if enabled) | Adequacy decision or SCC |

---

## 8. Data Retention

| Data Type | Retention Period | Deletion Method |
|-----------|------------------|-----------------|
| Execution logs | 30 days | Automatic rotation |
| Usage metrics | 90 days | Automatic cleanup |
| Configuration | Until uninstall | Manual deletion |
| Backups | 7 days | Automatic rotation |

---

## 9. Cookies & Tracking

**Novahiz OS does NOT use:**
- ❌ Cookies
- ❌ Tracking pixels
- ❌ Third-party analytics
- ❌ Fingerprinting

---

## 10. Children's Privacy

Novahiz OS is **not intended for children under 16**.  
We do not knowingly collect data from children.

---

## 11. Changes to This Policy

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-27 | Initial version |

**Notification:** Users will be notified of material changes via in-app notice.

---

## 12. Supervisory Authority

If you believe our processing violates GDPR, you may lodge a complaint with your local Data Protection Authority.

**EU Users:** CNIL (France), ICO (UK), etc.

---

## 13. Consent Management

### 13.1 Default Settings

| Feature | Default | User Control |
|---------|---------|--------------|
| Usage analytics | ❌ Disabled | Settings → Privacy |
| Error reporting | ❌ Disabled | Settings → Privacy |
| Log retention | 30 days | Configurable |

### 13.2 How to Withdraw Consent

```bash
# Disable telemetry
echo '{"telemetry": {"enabled": false}}' > ~/.opencode/config/privacy.json

# Delete all usage data
rm -rf ~/.opencode/memory/00_Core/metrics.json
rm -rf ~/.opencode/logs/
```

---

## 14. Data Processing Agreement (DPA)

For enterprise users, a DPA is available upon request.  
Contact: legal@novahiz-os.local

---

## 15. Contact

**Privacy Questions:** privacy@novahiz-os.local  
**Legal Questions:** legal@novahiz-os.local  
**Security Issues:** security@novahiz-os.local

---

*This policy complies with:*
- ✅ GDPR (EU) 2016/679
- ✅ UK GDPR
- ✅ CCPA/CPRA (California)
- ✅ Swiss DSG
