# Authentication Registration API — Frontend Integration Guide

This document explains **how frontend should call and handle** the Authentication Registration endpoint.
It is separate from backend engineering docs and focuses only on the **public API contract and UX behavior**.

---

## SECTION 1 — ENDPOINT OVERVIEW

### Base URL

- Base API prefix: `https://<YOUR-BACKEND-DOMAIN>/api/v1`
- Registration endpoint (full path):
  - `POST /api/v1/auth/register`

### Purpose

This endpoint is used to **create a new business account and its owner user** in a single request.

- Creates a `Business` (company) record.
- Creates an `Employee` record with role `owner` linked to that business.
- Marks the owner as **inactive and unverified** until they confirm their email.

### When to Call It in the User Flow

Typical frontend flow:

1. User opens **Sign Up / Create Business Account** screen.
2. User fills in:
   - Business details (name, email, industry, optional description, optional domain URL).
   - Owner details (full name, email, password).
3. Frontend performs **client-side validation** (see Sections 2 and 3).
4. On submit, frontend sends a `POST /api/v1/auth/register` request with the JSON body described below.
5. On **201 success**, redirect the user to a **“Check your email”** page explaining that they must verify their email before logging in.
6. Do **not** log the user in automatically at this stage; login happens only **after** email verification (via separate endpoints).

---

## SECTION 2 — REQUEST BODY STRUCTURE

### Full JSON Structure

The backend expects the following structure in the request body:

```json
{
  "business": {
    "name": "...",
    "email": "...",
    "industry": "...",
    "description": "...",
    "domain_url": "..."
  },
  "owner": {
    "full_name": "...",
    "email": "...",
    "password": "..."
  }
}
```

### Business Object

#### `business.name`

- **Type:** string
- **Required:** Yes
- **Backend rules:**
  - Minimum length: 2 characters
  - Maximum length: 100 characters
- **Frontend recommendations:**
  - Trim whitespace before sending.
  - Disallow empty or 1-character names.
- **Example values:**
  - `"Kalamna AI Solutions"`
  - `"Nile Commerce"`

#### `business.email`

- **Type:** string (email)
- **Required:** Yes
- **Backend rules:**
  - Must be a **valid email format**.
  - Must be **unique** in the system (no other business with the same email).
- **Frontend recommendations:**
  - Validate email format before sending.
  - Use lowercase normalization (`email.toLowerCase()`) to avoid duplicates by case.
- **Example values:**
  - `"contact@kalamna.ai"`
  - `"info@nile-commerce.com"`

#### `business.industry`

- **Type:** string (enum)
- **Required:** Yes
- **Backend rules:**
  - Must be one of the allowed enum values.
  - Actual list from backend model:

    ```text
    "Technology",
    "Finance",
    "Healthcare",
    "Education",
    "Retail",
    "Manufacturing",
    "Hospitality",
    "Transportation",
    "Real Estate",
    "Entertainment",
    "Other"
    ```

- **Frontend recommendations:**
  - Provide a dropdown/select with these exact string values.
  - Do not send arbitrary strings.
- **Example values:**
  - `"Technology"`
  - `"Retail"`
  - `"Other"`

#### `business.description`

- **Type:** string
- **Required:** No (optional)
- **Backend rules:**
  - May be `null` or omitted.
  - Any string is accepted (within normal JSON limits).
- **Frontend recommendations:**
  - Optional textarea for business description.
  - You can send an empty string `""` or simply omit the field if not used.
- **Example values:**
  - `"AI-powered customer support for Egyptian businesses."`
  - `"E-commerce platform for local merchants."`

#### `business.domain_url`

- **Type:** string (URL)
- **Required:** No (optional)
- **Backend rules:**
  - If provided, must be a **valid URL** including scheme (e.g., `https://`).
  - Validated using a strict URL validator.
  - Can be `null`/omitted.
- **Frontend recommendations:**
  - If you allow this field, validate it with a URL regex or URL parser.
  - Always include `http://` or `https://`.
- **Example values:**
  - `"https://kalamna.ai"`
  - `"https://www.nile-commerce.com"`

---

### Owner Object

#### `owner.full_name`

- **Type:** string
- **Required:** Yes
- **Backend rules:**
  - Minimum length: 2 characters
  - Maximum length: 100 characters
- **Frontend recommendations:**
  - Trim whitespace.
  - Disallow purely numeric names if that doesn’t make sense for your UX.
- **Example values:**
  - `"Omar Ahmed"`
  - `"Sara Ali"`

#### `owner.email`

- **Type:** string (email)
- **Required:** Yes
- **Backend rules:**
  - Must be a **valid email format**.
  - Must be **unique** for employees (no other user account with the same email).
- **Frontend recommendations:**
  - Validate email format before sending.
  - Use lowercase normalization.
- **Example values:**
  - `"omar@kalamna.ai"`
  - `"sara.ali@example.com"`

#### `owner.password`

- **Type:** string
- **Required:** Yes
- **Backend rules:**
  - Length: 8–128 characters (hard limit).
  - Additional complexity rules are listed in **Section 3**.
- **Frontend recommendations:**
  - Enforce the same password rules on the client to avoid unnecessary round trips.
  - Provide real-time feedback as the user types (checklist of rules).
- **Example values:**
  - `"Str0ng!Pass2025"`
  - `"Welcome@2024"`

---

## SECTION 3 — PASSWORD RULES (Frontend Validation)

The backend applies the following password rules. The frontend **must mirror these** to provide a good UX.

### Required Rules

The password must:

1. Have **at least 8 characters**.
2. Contain **at least one uppercase letter** (`A–Z`).
3. Contain **at least one lowercase letter** (`a–z`).
4. Contain **at least one digit** (`0–9`).
5. Contain **at least one special character** from this set (or a subset):

   ```text
   ! @ # $ % ^ & * ( ) , . ? " : { } | < > _ - + = / \
   ```

### Suggested UI Error Messages

When the backend rejects a password, it sends clear messages like:

- `"Password must be at least 8 characters long."`
- `"Password must contain at least one uppercase letter."`
- `"Password must contain at least one lowercase letter."`
- `"Password must contain at least one digit."`
- `"Password must contain at least one special character."`

The frontend should implement equivalent/similar messages for **client-side validation**. Suggested user-facing messages:

- **Length:**
  - _"Password must be at least 8 characters long."_
- **Uppercase:**
  - _"Password must include at least one uppercase letter (A–Z)."_
- **Lowercase:**
  - _"Password must include at least one lowercase letter (a–z)."_
- **Digit:**
  - _"Password must include at least one number (0–9)."_
- **Special character:**
  - _"Password must include at least one special character (for example: ! @ # $ %)."_

Best UX pattern:

- Show a checklist of these rules under the password field and mark each rule as **passed/failed** in real time.

---

## SECTION 4 — SUCCESS RESPONSE

### HTTP Response

- **Status code:** `201 Created`
- **Response body (JSON):**

```json
{
  "message": "Account created successfully. Please check your email to verify your account."
}
```

### Important Notes for Frontend

- The response **does NOT contain**:
  - `business_id`
  - `owner_id`
  - JWT access or refresh tokens
- Reason: The account is not fully active until the email address is verified.

### Recommended Next Steps in the UI

1. After receiving `201`:
   - Show a confirmation screen: **“Account created. Please check your email to verify your account.”**
   - Optionally show which email address the verification was sent to.
2. Do **not** automatically log the user in.
3. Do **not** call any authenticated endpoints until the user logs in after verification.

---

## SECTION 5 — ERROR HANDLING (VERY IMPORTANT)

This section describes how to handle and display errors returned by the backend.

> All examples assume the backend returns errors in FastAPI’s default format: `{ "detail": ... }`.

### 1. 400 — Business Email Already Exists

**(A) Status Code**

- `400 Bad Request`

**(B) Message**

- `"Business email already exists"`

**(C) Example Error JSON**

```json
{
  "detail": "Business email already exists"
}
```

**(D) Frontend UI Behavior**

- Map this to the `business.email` field.
- Suggested user message:
  - _"A business with this email already exists. Please use a different business email."_
- Mark the email field as invalid and scroll/focus to it.

---

### 2. 400 — Employee Email Already Exists

**(A) Status Code**

- `400 Bad Request`

**(B) Message**

- `"Employee email already exists"`

**(C) Example Error JSON**

```json
{
  "detail": "Employee email already exists"
}
```

**(D) Frontend UI Behavior**

- Map this to the `owner.email` field.
- Suggested user message:
  - _"An account with this email already exists. Try logging in instead or use a different email."_

---

### 3. 400 — Invalid Password (All Cases)

The backend validates passwords and, on failure, returns `400` with one of these messages in `detail`:

- `"Password must be at least 8 characters long."`
- `"Password must contain at least one uppercase letter."`
- `"Password must contain at least one lowercase letter."`
- `"Password must contain at least one digit."`
- `"Password must contain at least one special character."`

**(A) Status Code**

- `400 Bad Request`

**(B) Message**

- One of the strings above.

**(C) Example Error JSON**

```json
{
  "detail": "Password must contain at least one special character."
}
```

**(D) Frontend UI Behavior**

- Map this error to the `owner.password` field.
- Show the exact message from the backend where possible, or translate it to your own wording.
- Visually highlight which password rule failed.

Suggested generic messages per case:

| Backend detail text                                         | Suggested UI message                                                       |
|-------------------------------------------------------------|----------------------------------------------------------------------------|
| `Password must be at least 8 characters long.`              | "Password must be at least 8 characters long."                           |
| `Password must contain at least one uppercase letter.`      | "Add at least one uppercase letter (A–Z)."                                |
| `Password must contain at least one lowercase letter.`      | "Add at least one lowercase letter (a–z)."                                |
| `Password must contain at least one digit.`                 | "Add at least one number (0–9)."                                          |
| `Password must contain at least one special character.`     | "Add at least one special character (for example: ! @ # $ %)."            |

---

### 4. 422 — Field Missing or Invalid (Pydantic Validation)

These errors occur when **required fields are missing** or have the wrong type/format **before** the service runs.

**(A) Status Code**

- `422 Unprocessable Entity`

**(B) Message**

- FastAPI/Pydantic returns a list of validation errors. Example:

```json
{
  "detail": [
    {
      "loc": ["body", "business", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**(C) Example Error JSON (missing business.name)**

```json
{
  "detail": [
    {
      "loc": ["body", "business", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**(D) Frontend UI Behavior**

- Parse the `detail` array.
- For each item:
  - Use `loc` to identify the field (e.g., `business.name`).
  - Map `msg` to a user-friendly error.
- Suggested mapping examples:

| Condition (422)                                       | Example `msg`            | Field            | UI message                                 |
|------------------------------------------------------|--------------------------|------------------|--------------------------------------------|
| Missing `business.name`                              | `"field required"`      | business.name    | "Business name is required."              |
| Invalid email format for `owner.email`               | e.g. `"value is not a valid email address"` | owner.email      | "Enter a valid email address."           |
| Too short `owner.password` (< 8 characters)          | e.g. `"ensure this value has at least 8 characters"` | owner.password | "Password must be at least 8 characters." |

- 422 errors can be avoided almost entirely if frontend performs good client-side validation.

---

### 5. 400 — Domain URL Invalid Format

This is a special case of validation for `business.domain_url`:

- If the URL is present but **does not match** the expected format, Pydantic treats it as invalid.
- In practice, this usually results in a `422` error from Pydantic, but depending on how the backend wraps it or additional checks, you may also see a `400` in some flows.

For frontend purposes, treat any **URL-related validation failure** as:

**(A) Status Code**

- `422 Unprocessable Entity` (most common)
- or `400 Bad Request` (if backend wraps it—documented here for completeness)

**(B) Message**

- Something like `"value is not a valid URL"` inside the `detail` list, or a generic `"Invalid domain URL"` message if wrapped.

**(C) Example Error JSON**

```json
{
  "detail": [
    {
      "loc": ["body", "business", "domain_url"],
      "msg": "value is not a valid URL",
      "type": "value_error.url"
    }
  ]
}
```

**(D) Frontend UI Behavior**

- Map to `business.domain_url` field.
- Suggested UI message:
  - _"Enter a valid website URL (for example: https://example.com)."_

---

### Mapping Backend Errors to UI & UX Guidelines

#### Mapping Strategy

1. **Check status code:**
   - `400`: Business logic or custom validation error (duplicate email, password rules, etc.).
   - `422`: Structural / format errors from Pydantic (missing fields, invalid data type/shape).
2. **For 400 with `{ detail: <string> }`:**
   - Use the `detail` string to determine which field it belongs to.
   - Map to one of: `business.email`, `owner.email`, `owner.password`, or global error.
3. **For 422 with `{ detail: [...] }`:**
   - Iterate through the list and map by `loc` to specific fields.

#### UX Guidelines

- **Debounce submit:**
  - When the user clicks “Sign Up”, disable the button and show a loading state while the request is in flight.
  - Prevent double submissions.
- **Field-level errors:**
  - Show error messages directly under the related field input.
  - Highlight fields with a red border or similar.
- **Global errors:**
  - For unexpected errors (500, network issues), show a global toast or banner: _"Something went wrong. Please try again."_
- **Retry logic:**
  - For network timeouts or 5xx responses, allow the user to retry by clicking the submit button again.
  - For 400/422 validation issues, **do not auto-retry**; let the user correct the data first.
- **Loading state:**
  - Show a spinner or “Creating your account…” message while the request is pending.

---

## SECTION 6 — FRONTEND FLOW RECOMMENDATION

### Recommended Client-Side Flow

1. **User fills out form** with business and owner details.
2. **Client-side validation**:
   - Required fields: `business.name`, `business.email`, `business.industry`, `owner.full_name`, `owner.email`, `owner.password`.
   - Email format for both emails.
   - Password rules from Section 3.
   - Optional: domain URL format.
3. **If validation passes**, send `POST /api/v1/auth/register` with JSON body.
4. **Handle responses**:
   - **201:**
     - Show success state and **redirect to “Check your email” page**.
   - **400:**
     - Read `detail` string and map to specific field error messages.
   - **422:**
     - Parse `detail` array to show field-specific errors.
   - **Other (e.g. 500, network):**
     - Show a generic error: _"Something went wrong. Please try again."_

### After Success

- Route user to a **“Check your email”** page with instructions, such as:
  - _"We’ve sent a verification email to omar@kalamna.ai. Please click the link in that email to activate your account."_
- Do **not**:
  - Attempt automatic login.
  - Call token-based endpoints assuming user is authenticated.

Login should only be allowed after the user verifies their email using the future verification flow implemented by the backend.

---

## SECTION 7 — SAMPLE REQUESTS FOR FRONTEND

### Example Valid Request

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "business": {
    "name": "Kalamna AI Solutions",
    "email": "contact@kalamna.ai",
    "industry": "Technology",
    "description": "AI-powered customer support for Egyptian businesses.",
    "domain_url": "https://kalamna.ai"
  },
  "owner": {
    "full_name": "Omar Ahmed",
    "email": "omar@kalamna.ai",
    "password": "Str0ng!Pass2025"
  }
}
```

### Example Invalid Request (for Illustration)

Case: weak password + invalid owner email + missing business name.

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "business": {
    "email": "contact@kalamna.ai",
    "industry": "Technology",
    "description": "",
    "domain_url": "not-a-valid-url"
  },
  "owner": {
    "full_name": "O",
    "email": "omar-at-kalamna.ai",
    "password": "abc"
  }
}
```

Possible backend behavior:

- Pydantic 422 errors for:
  - Missing `business.name`.
  - Invalid `business.domain_url`.
  - Invalid email format for `owner.email`.
  - Too short `owner.full_name` and `owner.password`.
- If it gets through schema, the service will reject the password based on rules and return 400.

Frontends should avoid sending obviously invalid data by validating locally first.

---

## SECTION 8 — API CONTRACT SUMMARY TABLE

### Request Fields Summary

| JSON Path                 | Type     | Required | Notes                                                                                       |
|---------------------------|----------|----------|---------------------------------------------------------------------------------------------|
| `business`                | object   | Yes      | Contains all business-related fields.                                                       |
| `business.name`           | string   | Yes      | 2–100 chars.                                                                                |
| `business.email`          | string   | Yes      | Valid email; must be unique across businesses.                                              |
| `business.industry`       | string   | Yes      | One of: Technology, Finance, Healthcare, Education, Retail, Manufacturing, Hospitality, Transportation, Real Estate, Entertainment, Other. |
| `business.description`    | string   | No       | Optional free text description.                                                             |
| `business.domain_url`     | string   | No       | Optional; must be a valid URL with scheme (e.g. https://example.com) if provided.           |
| `owner`                   | object   | Yes      | Contains owner user fields.                                                                 |
| `owner.full_name`         | string   | Yes      | 2–100 chars.                                                                                |
| `owner.email`             | string   | Yes      | Valid email; must be unique across employees.                                              |
| `owner.password`          | string   | Yes      | 8–128 chars and must satisfy all complexity rules (uppercase, lowercase, digit, special).   |

### Response Summary

| Condition                  | Status | Body Shape                                       | Notes                                                       |
|----------------------------|--------|--------------------------------------------------|-------------------------------------------------------------|
| Success                    | 201    | `{ "message": string }`                         | Message instructs user to check email for verification.     |
| Business email exists      | 400    | `{ "detail": "Business email already exists" }` | Map to business email field; ask user to use different one. |
| Employee email exists      | 400    | `{ "detail": "Employee email already exists" }` | Map to owner email field.                                   |
| Password rule failure      | 400    | `{ "detail": "Password must ..." }`            | Map to password field and show rule-specific error.         |
| Validation error (schema)  | 422    | `{ "detail": [ ... ] }`                        | Map each issue to the corresponding field.                 |
| Other server / network     | 5xx    | Variable                                       | Show generic error and allow retry.                        |

if there is any problem contact with us