# Backend Authentication Registration Flow

> Scope: This document describes the **backend-only implementation** of the registration flow for creating a new **Business** and its **owner Employee** in the Kalamna FastAPI backend. It is written for backend engineers working on the SaaS platform.

---

## SECTION 1 — ARCHITECTURE OVERVIEW

### What the Registration Feature Does

The registration feature creates **two persisted records in a single transactional operation**:

1. A new `Business` entity (company-level account).
2. A new `Employee` entity with `role=OWNER` linked to that business.

Additional behaviors:

- Ensures **uniqueness** for:
  - Business email (`Business.email`).
  - Owner email (`Employee.email`).
- Validates the **strength of the owner password** against explicit complexity rules.
- Hashes the owner password using **Argon2 & bcrypt** (via `passlib` `CryptContext`).
- Marks the owner as **inactive and unverified** (`is_active=False`, `is_verified=False`) to enforce an email-verification step later.
- Does **not** return IDs or tokens — only a success message, deferring identity and session creation to the login flow.

### Domain Structure: Schemas, Services, Routers

The registration feature is split across three main layers:

| Layer     | Location                                                             | Responsibility                                         |
|----------|----------------------------------------------------------------------|--------------------------------------------------------|
| Router   | `kalamna/apps/authentication/routers.py`                             | HTTP endpoint, dependency injection, error mapping     |
| Schemas  | `kalamna/apps/authentication/schemas.py`<br>`kalamna/apps/business/schemas.py`<br>`kalamna/apps/employees/schemas.py` | Input shapes, basic field-level validation             |
| Service  | `kalamna/apps/authentication/services.py`                            | Business logic, password validation + hashing, DB ops  |
| Models   | `kalamna/apps/business/models.py`<br>`kalamna/apps/employees/models.py` | Persistence structure, relationships, constraints      |
| Security | `kalamna/core/security.py`                                           | Password hashing & verification, JWTs (not used here)  |
| Validation | `kalamna/core/validation.py`                                       | Password complexity rules                              |

### High-Level Flow: Request → Validation → Service → DB

1. **HTTP Request (Router)**
   - Path: `POST /auth/register` (mounted under `/api/v1` in the main app → `/api/v1/auth/register`).
   - The body is parsed into a `RegisterSchema` instance by FastAPI/Pydantic.

2. **Schema Validation (Pydantic)**
   - Pydantic performs type and basic constraint validation for:
     - `BusinessCreateSchema`
     - `OwnerCreateSchema`
   - If invalid, FastAPI returns `422 Unprocessable Entity` with standard Pydantic error details.

3. **Service Execution** (`register_business_and_owner`)
   - The router passes the validated `RegisterSchema` and an `AsyncSession` to `register_business_and_owner`.
   - The service performs:
     - Email uniqueness checks (business and employee).
     - Domain URL normalization (`HttpUrl` → `str`).
     - Password complexity validation (`validate_password`).
     - Password hashing (`hash_password` with Argon2, offloaded via `asyncio.to_thread`).
     - Creation of `Business` and `Employee` rows.

4. **Database Persistence (SQLAlchemy)**
   - A new `Business` is added and flushed (`await db.flush()`) to obtain `business.id`.
   - A new owner `Employee` (role `OWNER`) is created with `business_id` set.
   - A single `await db.commit()` commits the transaction.

5. **Response**
   - On success, the router returns `201 Created` with:

     ```json
     {
       "message": "Account created successfully. Please check your email to verify your account."
     }
     ```

   - On **business rule errors** (duplicate email, weak password), the service raises `ValueError`, which the router maps to `400 Bad Request` with a simple `detail` message.

---

## SECTION 2 — SCHEMAS EXPLANATION

### RegisterSchema (Business + Owner Nested Input)

`RegisterSchema` is the **request body** for the registration endpoint. It encapsulates two nested objects:

- `business`: **company-level** attributes needed to create a `Business` record.
- `owner`: **user-level** attributes needed to create the owner `Employee` record.

This design groups business and owner data into a single, coherent payload and transaction.

### BusinessCreateSchema

File: `kalamna/apps/business/schemas.py`

**Field-level details**

| Field        | Type             | Constraints / Notes                                               |
|-------------|------------------|-------------------------------------------------------------------|
| `name`      | `str`            | Required; 2–100 chars (`min_length=2`, `max_length=100`).         |
| `email`     | `EmailStr`       | Required; Pydantic validates RFC-compliant email format.          |
| `industry`  | `IndustryEnum`   | Required; must be one of the enum values from `IndustryEnum`.    |
| `description` | `Optional[str]` | Optional free-text description.                                  |
| `domain_url`  | `Optional[HttpUrl]` | Optional; must be a valid URL if provided; normalized as `HttpUrl`. |

**Validation rules**

- Pydantic automatically enforces types and lengths.
- `industry` must match one of the `IndustryEnum` values defined in `kalamna.apps.business.models.IndustryEnum` (e.g. `"Technology"`, `"Finance"`, etc.).
- `domain_url` is validated as a full URL (includes scheme). If invalid, the request is rejected at the schema layer with a 422 error.

### OwnerCreateSchema

File: `kalamna/apps/employees/schemas.py`

**Field-level details**

| Field       | Type       | Constraints / Notes                                            |
|------------|------------|----------------------------------------------------------------|
| `full_name`| `str`      | Required; 2–100 chars.                                        |
| `email`    | `EmailStr` | Required; validated email address.                            |
| `password` | `str`      | Required; 8–128 chars at schema level, more rules in service. |

**Validation rules**

- `full_name`: ensures a non-trivial name; empty or 1-char names are rejected.
- `email`: ensures well-formed email.
- `password`: ensures **minimum length** 8 and maximum length 128 at the schema level.
  - Additional complexity rules (uppercase, lowercase, digits, symbols) are enforced later in the **service layer** using `validate_password`.

### Why Nested Schemas Are Used

Reasons for the nested structure (`RegisterSchema` containing `business` and `owner`):

1. **Atomicity & Transactional Semantics**
   - The API models the intent: “create a business and its owner in one shot”.
   - It maps cleanly to the service-layer function `register_business_and_owner` which wraps both DB operations in a single transaction.

2. **Strong Separation of Concerns**
   - `BusinessCreateSchema` is reusable in other parts of the system (e.g. internal business creation tools) without mixing user-related fields.
   - `OwnerCreateSchema` is reusable for other flows where you create an owner account, possibly via invitations.

3. **Clarity in API Design**
   - Keeps the top-level JSON body organized and self-describing:

     ```json
     {
       "business": { ... },
       "owner": { ... }
     }
     ```

4. **Extensibility**
   - You can later extend each schema independently (e.g. additional business metadata, locale, settings, or extra owner attributes) without breaking the top-level contract.

### Example Registration Request Body

This is **for internal understanding**; real clients should conform to the same structure.

---

## SECTION 3 — PASSWORD SYSTEM (FULL DETAILS)

### CryptContext Configuration

File: `kalamna/core/security.py`

`CryptContext` is configured with:

- `schemes=["argon2", "bcrypt"]`
- `default="argon2"`
- `deprecated="auto"`

**Implications:**

- New hashes created via `pwd_context.hash()` (hence `hash_password`) use **Argon2** by default.
- `verify_password` can transparently verify hashes stored using either **Argon2** or **bcrypt** (or any future scheme listed in `schemes`).
- `deprecated="auto"` allows passlib to mark old schemes as deprecated and manage future migrations if needed.

### Why Argon2 is the Primary Hashing Scheme

Argon2 (specifically `argon2id` under passlib) is used as the primary scheme because:

1. **Memory-Hard Design**
   - Argon2 is intentionally expensive in terms of both CPU and memory.
   - This limits the efficiency of GPU/ASIC-based brute-force attacks.

2. **Modern, Strong Defaults**
   - Designed as a successor to bcrypt/scrypt, with modern cryptographic review and a tunable parameter set.

3. **Passlib Integration**
   - `passlib` provides a stable and well-tested interface for Argon2, handling salts, parameters, and correct encoding.

4. **Future-Proofing**
   - Using Argon2 now avoids needing to migrate away from older schemes as security expectations rise.

### Why bcrypt is Kept as Fallback (Verification Only)

Even though Argon2 is the default for **new hashes**, `bcrypt` remains in the `schemes` list:

- `verify_password` will **accept both Argon2 and bcrypt hashes**.
- This is important if:
  - There are **legacy users** whose passwords were hashed with bcrypt.
  - Or if you later migrate from a system that used bcrypt.

Current behavior:

- Registration always **creates Argon2 hashes**.
- Login / verification will continue to verify existing bcrypt hashes if present.

This allows smooth migrations without forcing a full re-hash of all user passwords at once.

### Password Hashing Flow (Registration)

Relevant code: `kalamna/apps/authentication/services.py`

Flow:

1. The **plain text password** comes from `OwnerCreateSchema.password` as `o.password`.
2. `validate_password(o.password)` ensures the password meets complexity rules (see Section 4).
3. If valid, `hash_password(o.password)` is executed inside `asyncio.to_thread(...)`:
   - `hash_password` calls `pwd_context.hash(password)`.
   - Argon2 is used to generate a secure hash.
4. The resulting `hashed` string is stored in the database as `Employee.password`.

**Why `asyncio.to_thread`?**

- Argon2 hashing is CPU-intensive and blocking.
- Offloading it to `asyncio.to_thread` prevents blocking the event loop in an async FastAPI environment.

### `verify_password` Flow (Login / Future Use)

While not directly used in registration, `verify_password` is key for the login flow.

Expected usage:

1. Fetch stored `hashed` password from DB (`Employee.password`).
2. Call `verify_password(plain_password_from_login, hashed)`.
3. `CryptContext` determines the correct scheme from the hash prefix and applies the corresponding verifier:
   - If Argon2 hash → Argon2 verification.
   - If bcrypt hash → bcrypt verification.

Return value:

- `True` if the password matches.
- `False` or exception (depending on calling code) for mismatches or malformed hashes.
---

## SECTION 4 — PASSWORD VALIDATION LOGIC

### Rules and Implementation

File: `kalamna/core/validation.py`
**Rule breakdown**

| Rule ID | Description                                        | Implementation Detail                                      |
|--------|----------------------------------------------------|------------------------------------------------------------|
| R1     | Minimum length 8                                   | `len(password) < 8` → error                                |
| R2     | At least one uppercase letter                      | `re.search(r"[A-Z]", password)`                           |
| R3     | At least one lowercase letter                      | `re.search(r"[a-z]", password)`                           |
| R4     | At least one digit                                 | `re.search(r"[0-9]", password)`                           |
| R5     | At least one special character from a defined set  | `re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", password)` |

On the first failing rule, a `ValidationError` is raised with a **specific, user-friendly message**.

### Where Validation Happens (Service Layer)

In `kalamna/apps/authentication/services.py`:

Key points:

- Password complexity is enforced **inside the service layer**, not in the Pydantic schema.
- The service catches `ValidationError` and converts it to `ValueError`.
- The router then maps `ValueError` to an HTTP 400 response.
---

## SECTION 5 — REGISTRATION SERVICE FLOW (LINE BY LINE)

### Function Signature

File: `kalamna/apps/authentication/services.py`
### Step-by-Step Explanation

1. **Input Decomposition**

   ```python
   b = data.business
   o = data.owner
   ```

   - `data` is a `RegisterSchema` instance.
   - `b` and `o` are Pydantic models:
     - `b: BusinessCreateSchema`
     - `o: OwnerCreateSchema`

2. **Unique Business Email Check**

   ```python
   existing_business = await db.scalar(
       select(Business).where(Business.email == b.email)
   )
   if existing_business:
       raise ValueError("Business email already exists")
   ```

   - Executes a `SELECT` query on `businesses` table filtering by `email`.
   - Returns a single `Business` instance or `None` using `db.scalar`.
   - If a business already exists with the same email, raises `ValueError`.
   - The router converts this to HTTP 400: `{"detail": "Business email already exists"}`.

3. **Unique Employee Email Check**

   ```python
   existing_employee = await db.scalar(
       select(Employee).where(Employee.email == o.email)
   )
   if existing_employee:
       raise ValueError("Employee email already exists")
   ```

   - Similar logic, but against the `employees` table.
   - Ensures **no user account** already exists with the same email.
   - Again, mapped to HTTP 400 by the router.

4. **Domain URL Conversion (HttpUrl → str) & Business Creation**

   ```python
   print("DEBUG domain_url:", b.domain_url, type(b.domain_url))
   business = Business(
       name=b.name,
       email=b.email,
       industry=b.industry,
       description=b.description,
       domain_url=str(b.domain_url) if b.domain_url else None,
   )

   db.add(business)
   await db.flush()  # get business.id
   ```

   - `b.domain_url` is an optional `HttpUrl` from Pydantic, not a raw string.
   - For the DB model, `Business.domain_url` is a `String(255)`, so:
     - If a URL is present: `domain_url=str(b.domain_url)`.
     - If not: `None` is passed (stored as `NULL`).
   - `db.add(business)`: stage the new `Business` object for insertion.
   - `await db.flush()` sends pending changes to the DB without committing:
     - This guarantees that `business.id` is populated with a generated UUID.
     - The ID is needed to set `Employee.business_id` next.

5. **Password Validation**

   ```python
   try:
       validate_password(o.password)
   except ValidationError as e:
       raise ValueError(str(e)) from e
   ```

   - Applies the **business-layer password rules** to `o.password`.
   - On failure, `validate_password` raises `ValidationError` with a reason.
   - The service converts this into a generic `ValueError`, preserving the message.
   - The router interprets any `ValueError` as a 400 error.

6. **Password Hashing Using Argon2**

   ```python
   hashed = await asyncio.to_thread(hash_password, o.password)
   ```

   - Offloads `hash_password(o.password)` to a worker thread.
   - `hash_password` uses the `CryptContext` configured with **Argon2** (default) and **bcrypt**.
   - The result is a secure hash string stored later in `Employee.password`.

7. **Creating the Employee (role=OWNER)**

   ```python
   owner = Employee(
       full_name=o.full_name,
       email=o.email,
       password=hashed,
       business_id=business.id,
       role=EmployeeRole.OWNER,
       is_verified=False,
       is_active=False,
       email_verified_at=None,
   )
   db.add(owner)
   ```

   - Initializes an `Employee` SQLAlchemy model instance with:
     - `full_name` and `email` from `OwnerCreateSchema`.
     - `password` set to the **hashed password**.
     - `business_id` set to the just-created `business.id` (from `flush`).
     - `role=EmployeeRole.OWNER` to represent the account owner.
     - `is_verified=False`: email not yet verified.
     - `is_active=False`: account not yet active for login/usage.
     - `email_verified_at=None`: timestamp to be filled once verification succeeds.
   - `db.add(owner)` stages the owner for insertion.

   **Note on `is_active` default:**
   - In the model, `is_active` has a default of `True`. Here we explicitly override it to `False` for owners created via registration until they verify their email.

8. **Transaction Commit**

   ```python
   await db.commit()

   return business, owner
   ```

   - `await db.commit()` atomically persists both `Business` and `Employee` records.
   - If an exception occurs before this commit, the transaction is rolled back and no records are persisted.
   - The function returns `(business, owner)` for internal use, but the router **ignores these values** and instead returns a simple message.

### Why No `business.owner_id` is Used

- The relationship is implemented as **one-to-many**:
  - A business has many employees.
  - The owner is just an employee with `role=OWNER`.
- There is **no `owner_id` column on the `Business` model`**:
  - This avoids circular dependencies and simplifies the schema.
  - Ownership can be derived by querying `Employee` where `business_id=<id>` and `role=OWNER`.
  - Future support for multiple owners or other privileged roles becomes easier.

## SECTION 6 — ROUTER FLOW

### Endpoint Definition

File: `kalamna/apps/authentication/routers.py`

**Path & Method**

- Method: `POST`
- Relative path: `/auth/register`
- Assuming router is included under `/api/v1`, the full path becomes:
  - `POST /api/v1/auth/register`

**Request & Dependencies**

- `data: RegisterSchema` — body parsed and validated as described earlier.
- `db: AsyncSession = Depends(get_db)` — async SQLAlchemy session from the shared DB dependency.

### Error Handling (ValueError → HTTP 400)

```python
try:
    await register_business_and_owner(data, db)
except ValueError as e:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(e),
    ) from e
```

- The router strictly interprets any `ValueError` thrown by the service as a **client error (400)**.
- Typical `ValueError` messages:
  - "Business email already exists"
  - "Employee email already exists"
  - Password complexity error messages (forwarded from `validate_password`).

This pattern keeps **service code** clean (raising domain errors) while localizing the HTTP-specific mapping at the router.

### Response Semantics: Why Only Message, Not IDs

```python
return {
    "message": "Account created successfully. Please check your email to verify your account."
    # TODO: In the future, add a boolean to indicate if verification email was sent
}
```

## SECTION 8 — FUTURE EXTENSIONS (EMAIL VERIFICATION SYSTEM)

This section outlines how a teammate can extend the current design to implement an **email verification flow** on top of registration.

### High-Level Flow

1. **Registration (existing)**
   - Create `Business` and owner `Employee` with:
     - `is_verified=False`
     - `is_active=False`
     - `email_verified_at=None`

2. **Generate Verification Token**
3. **Send Verification Email**
     - Trigger an async task (e.g. via Celery, RQ, or background task) to send an email.
   - Email contains a link like:
     ```text
     https://app.kalamna.ai/verifyl?token=<token>
     ```

4. **Verification Endpoint**
=

5. **Guard Login by Verification**

   - In the login flow (not yet implemented here), after verifying password:
     - Deny login if `is_verified` is `False` or `is_active` is `False`.
     - Return a specific error message, e.g. "Please verify your email before logging in".

### Data Model Considerations

- The `Employee` model already has:
  - `is_verified: bool`
  - `email_verified_at: datetime | None`

This is sufficient for a minimal verification system.


