"""Google People API operations."""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..shared.auth import get_credentials, PEOPLE_SCOPES
from ..shared.exceptions import APIError, ValidationError
from .cache import ContactCache


def build_people_service():
    """Build and return People API service object."""
    creds = get_credentials(scopes=PEOPLE_SCOPES)
    return build("people", "v1", credentials=creds)


def search_contacts(query: str, page_size: int = 10) -> List[Dict[str, Any]]:
    """Search for contacts by name, email, phone, or organization.

    Args:
        query: Search query (required, not empty)
        page_size: Number of results to return (default: 10, max: 30)

    Returns:
        List of matching contacts with names and email addresses

    Raises:
        ValidationError: If query is empty or page_size is invalid
        APIError: If API call fails
    """
    if not query or not query.strip():
        raise ValidationError("Search query cannot be empty")

    if page_size < 1 or page_size > 30:
        raise ValidationError("Page size must be between 1 and 30")

    service = build_people_service()

    try:
        results = service.people().searchContacts(
            query=query.strip(),
            pageSize=page_size,
            readMask="names,emailAddresses,phoneNumbers,organizations"
        ).execute()

        return results.get('results', [])
    except HttpError as e:
        raise APIError(f"Failed to search contacts: {e}")


def get_contact(resource_name_or_email: str, fields: Optional[str] = None) -> Dict[str, Any]:
    """Get contact details by resource name or email.

    Args:
        resource_name_or_email: Contact resource name (people/c...) or email address
        fields: Field mask for response. If None, returns minimal fields:
                names,emailAddresses,phoneNumbers,organizations

    Returns:
        Contact object with requested fields

    Raises:
        ValidationError: If resource name/email is invalid
        APIError: If API call fails or contact not found
    """
    if not resource_name_or_email or not resource_name_or_email.strip():
        raise ValidationError("Resource name or email cannot be empty")

    service = build_people_service()
    resource_name = resource_name_or_email.strip()

    # If it's an email, search for it first
    if "@" in resource_name and not resource_name.startswith("people/"):
        try:
            results = search_contacts(resource_name, page_size=1)
            if not results:
                raise APIError(f"Contact not found: {resource_name}")
            # Get the full resource name from search result
            resource_name = results[0]['person']['resourceName']
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Failed to lookup contact by email: {e}")

    if not fields:
        fields = "names,emailAddresses,phoneNumbers,organizations"

    try:
        result = service.people().get(
            resourceName=resource_name,
            personFields=fields
        ).execute()
        return result
    except HttpError as e:
        if e.resp.status == 404:
            raise APIError(f"Contact not found: {resource_name}")
        raise APIError(f"Failed to get contact: {e}")


def list_contacts(
    page_size: int = 100,
    sort_order: Optional[str] = None,
    page_token: Optional[str] = None
) -> Dict[str, Any]:
    """List authenticated user's contacts.

    Args:
        page_size: Number of results per page (default: 100, max: 1000)
        sort_order: Sort order - one of:
                   LAST_MODIFIED_ASCENDING, LAST_MODIFIED_DESCENDING,
                   FIRST_NAME_ASCENDING, LAST_NAME_ASCENDING
        page_token: Token for pagination

    Returns:
        Dict with 'connections' list and 'nextPageToken' if more results exist

    Raises:
        ValidationError: If parameters are invalid
        APIError: If API call fails
    """
    if page_size < 1 or page_size > 1000:
        raise ValidationError("Page size must be between 1 and 1000")

    valid_sort_orders = {
        "LAST_MODIFIED_ASCENDING",
        "LAST_MODIFIED_DESCENDING",
        "FIRST_NAME_ASCENDING",
        "LAST_NAME_ASCENDING",
    }

    if sort_order and sort_order not in valid_sort_orders:
        raise ValidationError(
            f"Invalid sort order: {sort_order}. "
            f"Valid options: {', '.join(valid_sort_orders)}"
        )

    service = build_people_service()

    kwargs = {
        'resourceName': 'people/me',
        'pageSize': page_size,
        'personFields': 'names,emailAddresses,phoneNumbers,organizations,metadata'
    }

    if sort_order:
        kwargs['sortOrder'] = sort_order

    if page_token:
        kwargs['pageToken'] = page_token

    try:
        result = service.people().connections().list(**kwargs).execute()
        return result
    except HttpError as e:
        raise APIError(f"Failed to list contacts: {e}")


def get_contact_email(resource_name_or_email: str) -> str:
    """Get primary email address for a contact.

    Args:
        resource_name_or_email: Contact resource name or email

    Returns:
        Email address string

    Raises:
        ValidationError: If no email found or invalid input
        APIError: If API call fails
    """
    contact = get_contact(resource_name_or_email, fields="emailAddresses")
    emails = contact.get('emailAddresses', [])

    if not emails:
        raise ValidationError(f"No email address found for contact")

    # Return primary email if marked, otherwise first email
    for email in emails:
        if email.get('metadata', {}).get('primary'):
            return email.get('value')

    return emails[0].get('value')


def get_contact_name(resource_name_or_email: str) -> str:
    """Get display name for a contact.

    Args:
        resource_name_or_email: Contact resource name or email

    Returns:
        Display name string

    Raises:
        ValidationError: If no name found or invalid input
        APIError: If API call fails
    """
    contact = get_contact(resource_name_or_email, fields="names")
    names = contact.get('names', [])

    if not names:
        raise ValidationError(f"No name found for contact")

    # Return primary name if marked, otherwise first name
    for name in names:
        if name.get('metadata', {}).get('primary'):
            return name.get('displayName')

    return names[0].get('displayName')


def create_contact(
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    organization: Optional[str] = None,
    address: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new contact.

    Args:
        name: Contact display name (at least name or email required)
        email: Email address
        phone: Phone number
        organization: Organization name
        address: Physical address

    Returns:
        Created contact object with resourceName

    Raises:
        ValidationError: If required fields missing or invalid
        APIError: If API call fails
    """
    if not name and not email:
        raise ValidationError("At least name or email is required to create a contact")

    service = build_people_service()

    # Build contact object
    contact = {}

    if name:
        contact['names'] = [{'displayName': name}]

    if email:
        contact['emailAddresses'] = [{'value': email}]

    if phone:
        contact['phoneNumbers'] = [{'value': phone}]

    if organization:
        contact['organizations'] = [{'name': organization}]

    if address:
        contact['addresses'] = [{'formattedValue': address}]

    try:
        result = service.people().createContact(body=contact).execute()
        return result
    except HttpError as e:
        if e.resp.status == 409:
            raise ValidationError(f"Contact with this email already exists")
        raise APIError(f"Failed to create contact: {e}")


def create_contact_batch(contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create multiple contacts in a batch operation.

    Args:
        contacts: List of contact dicts (each can have name, email, phone, organization, address)

    Returns:
        List of created contacts with resourceNames

    Raises:
        ValidationError: If contacts list is empty or invalid
        APIError: If API call fails
    """
    if not contacts:
        raise ValidationError("Contacts list cannot be empty")

    if len(contacts) > 1000:
        raise ValidationError("Maximum 1000 contacts per batch")

    service = build_people_service()

    # Build batch request
    requests = []
    for contact_data in contacts:
        contact = {}

        if contact_data.get('name'):
            contact['names'] = [{'displayName': contact_data['name']}]

        if contact_data.get('email'):
            contact['emailAddresses'] = [{'value': contact_data['email']}]

        if contact_data.get('phone'):
            contact['phoneNumbers'] = [{'value': contact_data['phone']}]

        if contact_data.get('organization'):
            contact['organizations'] = [{'name': contact_data['organization']}]

        if contact_data.get('address'):
            contact['addresses'] = [{'formattedValue': contact_data['address']}]

        requests.append({'createContact': {'contactToCreate': contact}})

    try:
        result = service.people().batchCreateContacts(body={'requests': requests}).execute()
        return result.get('responses', [])
    except HttpError as e:
        raise APIError(f"Failed to batch create contacts: {e}")


def update_contact(
    resource_name_or_email: str,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    organization: Optional[str] = None,
    address: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing contact.

    Args:
        resource_name_or_email: Contact resource name or email
        name: New display name
        email: New email address
        phone: New phone number
        organization: New organization name
        address: New physical address

    Returns:
        Updated contact object

    Raises:
        ValidationError: If contact not found or no fields to update
        APIError: If API call fails or etag conflict
    """
    # Get current contact with etag
    current = get_contact(resource_name_or_email, fields="names,emailAddresses,phoneNumbers,organizations,addresses")
    resource_name = current.get('resourceName')
    etag = current.get('etag')

    if not resource_name:
        raise APIError("Could not determine resource name for contact")

    # Build update object with only specified fields
    update_obj = {
        'resourceName': resource_name,
        'etag': etag
    }

    if name is not None:
        update_obj['names'] = [{'displayName': name}]

    if email is not None:
        update_obj['emailAddresses'] = [{'value': email}]

    if phone is not None:
        update_obj['phoneNumbers'] = [{'value': phone}]

    if organization is not None:
        update_obj['organizations'] = [{'name': organization}]

    if address is not None:
        update_obj['addresses'] = [{'formattedValue': address}]

    # Check that at least one field was updated
    if len(update_obj) <= 2:  # Only has resourceName and etag
        raise ValidationError("No fields to update")

    service = build_people_service()

    # Determine which fields are being updated (exclude resourceName and etag)
    update_fields = [k for k in update_obj.keys() if k not in ('resourceName', 'etag')]
    update_mask = ','.join(update_fields)

    try:
        result = service.people().updateContact(
            resourceName=resource_name,
            body=update_obj,
            updatePersonFields=update_mask
        ).execute()
        return result
    except HttpError as e:
        if e.resp.status == 409:
            raise APIError(
                f"Contact was modified by someone else. "
                f"Fetch the latest version and try again."
            )
        raise APIError(f"Failed to update contact: {e}")


def update_contact_batch(updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Update multiple contacts in a batch operation.

    Args:
        updates: List of update dicts (each must have 'email_or_id' and fields to update)

    Returns:
        List of update responses

    Raises:
        ValidationError: If updates list is empty or invalid
        APIError: If API call fails
    """
    if not updates:
        raise ValidationError("Updates list cannot be empty")

    if len(updates) > 1000:
        raise ValidationError("Maximum 1000 contacts per batch")

    service = build_people_service()

    requests = []
    for update_data in updates:
        email_or_id = update_data.get('email_or_id')
        if not email_or_id:
            raise ValidationError("Each update must have 'email_or_id'")

        # Get current contact to get resource name and etag
        current = get_contact(email_or_id)
        resource_name = current.get('resourceName')
        etag = current.get('etag')

        if not resource_name:
            continue  # Skip if can't find resource name

        # Build update object with resourceName and etag
        update_obj = {
            'resourceName': resource_name,
            'etag': etag
        }
        fields_to_update = []

        if update_data.get('name') is not None:
            update_obj['names'] = [{'displayName': update_data['name']}]
            fields_to_update.append('names')

        if update_data.get('email') is not None:
            update_obj['emailAddresses'] = [{'value': update_data['email']}]
            fields_to_update.append('emailAddresses')

        if update_data.get('phone') is not None:
            update_obj['phoneNumbers'] = [{'value': update_data['phone']}]
            fields_to_update.append('phoneNumbers')

        if update_data.get('organization') is not None:
            update_obj['organizations'] = [{'name': update_data['organization']}]
            fields_to_update.append('organizations')

        if update_data.get('address') is not None:
            update_obj['addresses'] = [{'formattedValue': update_data['address']}]
            fields_to_update.append('addresses')

        if fields_to_update:
            requests.append({
                'updateContact': {
                    'contact': update_obj,
                    'updatePersonFields': ','.join(fields_to_update)
                }
            })

    if not requests:
        raise ValidationError("No valid updates to process")

    try:
        result = service.people().batchUpdateContacts(body={'requests': requests}).execute()
        return result.get('responses', [])
    except HttpError as e:
        raise APIError(f"Failed to batch update contacts: {e}")


def delete_contact(resource_name_or_email: str) -> None:
    """Delete a contact.

    Args:
        resource_name_or_email: Contact resource name or email

    Raises:
        ValidationError: If contact not found
        APIError: If API call fails
    """
    # Get resource name if email provided
    if "@" in resource_name_or_email and not resource_name_or_email.startswith("people/"):
        contact = get_contact(resource_name_or_email, fields="names")
        resource_name = contact.get('resourceName')
    else:
        resource_name = resource_name_or_email.strip()

    if not resource_name:
        raise ValidationError("Could not determine resource name for contact")

    service = build_people_service()

    try:
        service.people().deleteContact(resourceName=resource_name).execute()
    except HttpError as e:
        if e.resp.status == 404:
            raise ValidationError(f"Contact not found")
        raise APIError(f"Failed to delete contact: {e}")


def delete_contact_batch(resource_names: List[str]) -> List[Dict[str, Any]]:
    """Delete multiple contacts in a batch operation.

    Args:
        resource_names: List of contact resource names

    Returns:
        List of delete responses

    Raises:
        ValidationError: If resource_names is empty
        APIError: If API call fails
    """
    if not resource_names:
        raise ValidationError("Resource names list cannot be empty")

    if len(resource_names) > 1000:
        raise ValidationError("Maximum 1000 contacts per batch")

    service = build_people_service()

    requests = [
        {'deleteContact': {'resourceName': name}}
        for name in resource_names
    ]

    try:
        result = service.people().batchDeleteContacts(body={'requests': requests}).execute()
        return result.get('responses', [])
    except HttpError as e:
        raise APIError(f"Failed to batch delete contacts: {e}")


def sync_contacts(cache: Optional[ContactCache] = None, force_full: bool = False) -> Dict[str, Any]:
    """Sync contacts from Google using sync tokens for incremental updates.

    Args:
        cache: ContactCache instance. If None, creates a new one.
        force_full: If True, perform full sync instead of incremental

    Returns:
        Dict with sync results (contacts_synced, sync_token, full_sync)

    Raises:
        APIError: If sync fails
    """
    if cache is None:
        cache = ContactCache()

    service = build_people_service()

    # Get last sync token if not forcing full sync
    sync_token = None if force_full else cache.get_sync_token()
    is_incremental = sync_token is not None

    try:
        # Prepare request kwargs
        kwargs = {
            'resourceName': 'people/me',
            'personFields': 'names,emailAddresses,phoneNumbers,organizations,metadata'
        }

        if sync_token:
            kwargs['syncToken'] = sync_token
        else:
            # For full sync, use maxDeletions to get deletion info
            kwargs['requestSyncToken'] = True

        result = service.people().connections().list(**kwargs).execute()

        # Cache the contacts
        connections = result.get('connections', [])
        cache.cache_contacts(connections)

        # Update sync token if available
        # nextSyncToken is returned when requestSyncToken=True or when using syncToken
        next_sync_token = result.get('nextSyncToken')
        if next_sync_token:
            cache.set_sync_token(next_sync_token)

        return {
            'contacts_synced': len(connections),
            'sync_token': next_sync_token,
            'full_sync': not is_incremental,
            'has_more': 'nextPageToken' in result
        }

    except HttpError as e:
        if e.resp.status == 410:
            # Sync token expired, fall back to full sync
            if not force_full:
                return sync_contacts(cache=cache, force_full=True)
        raise APIError(f"Failed to sync contacts: {e}")


# ============================================================================
# Contact Groups Operations
# ============================================================================

def list_contact_groups() -> List[Dict[str, Any]]:
    """List all contact groups (user-created and system groups).

    Returns:
        List of contact group objects

    Raises:
        APIError: If API call fails
    """
    service = build_people_service()

    try:
        result = service.contactGroups().list().execute()
        return result.get('contactGroups', [])
    except HttpError as e:
        raise APIError(f"Failed to list contact groups: {e}")


def get_contact_group(group_id: str) -> Dict[str, Any]:
    """Get details of a specific contact group.

    Args:
        group_id: Group resource ID (e.g., contactGroups/123456)

    Returns:
        Contact group object with member list

    Raises:
        ValidationError: If group_id is invalid
        APIError: If API call fails or group not found
    """
    if not group_id or not group_id.strip():
        raise ValidationError("Group ID cannot be empty")

    service = build_people_service()

    try:
        result = service.contactGroups().get(
            resourceName=group_id,
            maxMembers=10000
        ).execute()
        return result
    except HttpError as e:
        if e.resp.status == 404:
            raise ValidationError(f"Contact group not found: {group_id}")
        raise APIError(f"Failed to get contact group: {e}")


def create_contact_group(name: str) -> Dict[str, Any]:
    """Create a new contact group.

    Args:
        name: Group name (must be unique)

    Returns:
        Created contact group object with resource name

    Raises:
        ValidationError: If name is invalid or already exists
        APIError: If API call fails
    """
    if not name or not name.strip():
        raise ValidationError("Group name cannot be empty")

    service = build_people_service()

    try:
        result = service.contactGroups().create(
            body={'contactGroup': {'name': name.strip()}}
        ).execute()
        return result
    except HttpError as e:
        if e.resp.status == 409:
            raise ValidationError(f"Contact group '{name}' already exists")
        raise APIError(f"Failed to create contact group: {e}")


def update_contact_group(group_id: str, name: str) -> Dict[str, Any]:
    """Update a contact group's name.

    Args:
        group_id: Group resource ID
        name: New group name

    Returns:
        Updated contact group object

    Raises:
        ValidationError: If parameters invalid
        APIError: If API call fails
    """
    if not group_id or not group_id.strip():
        raise ValidationError("Group ID cannot be empty")

    if not name or not name.strip():
        raise ValidationError("Group name cannot be empty")

    service = build_people_service()

    try:
        # Get current group to get etag
        current = service.contactGroups().get(resourceName=group_id).execute()
        etag = current.get('etag')

        result = service.contactGroups().update(
            resourceName=group_id,
            body={
                'contactGroup': {
                    'name': name.strip(),
                    'etag': etag
                }
            }
        ).execute()
        return result
    except HttpError as e:
        if e.resp.status == 404:
            raise ValidationError(f"Contact group not found: {group_id}")
        if e.resp.status == 409:
            raise ValidationError(f"Contact group '{name}' already exists")
        raise APIError(f"Failed to update contact group: {e}")


def delete_contact_group(group_id: str) -> None:
    """Delete a contact group.

    Note: System groups cannot be deleted.

    Args:
        group_id: Group resource ID

    Raises:
        ValidationError: If group not found or is a system group
        APIError: If API call fails
    """
    if not group_id or not group_id.strip():
        raise ValidationError("Group ID cannot be empty")

    service = build_people_service()

    try:
        service.contactGroups().delete(resourceName=group_id).execute()
    except HttpError as e:
        if e.resp.status == 404:
            raise ValidationError(f"Contact group not found: {group_id}")
        if e.resp.status == 400:
            raise ValidationError(f"Cannot delete system group")
        raise APIError(f"Failed to delete contact group: {e}")


def add_group_member(group_id: str, resource_name: str) -> None:
    """Add a single member to a contact group.

    Args:
        group_id: Group resource ID
        resource_name: Contact resource name (people/c...)

    Raises:
        ValidationError: If parameters invalid
        APIError: If API call fails
    """
    if not group_id or not group_id.strip():
        raise ValidationError("Group ID cannot be empty")

    if not resource_name or not resource_name.strip():
        raise ValidationError("Contact resource name cannot be empty")

    service = build_people_service()

    try:
        service.contactGroups().members().modify(
            resourceName=group_id,
            body={'resourceNamesToAdd': [resource_name.strip()]}
        ).execute()
    except HttpError as e:
        if e.resp.status == 404:
            raise ValidationError(f"Group or contact not found")
        raise APIError(f"Failed to add group member: {e}")


def add_group_members(group_id: str, resource_names: List[str]) -> None:
    """Add multiple members to a contact group.

    Args:
        group_id: Group resource ID
        resource_names: List of contact resource names

    Raises:
        ValidationError: If parameters invalid
        APIError: If API call fails
    """
    if not group_id or not group_id.strip():
        raise ValidationError("Group ID cannot be empty")

    if not resource_names:
        raise ValidationError("Resource names list cannot be empty")

    service = build_people_service()

    try:
        service.contactGroups().members().modify(
            resourceName=group_id,
            body={'resourceNamesToAdd': resource_names}
        ).execute()
    except HttpError as e:
        if e.resp.status == 404:
            raise ValidationError(f"Group or contact not found")
        raise APIError(f"Failed to add group members: {e}")


def remove_group_member(group_id: str, resource_name: str) -> None:
    """Remove a member from a contact group.

    Args:
        group_id: Group resource ID
        resource_name: Contact resource name (people/c...)

    Raises:
        ValidationError: If parameters invalid
        APIError: If API call fails
    """
    if not group_id or not group_id.strip():
        raise ValidationError("Group ID cannot be empty")

    if not resource_name or not resource_name.strip():
        raise ValidationError("Contact resource name cannot be empty")

    service = build_people_service()

    try:
        service.contactGroups().members().modify(
            resourceName=group_id,
            body={'resourceNamesToRemove': [resource_name.strip()]}
        ).execute()
    except HttpError as e:
        if e.resp.status == 404:
            raise ValidationError(f"Group or contact not found")
        raise APIError(f"Failed to remove group member: {e}")


def batch_add_to_group(group_id: str, emails_or_ids: List[str]) -> Dict[str, Any]:
    """Add multiple contacts to a group by email or resource name.

    This is a convenience function that looks up contacts by email if needed.

    Args:
        group_id: Group resource ID
        emails_or_ids: List of emails or resource names

    Returns:
        Result dict with added_count

    Raises:
        APIError: If API call fails
    """
    if not emails_or_ids:
        raise ValidationError("Emails/IDs list cannot be empty")

    # Convert emails to resource names if needed
    resource_names = []
    for email_or_id in emails_or_ids:
        if "@" in email_or_id and not email_or_id.startswith("people/"):
            # It's an email, look up the contact
            try:
                contact = get_contact(email_or_id, fields="names")
                resource_names.append(contact.get('resourceName'))
            except APIError:
                continue  # Skip if not found
        else:
            resource_names.append(email_or_id.strip())

    if resource_names:
        add_group_members(group_id, resource_names)
        return {'added_count': len(resource_names)}

    return {'added_count': 0}


# ============================================================================
# Directory Operations (Google Workspace only)
# ============================================================================

def search_directory(query: str, page_size: int = 100) -> List[Dict[str, Any]]:
    """Search the Google Workspace directory.

    Note: Requires Google Workspace and directory search enabled.

    Args:
        query: Search query (name, email, etc.)
        page_size: Number of results to return (default: 100, max: 500)

    Returns:
        List of matching directory profiles

    Raises:
        ValidationError: If query invalid
        APIError: If API call fails or feature not available
    """
    if not query or not query.strip():
        raise ValidationError("Search query cannot be empty")

    if page_size < 1 or page_size > 500:
        raise ValidationError("Page size must be between 1 and 500")

    service = build_people_service()

    try:
        result = service.people().searchDirectoryPeople(
            query=query.strip(),
            pageSize=page_size,
            readMask="names,emailAddresses,phoneNumbers,jobTitle,departments,photographs"
        ).execute()
        return result.get('people', [])
    except HttpError as e:
        if e.resp.status == 403:
            raise APIError(
                "Directory search not available. "
                "Requires Google Workspace and directory search enabled."
            )
        raise APIError(f"Failed to search directory: {e}")


def list_directory(page_size: int = 100) -> Dict[str, Any]:
    """List all profiles in the Google Workspace directory.

    Note: Requires Google Workspace and directory listing enabled.

    Args:
        page_size: Number of results per page (default: 100, max: 500)

    Returns:
        Dict with 'people' list and pagination token if available

    Raises:
        ValidationError: If parameters invalid
        APIError: If API call fails or feature not available
    """
    if page_size < 1 or page_size > 500:
        raise ValidationError("Page size must be between 1 and 500")

    service = build_people_service()

    try:
        result = service.people().listDirectoryPeople(
            pageSize=page_size,
            readMask="names,emailAddresses,phoneNumbers,jobTitle,departments,photographs"
        ).execute()
        return result
    except HttpError as e:
        if e.resp.status == 403:
            raise APIError(
                "Directory listing not available. "
                "Requires Google Workspace and directory listing enabled."
            )
        raise APIError(f"Failed to list directory: {e}")
