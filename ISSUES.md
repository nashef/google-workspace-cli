# Known Issues

## 1. Email search and get commands return incomplete metadata

**Status**: Open
**Date**: 2025-11-18

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

### Possible Fix
The operations.py file likely needs to:
1. Request additional metadata fields in the search query
2. Parse the payload correctly to extract headers and body

### Environment
- Poetry environment
- All 7 Google Workspace APIs enabled
- Authentication working (emails are found, just metadata missing)