class InternalURIs:
    SIGN_IN_V1 = "/v1/auth/signin"
    SIGN_UP_V1 = "/v1/auth/signup"
    ME_V1 = "/v1/me"
    PUBLIC_KEY_V1 = ME_V1 + "/pubkey"
    DOCUMENT_V1 = ME_V1 + "/document"
    DOCUMENT_DOWNLOAD_V1 = DOCUMENT_V1 + "/download"
    DOCUMENT_UPLOADS_V1 = DOCUMENT_V1 + "/upload"
    ACCESS_HISTORY_V1 =  ME_V1 + "/access-history"
    REQUEST_ACCESS_V1 = ME_V1 + "/request-access"
    GRANT_ACCESS_V1 = ME_V1 + "/grant"
    REQUEST_STATUS_V1 = ME_V1 + "/request-status"
    DOWNLOAD_V1 = ME_V1 + "/download"

class ExternalURLs:
    pass
