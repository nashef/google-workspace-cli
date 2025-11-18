---
name: email-advanced
description: Advanced Gmail features (filters, signatures, auto-responders, templates)
---

# Advanced Gmail Features

For basic tasks, see **SKILL.md**. This document covers Phase 4 advanced features.

## Filters

Automatically organize incoming mail based on criteria.

**Create filter:**
```bash
poetry run gwc-email filters create "Archive spam" --from "spam@example.com" --action archive
poetry run gwc-email filters create "Work mail" --to "work@example.com" --action add-label --label Work
poetry run gwc-email filters create "Attachments" --has-attachment --action add-label --label Attachments
```

**Actions:** `archive`, `delete`, `mark-read`, `add-label`, `skip-inbox`

**List/Get/Delete:**
```bash
poetry run gwc-email filters list --output llm
poetry run gwc-email filters get filter_id --output json
poetry run gwc-email filters delete filter_id
```

## Signatures

Email signatures appended to outgoing messages.

```bash
poetry run gwc-email signatures list --output llm
poetry run gwc-email signatures get user@example.com --output json
poetry run gwc-email signatures update user@example.com "<p>Best regards,<br/>John</p>"
```

## Auto-Responders

Automatic replies while away (vacation messages).

```bash
# Enable now
poetry run gwc-email auto-responder create --subject "Out of Office" --message "I'm away"

# With date range
poetry run gwc-email auto-responder create \
  --subject "Out of Office" \
  --message "Back on Dec 15" \
  --start-date 2025-12-01 \
  --end-date 2025-12-15

# Check/disable
poetry run gwc-email auto-responder get --output json
poetry run gwc-email auto-responder disable
```

## Templates

Reusable message patterns.

```bash
# Create template
poetry run gwc-email templates create "Weekly Report" \
  --subject "Weekly Update" \
  --body "<p>Week of...</p><ul><li>Item 1</li></ul>"

# List/Get/Delete
poetry run gwc-email templates list --output llm
poetry run gwc-email templates get template123 --output json
poetry run gwc-email templates delete template123

# Use template (creates draft)
poetry run gwc-email templates use template123 --to alice@example.com
poetry run gwc-email templates use template123 --to alice@example.com --cc boss@example.com
```

## Command Reference

| Command | Purpose |
|---------|---------|
| `filters create` | Create message filter |
| `filters list` | List all filters |
| `filters get` | Get filter details |
| `filters delete` | Delete filter |
| `signatures list` | List signatures |
| `signatures get` | Get signature for address |
| `signatures update` | Update signature |
| `auto-responder create` | Enable auto-responder |
| `auto-responder get` | Get auto-responder settings |
| `auto-responder disable` | Disable auto-responder |
| `templates create` | Create template |
| `templates list` | List templates |
| `templates get` | Get template details |
| `templates delete` | Delete template |
| `templates use` | Create draft from template |

See **REFERENCE.md** for complete option documentation.
