### Tables

---
#### User
```python
class UserSchema(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)  # hashed
    role = Column(Enum(AccountType), nullable=False)
    is_active = Column(Boolean, nullable=False)

class AccountType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"
```

---
#### Document
```python
class DocumentSchema(Base):
    __tablename__ = "document"

    id = Column(String(64), primary_key=True, nullable=False)
    uploader_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    encrypted_data = Column(BYTEA, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    title = Column(Text, nullable=False)
```

---

#### AccessRequest
```python
class AccessRequestSchema(Base):
    __tablename__ = "access_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    doc_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=False)
    status = Column(Enum(AccessStatus), default=AccessStatus.PENDING, nullable=False)
    requested_at = Column(BigInteger, nullable=False)
    approved_at = Column(BigInteger, nullable=True)

class AccessStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    COMPLETED = "COMPLETED"
```

---

#### AuthToken
```python
class AuthTokenSchema(Base):
    __tablename__ = "auth_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    token = Column(String, nullable=False)
    created_at = Column(BigInteger, nullable=False)
    expires_at = Column(BigInteger, nullable=False)
```

---

#### AuditLog
```python
class AuditLogSchema(Base):
    __tablename__ = "audit_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    doc_id = Column(UUID(as_uuid=True), ForeignKey("document.id"), nullable=True)
    timestamp = Column(BigInteger, nullable=False)
    ip_address = Column(String(45), nullable=False)  # supports IPv6
    user_agent = Column(Text, nullable=False)

class AuditAction(Enum):
    REQUESTED_DOCUMENT = "Requested Document"
    APPROVED_REQUEST = "Approved Request"
    DOWNLOADED_DOCUMENT = "Downloaded Document"
    REVOKED_ACCESS = "Revoked Access"
    LOGIN = "Login"
    LOGOUT = "Logout"
```

---

#### EncryptionKeyStore
```python
class EncryptionKeyStoreSchema(Base):
    __tablename__ = "encryption_key_store"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    public_key = Column(String, nullable=False)
    encrypted_private_key = Column(String, nullable=False)
    created_at = Column(BigInteger, nullable=False, default=lambda: int(time.time()))
```
---

#### AuthLogs
```python
class AuthLogsSchema(Base):
    __tablename__ = "encryption_key_store"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, unique=True, nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    last_attempt = Column(BIGINT, default=lambda: int(time.time()), nullable=False)
    blocked_until = Column(BIGINT, nullable=True)
```

---

---

### Cardinality & Relationship

 **User (1) → (Many) AccessRequest**  
- A user (employer/university) can make multiple document requests.

 **User (1) → (Many) Document**  
- A university uploads multiple documents for different individuals.

 **Document (1) → (Many) AccessRequest**  
- A single document may have multiple access requests from different employers/universities.

 **User (1) → (Many) AuthToken**  
- A user can have multiple active sessions (multiple tokens).

 **User (1) → (1) EncryptionKeyStore**  
- Each user has exactly one cryptographic key store entry.

 **User (1) → (Many) AuditLog**  
- A user can perform multiple actions, all of which are logged.

 **Document (1) → (Many) AuditLog**  
- A single document can be involved in multiple log entries (e.g., requested, downloaded).

 **User (1) → (1) AuthLogs**  
   - Each user has **one login attempt tracking entry** (`failed_attempts` is updated instead of inserting new rows).

---

### **Diagram Representation (Text-Based)**
```
User (1) ------------< (Many) AccessRequest
User (1) ------------< (Many) Document
User (1) ------------< (Many) AuthToken
User (1) ------------< (1) EncryptionKeyStore
User (1) ------------< (Many) AuditLog
User (1) ------------< (1) AuthLogs
Document (1) ------------< (Many) AccessRequest
Document (1) ------------< (Many) AuditLog
```

---

### ** Functional Dependencies**
```text
USER - D
user_id → email, name, password, role, public_key, is_active  
email → user_id, name, password, role, public_key, is_active

DOCUMENT - D
document_id → uploader_id (user_id), owner_id (user_id), encrypted_data, hash, created_at, title  
hash → document_id, uploader_id (user_id), owner_id (user_id), encrypted_data, created_at, title

ACCESS REQUEST - D 
access_request_id → requester_id (user_id), doc_id (document_id), status, requested_at, approved_at

AUTH_TOKEN - D
auth_token_id → user_id, token, created_at, expires_at  
token → auth_token_id, user_id, created_at, expires_at

AUDIT LOG
audit_log_id → user_id, action, doc_id (document_id), timestamp, ip_address, user_agent

ENCYRPTION KEY STORE - D
user_id → key_store_id, public_key, encrypted_private_key, created_at

AUTH LOGS - D
user_id → auth_log_id, failed_attempts, last_attempt, blocked_until
```









