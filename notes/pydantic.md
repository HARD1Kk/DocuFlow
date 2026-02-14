# Pydantic & Pydantic Settings - Explained

## **What is Pydantic?**

A Python library for **data validation** and **parsing** using type hints. It ensures your data has the correct types and values.

**Why use it?**
- ✅ Automatic data validation
- ✅ Type conversion (e.g., "123" → 123)
- ✅ Clear error messages
- ✅ Works great with APIs, configs, and data processing

---

## **Pydantic Core Concepts**

### 1. **BaseModel - The Foundation**

Think of `BaseModel` as a blueprint for your data structure.

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
```

**What happens?**
- When you create a `User`, Pydantic checks if data matches the types
- If `id` is a string "5", it auto-converts to integer `5`
- If conversion fails, you get a clear error

```python
user = User(id=1, name="Alice", email="alice@example.com")
# ✅ Works fine

user = User(id="hello", name="Alice", email="alice@example.com")  
# ❌ Error: id must be integer-compatible
```

---

### 2. **Validation - Keeping Data Clean**

Pydantic validates data automatically, but you can add custom rules.

**Default Values:**
```python
class User(BaseModel):
    name: str
    age: int = 18  # If age not provided, defaults to 18
```

**Optional Fields:**
```python
from typing import Optional

class User(BaseModel):
    name: str
    nickname: Optional[str] = None  # Can be None or a string
```

---

### 3. **Field - Adding Constraints**

`Field` lets you set rules like min/max values, string length, etc.

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    price: float = Field(gt=0, le=10000)  # gt = greater than, le = less/equal
    quantity: int = Field(default=1, ge=1)  # ge = greater/equal
```

**Common Field arguments:**
- `min_length`, `max_length` - for strings
- `gt`, `ge`, `lt`, `le` - for numbers (greater/less than)
- `pattern` - regex for strings
- `default` - default value

---

### 4. **Custom Validators**

Add your own validation logic.

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    username: str
    age: int
    
    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
    
    @field_validator('age')
    def check_age(cls, v):
        if v < 13:
            raise ValueError('Must be 13 or older')
        return v
```

**How it works:**
- Validator runs automatically when you create an instance
- `cls` = the class, `v` = the value being validated
- Raise `ValueError` to reject invalid data

---

### 5. **Useful Methods**

```python
user = User(id=1, name="Alice", email="alice@example.com")

# Convert to dictionary
user.model_dump()  
# {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'}

# Convert to JSON string
user.model_dump_json()  
# '{"id":1,"name":"Alice","email":"alice@example.com"}'

# Create from dictionary
data = {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'}
user2 = User(**data)
```

---

## **Pydantic Settings - Configuration Management**

### **What is Pydantic Settings?**

Extension of Pydantic for managing **application configuration**. It reads settings from:
- Environment variables
- `.env` files
- Defaults in code

**Why use it?**
- ✅ Keep secrets out of code (DATABASE_URL, API_KEYS)
- ✅ Different configs for dev/production
- ✅ Type-safe configuration
- ✅ Automatic loading from environment

---

### **How It Works**

**Step 1: Install**
```bash
pip install pydantic-settings
```

**Step 2: Create Settings Class**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str  # Required, no default
    api_key: str
```

**Step 3: Load Settings**

Settings loads from **environment variables automatically**:

```bash
# In terminal
export DATABASE_URL="postgresql://localhost/mydb"
export API_KEY="secret123"
export DEBUG="true"
```

```python
settings = Settings()
print(settings.database_url)  # postgresql://localhost/mydb
print(settings.debug)  # True (auto-converted from string)
```

---

### **Using .env Files**

Instead of setting environment variables manually, use a `.env` file.

**Create `.env` file:**
```
DATABASE_URL=postgresql://localhost/mydb
API_KEY=secret123
DEBUG=true
APP_NAME=ProductionApp
```

**Load it:**
```python
class Settings(BaseSettings):
    app_name: str
    debug: bool
    database_url: str
    api_key: str
    
    class Config:
        env_file = ".env"  # Tell Pydantic to read this file

settings = Settings()  # Automatically loads from .env
```

---

### **Configuration Options**

```python
class Settings(BaseSettings):
    database_url: str
    
    class Config:
        env_file = ".env"  # Which file to read
        env_file_encoding = 'utf-8'  # File encoding
        case_sensitive = False  # API_KEY = api_key (case doesn't matter)
        env_prefix = "MYAPP_"  # Only read vars starting with MYAPP_
```

**With prefix example:**
```
# .env
MYAPP_DATABASE_URL=postgres://...
MYAPP_DEBUG=true
OTHER_VAR=ignored  # Won't be read
```

---

### **Nested Settings**

Organize complex configs into groups.

```python
class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    username: str
    password: str

class Settings(BaseSettings):
    app_name: str
    database: DatabaseSettings
    
    class Config:
        env_nested_delimiter = "__"  # Use __ to separate nested fields
```

**In .env:**
```
APP_NAME=MyApp
DATABASE__HOST=prod-server
DATABASE__PORT=3306
DATABASE__USERNAME=admin
DATABASE__PASSWORD=secret
```

---

### **Singleton Pattern (Best Practice)**

Load settings **once** and reuse everywhere.

```python
from functools import lru_cache

@lru_cache()  # Caches the result, only creates Settings once
def get_settings():
    return Settings()

# Use it
settings = get_settings()
print(settings.database_url)

# In another file
settings = get_settings()  # Same instance, not recreated
```

---

## **Real-World Example**

**File: `.env`**
```
DATABASE_URL=postgresql://user:pass@localhost/mydb
SECRET_KEY=super-secret-key
DEBUG=false
MAX_CONNECTIONS=10
```

**File: `config.py`**
```python
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    debug: bool = False
    max_connections: int = Field(default=5, ge=1, le=100)
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

**File: `main.py`**
```python
from config import get_settings

settings = get_settings()

if settings.debug:
    print("Debug mode ON")

print(f"Connecting to: {settings.database_url}")
print(f"Max connections: {settings.max_connections}")
```

---

## **Key Differences**

| Aspect | Pydantic | Pydantic Settings |
|--------|----------|-------------------|
| **Purpose** | Validate any data (API requests, user input) | Manage app configuration |
| **Data Source** | Python code, JSON, dicts | Environment variables, .env files |
| **Base Class** | `BaseModel` | `BaseSettings` |
| **Auto-loading** | No | Yes (from environment) |
| **Use Case** | User profiles, API responses | Database URLs, API keys, feature flags |

---

## **Quick Tips**

✅ **Use Pydantic** when validating data from users, APIs, or files  
✅ **Use Pydantic Settings** for application configuration (secrets, URLs)  
✅ Always use `.env` files for sensitive data (never commit them to git!)  
✅ Use `Field` to add constraints  
✅ Use `@field_validator` for complex validation logic  
✅ Use `@lru_cache()` with settings for performance  

---

