
# Kalamna – Registration Flow (Paper Sketch Document)
# **1. Overview**

The Kalamna registration system uses a **single unified endpoint** to create:

1. A **Business** (organization)
2. An **Owner Employee**

Both must validate their data before creation.
The business and owner will remain in **pending/unverified state** until email verification is completed.

**Email verification is NOT implemented in this ticket.**
Another teammate will handle it — notes included below.

---

# **2. Required Fields**

## **2.1 Business Requirements**

| Field       | Required | Rule                                                 |
| ----------- | -------- |------------------------------------------------------|
| name        | yes      | min length 2                                         |
| email       | yes      | unique                                               |
| industry    | **yes**  | must be valid IndustryEnum                           |
| status      | pending  | enum "pending", "active" , "suspended" , "deleted"   |
| domain_url  | optional | unique                                               |
| description | optional | text                                                 |

## **2.2 Owner Employee Requirements**

| Field       | Required                         | Rule                         |
| ----------- |----------------------------------| ---------------------------- |
| full_name   | yes                              | min length 2                 |
| email       | yes                              | unique across Employee table |
| password    | yes                              | min length 8                 |
| role        | forced                           | owner                        |
| is_active   | false until verification & login |                              |
| is_verified | false until verification         |                              |

---

# **3. Password Hashing – Options**

We want the system **secure and scalable**, so recommend these hashing libraries:

### ** bcrypt (industry standard)**

Strength: Very secure, widely used, recommended for FastAPI.

---

# **4. Updated Registration Flow (Step-by-Step)**

### **STEP 1 — Validate Business Data**

* industry is required
* business email must be unique
* domain_url must be unique
* valid enum for industry

### **STEP 2 — Validate Owner Employee Data**

* owner email must be unique
* password ≥ 8 chars and contains at least 1 digit, capital letter
* role = owner (force override)

### **STEP 3 — Hash Password**

Using bcrypt:

```python
hashed = hash_password(owner_password)
```

### **STEP 4 — Create Business**

* status = "pending"
* owner_id = assigned later

### **STEP 5 — Create Owner Employee**

* is_verified = false
* is_active = false
* email_verified_at = null
* link to business_id

### **STEP 6 — Generate email verification token (TO-DO)**

(Another teammate will implement, see notes below.)

### **STEP 8 — Return Registration Response**

```
{
  "message": "Please check your email to verify your business account.",
  "business_id": "...",
  "owner_id": "...",
  "verification_required": true
}
```

---

# **5. Notes for Teammate (Verification System TO-DO)**

Here is what you should tell your teammate — a clean bullet list of tasks.

---

## **5.1 Email Verification Model (TO-DO by teammate)**

Create table: **email_verification_tokens**

---

## **5.2 Endpoint to Verify Email (TO-DO by teammate)**

### Endpoint:

```
GET /auth/verify?token=xyz
```

### Logic Required:

1. Find token
2. Ensure token not expired
3. Ensure token not used
4. Mark employee:
    * is_verified = true
    * is_active = true
    * email_verified_at = now()
5. Update business:
    * if owner is verified → business.status = "active"
6. Mark verification_token.used_at = now()

---

## **5.3 Email Sending System (TO-DO by teammate)**

Use:

*  BackgroundTasks OR
* Celery queue (optional) OR
* messages queue (optional)

Send email containing:

```
https://yourdomain.com/auth/verify?token=XYZ
```

---

## **5.4 Error Cases (TO-DO by teammate)**

* token not found
* token expired
* token already used
* employee already verified

Return simple HTML or JSON response.

---

# **6. Updated Flow Diagram (Text UML)**

```
User → POST /auth/register
      → Validate request
      → Validate business fields
      → Validate owner fields
      → Hash owner password
      → Create Business (status=pending)
      → Create Owner Employee (verified=false, active=false)
      → Link owner to business
      → Generate verification token (TO-DO)
      → Send email (TO-DO)
API → Response: "Please check your email"
```