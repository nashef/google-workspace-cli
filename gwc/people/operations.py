"""Google People API operations."""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..shared.auth import get_credentials, PEOPLE_SCOPES
from ..shared.exceptions import APIError, ValidationError


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
