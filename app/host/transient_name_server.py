# Download and ingest transients from the Transient Name Server (TNS)
import os


def get_tns_credentials():
    """
    Retrieves TNS credentials from environment variables
    """
    credentials = ['TNS_BOT_API_KEY', 'TNS_BOT_NAME', 'TNS_USERNAME',
                   'TNS_BOT_ID']

    for credential in credentials:
        credential_value = os.environ.get(credential)
        if credential_value is None:
            raise ValueError(f'{credential} not defined in environment')

    return {credential: os.environ[credential] for credential in credentials}



def ingest_new_transients():
    """
    Ingest new transients from the transient name server
    """
    tns_credentials = get_tns_credentials()

    return None

