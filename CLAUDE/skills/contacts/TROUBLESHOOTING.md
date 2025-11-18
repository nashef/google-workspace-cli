---
name: contacts-troubleshooting
description: Solutions to common Google Contacts CLI issues
---

# Google Contacts CLI - Troubleshooting Guide

Solutions to common problems and issues you might encounter.

## Authentication Issues

### "No valid authentication token found"

**Problem:** When running any command, you get:
```
No valid authentication token found
```

**Solution:**
```bash
poetry run gwc-people auth
```

This performs initial OAuth2 authentication:
1. Opens your browser
2. Ask you to sign in to Google
3. Asks you to approve access
4. Saves credentials locally

**Prevention:** Keep your token fresh by refreshing if errors occur:
```bash
poetry run gwc-people auth --refresh
```

---

### "Request had insufficient authentication scopes"

**Problem:** You get an error about missing permissions even after authenticating.

**Solution:**
Your token is old or missing permissions. Re-authenticate:

```bash
poetry run gwc-people auth
```

This will request updated permissions from Google.

---

### Credentials file not found

**Problem:** Error mentioning missing `credentials.json`

**Solution:**
This file should be set up by your admin. If you don't have it:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create or select a project
3. Enable the Google People API
4. Create OAuth2 credentials (Desktop application type)
5. Download the credentials JSON
6. Save to `~/.config/gwc/credentials.json`

---

## Search & Lookup Issues

### "Contact not found"

**Problem:** Command says contact doesn't exist when you know it does.

**Cause:** You're searching by name, which is prefix-based. If the contact's name doesn't match exactly, it won't be found.

**Solution:**
Use email instead for exact matches:

```bash
# This might not find them
poetry run gwc-people search "John Smith"

# This will find them if they exist
poetry run gwc-people get "john@example.com" --output llm
```

---

### Search returns too many results

**Problem:** Searching for "John" returns 30 unrelated contacts.

**Solution:**
Be more specific in your search:

```bash
# Too broad
poetry run gwc-people search "John" --limit 30

# More specific
poetry run gwc-people search "John Smith" --limit 10
poetry run gwc-people get "john.smith@example.com"
```

---

### Search returns no results when you expect matches

**Problem:** You search for something but get 0 results.

**Causes & Solutions:**

1. **Exact spelling/capitalization matters:**
   ```bash
   # Try different variations
   poetry run gwc-people search "Alice"
   poetry run gwc-people search "Alicia"
   poetry run gwc-people search "alice@"
   ```

2. **Prefix matching only:**
   ```bash
   # These work:
   poetry run gwc-people search "john@"     # Email prefix
   poetry run gwc-people search "John"      # Name prefix

   # These don't:
   poetry run gwc-people search "ohn"       # Middle of word
   poetry run gwc-people search "smith@"    # If first name is "John"
   ```

3. **Try exact email lookup:**
   ```bash
   poetry run gwc-people get "john@example.com"
   ```

---

## Performance Issues

### Search is very slow

**Problem:** Searches take several seconds on first use.

**Solution:**
Initialize and warm up the cache:

```bash
poetry run gwc-people cache sync
```

This downloads all contacts locally. Subsequent searches will be much faster.

**Prevention:**
Set up a daily cache sync (add to cron):
```bash
0 9 * * * cd ~/Jarvis/sagas/src/google-workspace-cli && poetry run gwc-people cache sync
```

---

### Cache is slow or out of sync

**Problem:** Cache `list` or `sync` operations are slow or showing stale data.

**Solution:**
Clear and rebuild the cache:

```bash
# Clear everything
poetry run gwc-people cache clear

# Rebuild from scratch
poetry run gwc-people cache sync
```

---

### Import is slow for large files

**Problem:** Importing thousands of contacts is slow.

**Cause:** Network latency and API rate limits.

**Solution:**
This is normal for large imports. The command will:
- Show progress by reporting created/failed counts
- Continue even if some rows fail
- Complete successfully at the end

Just be patient. For very large files (10,000+), this might take several minutes.

---

## Import/Export Issues

### Import fails with "Row X: Missing name and email"

**Problem:** Import stops or reports failures for certain rows.

**Cause:** CSV file has rows that don't meet minimum requirements.

**Solution:**
Each contact must have either a name OR email. Fix your CSV:

```csv
name,email,phone,organization
John Smith,john@example.com,555-1234,
,alice@example.com,,

# This will fail:
,,,
```

Ensure each row has at least name OR email.

---

### Import succeeds but some contacts don't appear

**Problem:** Import reports "Created: 10, Failed: 1" but you only see 9 new contacts.

**Solution:**
This is normal. The import results show what was created during this import. Check the error messages:

```bash
# The import command output will show:
# Import completed:
#   Created: 10
#   Failed: 1
#
# Errors:
#   Row 3: Failed to create contact: <error details>
```

The failed row will be listed with the error. You can manually fix and re-import just that row.

---

### CSV export has strange formatting

**Problem:** CSV file has extra quotes, commas in wrong places, or special characters are garbled.

**Solution:**
This is normal for CSV with special characters. Open in your spreadsheet app which handles escaping automatically:

```bash
# Export
poetry run gwc-people export ~/contacts.csv

# Open in Excel/Google Sheets
# They'll handle the escaping correctly
```

If you need clean data programmatically, use JSON export instead:

```bash
poetry run gwc-people export ~/contacts.json --format json
```

---

### Import doesn't update existing contacts

**Problem:** You import a CSV with an updated email, but the contact's old email still shows.

**Cause:** Import always creates NEW contacts. It doesn't update existing ones.

**Solution:**
For updates, use the `update` command:

```bash
poetry run gwc-people update "old@example.com" --email "new@example.com"
```

Or manually update in Google Contacts, then sync the cache:

```bash
poetry run gwc-people cache sync --full
```

---

## Group Issues

### "Group not found" error

**Problem:** Command says group doesn't exist.

**Solution:**
Check that the group name is correct (case-sensitive):

```bash
# See all groups
poetry run gwc-people groups list --output llm

# Then use exact name
poetry run gwc-people groups get "Engineering Team"
```

---

### Can't add member to group

**Problem:** `add-member` command fails even though contact exists.

**Causes & Solutions:**

1. **Wrong email format:**
   ```bash
   # Make sure email is valid
   poetry run gwc-people groups add-member "Team" "john@example.com"

   # Not like this
   poetry run gwc-people groups add-member "Team" "John"
   ```

2. **Contact doesn't exist:**
   ```bash
   # Verify contact first
   poetry run gwc-people get "john@example.com"

   # If not found, create it
   poetry run gwc-people create --name "John Smith" --email "john@example.com"

   # Then add to group
   poetry run gwc-people groups add-member "Team" "john@example.com"
   ```

---

### "Duplicate group name" error

**Problem:** Group creation fails saying name already exists.

**Cause:** Group with that name already exists.

**Solution:**
Choose a different name, or rename the existing group:

```bash
# List existing groups
poetry run gwc-people groups list

# Rename if it exists
poetry run gwc-people groups update "Old Name" --name "New Name"
```

---

## Workspace Directory Issues (Enterprise)

### "Directory not available" error

**Problem:** Directory search/list fails with permission error.

**Cause:** Your account doesn't have Workspace directory enabled, or admin hasn't configured sharing.

**Solution:**

1. **Check account type:**
   ```bash
   # This only works for Google Workspace accounts
   # If using personal Google account, skip this feature
   ```

2. **Ask your admin to enable:**
   - Enable external contact/profile sharing
   - Grant you directory access

3. **Verify configuration:**
   After admin enables, try again:
   ```bash
   poetry run gwc-people directory search "Alice" --output llm
   ```

---

## Cache Issues

### Cache takes up too much space

**Problem:** The cache database (`~/.config/gwc/contacts.db`) is large.

**Solution:**

1. **Check size:**
   ```bash
   ls -lh ~/.config/gwc/contacts.db
   ```

2. **Clear if needed:**
   ```bash
   poetry run gwc-people cache clear
   ```

3. **Recreate:**
   ```bash
   poetry run gwc-people cache sync
   ```

Typical size for 1000 contacts: ~100-200KB

---

### Sync token expired

**Problem:** Cache sync says "Full sync" when it should be incremental.

**Cause:** Sync token expired (can happen if cache is old).

**Solution:**
Just let it run. When token expires, a full sync is required:

```bash
poetry run gwc-people cache sync
```

This will download all contacts again and get a new sync token.

---

## Output Format Issues

### Output is hard to read

**Problem:** Default tab-separated output is hard to parse visually.

**Solution:**
Use human-readable format:

```bash
# Hard to read (default)
poetry run gwc-people list

# Easy to read
poetry run gwc-people list --output llm
```

---

### Can't parse JSON output

**Problem:** JSON output has unexpected format or missing fields.

**Solution:**

1. **Check what fields are available:**
   ```bash
   poetry run gwc-people get "email@example.com" --output json | jq 'keys'
   ```

2. **Use appropriate query for your needs:**
   ```bash
   # Get all emails
   poetry run gwc-people list --output json | jq -r '.[].email'

   # Get names
   poetry run gwc-people list --output json | jq -r '.[].displayName'
   ```

3. **If fields missing:** Some contacts might not have all fields filled in
   ```bash
   # Filter for contacts with email
   poetry run gwc-people list --output json | jq -r '.[] | select(.email != null) | .email'
   ```

---

## Permission Issues

### "Permission denied" for files

**Problem:** Can't write export file or read import file.

**Cause:** Wrong file permissions or directory.

**Solution:**

```bash
# Make sure you have write permission in the directory
ls -ld ~/

# Use home directory expansion
poetry run gwc-people export ~/my_contacts.csv

# Not absolute paths unless necessary
# poetry run gwc-people export /root/contacts.csv  # Might fail

# Or use current directory
poetry run gwc-people export ./contacts.csv
```

---

## Network Issues

### "Network error" or "Connection timeout"

**Problem:** Commands fail with network errors.

**Cause:** Network connectivity or API server issues.

**Solutions:**

1. **Check your network:**
   ```bash
   ping google.com
   ```

2. **Try again later:**
   Sometimes Google's API has temporary issues. Wait a minute and retry.

3. **Check API status:**
   - Visit [Google Cloud Status](https://status.cloud.google.com/)
   - Look for People API incidents

4. **Verify credentials:**
   ```bash
   poetry run gwc-people auth --refresh
   ```

---

## Still Stuck?

### Get detailed error information

Add extra debugging:

```bash
# See full error details
poetry run gwc-people search "test" -v

# Or check command help
poetry run gwc-people search --help
```

### Check documentation

1. **Quick start:** [QUICK_START.md](QUICK_START.md)
2. **Common tasks:** [SKILL.md](SKILL.md)
3. **Complete reference:** [REFERENCE.md](REFERENCE.md)
4. **Full guide:** [../../README_PEOPLE.md](../../README_PEOPLE.md)

### Get help from command

Every command has built-in help:

```bash
poetry run gwc-people export --help
poetry run gwc-people groups --help
poetry run gwc-people cache --help
```

---

## Common Workflows for Troubleshooting

### "Reset everything and start fresh"

```bash
# Clear cache
poetry run gwc-people cache clear

# Re-authenticate
poetry run gwc-people auth

# Rebuild cache
poetry run gwc-people cache sync

# Test with simple search
poetry run gwc-people search "your_name" --output llm
```

### "Verify setup is working"

```bash
# 1. Check authentication
poetry run gwc-people auth --refresh

# 2. Try a simple search
poetry run gwc-people search "test" --limit 5 --output llm

# 3. Check cache
poetry run gwc-people cache list --limit 3

# 4. Export to verify
poetry run gwc-people export ~/test_export.csv

# 5. Try import
poetry run gwc-people import ~/test_export.csv
```

---

## Reporting Issues

If you've tried troubleshooting and still have problems:

1. **Collect information:**
   - What command did you run?
   - What was the exact error message?
   - When did it start happening?

2. **Share with support:**
   - Error message
   - Command you ran
   - Environment (OS, Python version)
   - Your steps to reproduce

3. **Check existing issues:**
   - See if others had the same problem
   - Try their solutions

---

**Last Resort:** Start completely fresh:

```bash
# Remove all local config
rm -rf ~/.config/gwc

# Re-authenticate
poetry run gwc-people auth

# Verify it works
poetry run gwc-people list --output llm
```

This will reset everything to factory defaults.

---

Still need help? Check [INDEX.md](INDEX.md) for all available documentation.
