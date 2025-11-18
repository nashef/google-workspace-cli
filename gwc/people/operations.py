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
