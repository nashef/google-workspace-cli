# Known Issues

## 1. Email search and get commands return incomplete metadata

**Status**: FIXED ✅
**Date**: 2025-11-18
**Fixed**: 2025-11-18

### Problem
The `gwc-mail search` and `gwc-mail get` commands are not returning complete email metadata.

### Current Behavior

#### Search command:
```bash
poetry run gwc-mail search "is:unread" --limit 5 --output llm
```

Returns only:
```
1. id: 19a97883e650e625
threadId: 19a5face9e34df43

2. id: 19a9777e42f396f0
threadId: 19a9777e42f396f0
...
```

#### Get command:
```bash
poetry run gwc-mail get 19a97883e650e625 --output llm
```

Returns:
```
1. from: Unknown
subject: (no subject)
body: [No body content]...
```

### Expected Behavior
- Search should return: from, subject, date, snippet for each email
- Get should return full email headers and body content

### Resolution
**Fixed by fetching full message details for each result.**

The issue was that `list` and `search` commands were only displaying the minimal metadata returned by the Gmail API's list endpoint. The fix fetches complete message details for each result using `get_message()` and `format_message_for_display()` to extract all headers and body content.

**Changes made:**
- Modified `gwc/email/__main__.py` lines 149-159 and 221-231
- Both `list` and `search` commands now fetch full message details
- Includes fallback to basic info if individual message fetch fails
- All metadata now displays correctly: from, to, subject, date, body, etc.

### Environment
- Poetry environment
- All 7 Google Workspace APIs enabled
- Authentication working (emails are found, just metadata missing)