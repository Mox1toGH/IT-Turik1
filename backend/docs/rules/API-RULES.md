# API Architecture Specification

## Normative Terminology

- **MUST** — absolute requirement.
- **MUST NOT** — absolute prohibition.
- **SHOULD** — recommended practice.
- **MAY** — optional behavior.

---

## API-001 — Explicit Response Contracts

### Requirement

Every API endpoint MUST explicitly declare a response schema using the framework's response declaration mechanism.

Endpoints MUST NOT rely on implicit response serialization of ORM models, QuerySets, or arbitrary Python objects.

Response data MUST be explicitly mapped to the declared schema fields.

### Compliant Implementation (DO)

```python
class GetUserResponse(Schema):
    id: int
    email: str


@router.get("/{user_id}", response=GetUserResponse)
def get_user(request, user_id: int):
    user = User.objects.get(id=user_id)

    return {
        "id": user.id,
        "email": user.email,
    }
```

### Non-compliant Implementation (DON'T)

```python
@router.get("/{user_id}")
def get_user(request, user_id: int):
    return User.objects.get(id=user_id)
```

### Rationale

Explicit response contracts ensure predictable serialization, prevent unintended data exposure, and make API behavior independently understandable and verifiable.

---

## API-002 — Endpoint-Owned Schemas

### Requirement

Each API endpoint MUST own its Request and Response schemas.

Endpoint-specific schemas MUST NOT be shared between different endpoints.

Endpoint-specific schemas MUST NOT inherit from other endpoint-specific Request or Response schemas.

This requirement applies even when multiple schemas contain identical fields.

### Compliant Implementation (DO)

```python
class GetUserResponse(Schema):
    id: int
    email: str


class UpdateUserResponse(Schema):
    id: int
    email: str
```

### Non-compliant Implementation (DON'T)

```python
class UserResponse(Schema):
    id: int
    email: str


class GetUserResponse(UserResponse):
    pass


class UpdateUserResponse(UserResponse):
    pass
```

### Rationale

Independent endpoint contracts prevent unintended coupling and ensure that modifications to one endpoint do not implicitly affect other endpoints.

Field duplication between independent API contracts is preferable to introducing hidden dependencies between API contracts.

---

## API-003 — Explicit Database Access

### Requirement

Database access MUST be explicit and identifiable when reading endpoint implementation.

Database-dependent operations MUST NOT be hidden inside response serialization or computed properties.

Related objects required by an endpoint MUST be explicitly loaded using `select_related()` or `prefetch_related()`.

### Compliant Implementation (DO)

```python
def get_user_with_profile(user_id: int):
    return User.objects.select_related(
        "profile"
    ).get(id=user_id)


@router.get("/{user_id}", response=GetUserResponse)
def get_user(request, user_id: int):
    user = get_user_with_profile(user_id)

    return {
        "id": user.id,
        "email": user.email,
    }
```

### Non-compliant Implementation (DON'T)

```python
@router.get("/{user_id}", response=GetUserResponse)
def get_user(request, user_id: int):
    user = User.objects.get(id=user_id)

    return {
        "id": user.id,
        "email": user.email,
        "profile_name": user.profile.name,
    }
```

### Rationale

Database operations must be predictable and identifiable. Hidden relationship loading can introduce unexpected queries and N+1 problems.

---

## API-004 — Explicit QuerySet Evaluation

### Requirement

QuerySets MUST NOT be passed directly to response serialization.

QuerySet evaluation MUST occur explicitly before response data is constructed.

### Compliant Implementation (DO)

```python
@router.get("/", response=list[GetUserResponse])
def get_users(request):
    users = list(
        User.objects.filter(is_active=True)
    )

    return [
        {
            "id": user.id,
            "email": user.email,
        }
        for user in users
    ]
```

### Non-compliant Implementation (DON'T)

```python
@router.get("/", response=list[GetUserResponse])
def get_users(request):
    return User.objects.filter(is_active=True)
```

### Rationale

Explicit QuerySet evaluation makes database execution boundaries visible and prevents unexpected SQL queries during response serialization.

---

## API-005 — No Database Access During Serialization

### Requirement

Response serialization MUST NOT execute database queries.

Response schemas MUST NOT trigger database access through properties, aliases, resolvers, or relationship traversal.

All database-dependent data MUST be retrieved before response serialization begins.

### Compliant Implementation (DO)

```python
user = User.objects.select_related(
    "profile"
).get(id=user_id)

return {
    "id": user.id,
    "profile_name": user.profile.name,
}
```

### Non-compliant Implementation (DON'T)

```python
class GetUserResponse(Schema):
    id: int
    profile_name: str = Field(
        alias="profile.name"
    )
```

When the related object has not been loaded, serialization may execute additional database queries.

### Rationale

Serialization MUST be a pure data transformation without additional database access.

---

## API-006 — Explicit Related Object Loading

### Requirement

All database relationships required for endpoint execution MUST be explicitly loaded.

- `select_related()` MUST be used for required ForeignKey and OneToOne relationships.
- `prefetch_related()` MUST be used for required ManyToMany and reverse relationships.

### Compliant Implementation (DO)

```python
users = User.objects.select_related(
    "profile"
).prefetch_related(
    "groups"
)

users = list(users)
```

### Non-compliant Implementation (DON'T)

```python
users = User.objects.all()

for user in users:
    print(user.profile.name)
    print(user.groups.all())
```

### Rationale

Explicit relationship loading makes query behavior predictable and prevents N+1 database queries.

---

## API-007 — Explicit Pagination

### Requirement

Pagination MUST be explicitly declared for endpoints returning collections.

Pagination MUST define documented limits and a predictable response structure.

Pagination MUST NOT be applied implicitly through undocumented global configuration.

### Compliant Implementation (DO)

```python
@router.get("/")
@paginate(LimitOffsetPagination)
def get_users(request):
    return User.objects.filter(is_active=True)
```

### Non-compliant Implementation (DON'T)

Applying global pagination behavior without an explicit project-level policy or documented endpoint contract.

### Rationale

Pagination is part of the API contract and MUST be predictable, documented, and consistent.

---

## API-008 — Explicit Filtering and Ordering

### Requirement

Filtering and ordering behavior MUST be explicitly defined.

Client-provided filtering and ordering parameters MUST be validated against approved fields.

Unvalidated client-provided values MUST NOT be passed directly to ORM filtering or ordering operations.

### Compliant Implementation (DO)

```python
def get_users(*, status: str):
    return User.objects.filter(
        status=status,
    ).order_by("id")
```

### Non-compliant Implementation (DON'T)

```python
def get_users(request):
    ordering = request.GET["ordering"]

    return User.objects.order_by(ordering)
```

### Rationale

Explicit filtering and ordering prevent unintended query behavior and unauthorized access to model fields.