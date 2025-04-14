### Tables

---
#### User
```text
id: UUID PRIMARY KEY
email: VARCHAR UNIQUE, NOT NULL
name: VARCHAR NOT NULL
password: TEXT NOT NULL -- store as bcrypt-hash 
role: ENUM('INDIVIDUAL', 'ORGANIZATION') NOT NULL
is_active: BOOLEAN DEFAULT TRUE FOR ROLE: 'INDIVIDUAL' DEFAULT FALSE FOR ROLE: 'ORGANIZATIONS'
```

---
#### Document
```text
id: UUID PRIMARY KEY
uploader_id: UUID NOT NULL FOREIGN KEY (User) 'id'
owner_id: UUID NOT NULL FOREIGN KEY(User) 'id'
encrypted_data: BYTEA NOT NULL
hash: VARCHAR(64) UNIQUE NOT NULL
created_at: BIGINT (EPOCH FROM NOW())
title: TEXT NOT NULL
```

---

#### AccessRequest
```text
id: UUID PRIMARY KEY
requester_id: UUID NOT NULL FOREIGN KEY (User) 'id'
doc_id: UUID NOT NULL FOREIGN KEY (Document) 'id'
status: ENUM (PENDING, APPROVED, DECLINED, COMPLETED) DEFAULT PENDING
requested_at: BIGINT
approved_at: BIGINT
```

---

#### AuthToken
```text
id: INTEGER AI PRIMARY KEY
user_id: UUID NOT NULL FOREIGN KEY (User) 'id'
token: VARCHAR NOT NULL
created_at BIGINT DEFAULT NOW()
expires_at: BIGINT DEFAULT 24 hours from creation
```

---

#### AuditLog
```text
id: BIGINT AUTO INCREMENT PRIMARY KEY
user_id: UUID NOT NULL FOREIGN KEY (User)
action: ENUM('Requested Document', 'Approved Request', 'Downloaded Document', 'Revoked Access', 'Login', 'Logout')
doc_id: UUID NULL FOREIGN KEY (Document)
timestamp: BIGINT NOW()
ip_address: VARCHAR(45) IPv4 and 6 NOT NULL
user_agent: TEXT NOT NULL
```

---

#### EncryptionKeyStore
```text
user_id UUID NOT NULL REFERENCES "user"(id) UNIQUE,  PRIMARY KEY -- One key store per user
public_key TEXT NOT NULL,  -- User's public key for encryption
encrypted_private_key TEXT NOT NULL,  -- Encrypted version of user's private key
created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())
```
---

#### AuthLogs
```text
id BIGINT AUTO INCREMENT PRIMARY KEY,
user_id UUID NOT NULL REFERENCES "user"(id),
failed_attempts INT DEFAULT 0,
last_attempt BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
blocked_until BIGINT NULL  -- If blocked, stores Unix timestamp when the block expires
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









