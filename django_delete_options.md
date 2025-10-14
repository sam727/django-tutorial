# Django ForeignKey DELETE Options: CASCADE vs PROTECT vs RESTRICT

## Overview Table

| Option | What happens when parent deleted? | Use case |
|--------|----------------------------------|----------|
| **CASCADE** | Children automatically deleted | "If parent dies, children can't exist" |
| **PROTECT** | Deletion blocked with error | "Can't delete parent while children exist" |
| **RESTRICT** | Deletion blocked (but smarter) | "Can't delete if children exist" |

---

## 1. CASCADE - "Delete children too"

### Example: Blog Post and Comments

```python
from django.db import models

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()

class Comment(models.Model):
    post = models.ForeignKey(
        BlogPost, 
        on_delete=models.CASCADE  # ← CASCADE
    )
    text = models.TextField()
```

### What happens:

```python
# Create a post with comments
post = BlogPost.objects.create(title="Django Tips", content="...")
Comment.objects.create(post=post, text="Great article!")
Comment.objects.create(post=post, text="Thanks for sharing!")

print(Comment.objects.count())  # → 2

# Delete the post
post.delete()  # ✅ SUCCESS!

# All comments are AUTOMATICALLY deleted
print(Comment.objects.count())  # → 0
```

### Real-world use cases:
- **Comments on a blog post** - no post = no comments
- **Order items in an order** - no order = no items
- **Messages in a chat room** - room deleted = messages gone
- **Chapters in a book** - book deleted = chapters gone

### SQL equivalent:
```sql
CREATE TABLE comment (
    id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    text TEXT,
    FOREIGN KEY (post_id) REFERENCES blogpost(id) ON DELETE CASCADE
);
```

---

## 2. PROTECT - "Block deletion strictly"

### Example: Author and Books

```python
from django.db import models
from django.db.models import ProtectedError

class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        Author, 
        on_delete=models.PROTECT  # ← PROTECT
    )
```

### What happens:

```python
# Create author with books
author = Author.objects.create(name="J.K. Rowling")
Book.objects.create(title="Harry Potter 1", author=author)
Book.objects.create(title="Harry Potter 2", author=author)

# Try to delete the author
try:
    author.delete()
except ProtectedError as e:
    print("ERROR: Cannot delete! Books still reference this author.")
    # ❌ BLOCKED! Raises ProtectedError

# You MUST delete books first
Book.objects.filter(author=author).delete()
author.delete()  # ✅ NOW it works
```

### Real-world use cases:
- **Author with books** - can't delete author while books exist
- **Category with products** - protect categories in use
- **Currency with transactions** - can't delete USD while transactions use it
- **Department with employees** - can't delete department with staff

### SQL equivalent:
```sql
CREATE TABLE book (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    author_id INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES author(id) ON DELETE RESTRICT
);
-- Note: SQL RESTRICT is similar to Django PROTECT
```

---

## 3. RESTRICT - "Block deletion smartly"

### Example: Company and Employees

```python
from django.db import models
from django.db.models import RestrictedError

class Company(models.Model):
    name = models.CharField(max_length=100)

class Employee(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(
        Company, 
        on_delete=models.RESTRICT  # ← RESTRICT
    )
```

### What happens:

```python
# Create company with employees
company = Company.objects.create(name="TechCorp")
emp1 = Employee.objects.create(name="Alice", company=company)
emp2 = Employee.objects.create(name="Bob", company=company)

# Try to delete the company
try:
    company.delete()
except RestrictedError as e:
    print("ERROR: Cannot delete! Employees still reference this company.")
    # ❌ BLOCKED! Raises RestrictedError
```

---

## PROTECT vs RESTRICT: What's the difference?

Both block deletion, but **timing** is different:

### PROTECT - Checks BEFORE any deletion

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.PROTECT)

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

# Scenario:
author = Author.objects.create(name="Author")
book = Book.objects.create(title="Book", author=author)
chapter = Chapter.objects.create(title="Ch1", book=book)

# Try to delete book
book.delete()  # ✅ SUCCESS! Chapter is CASCADE deleted, no PROTECT error
```

### RESTRICT - Checks AFTER cascade operations

```python
class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.RESTRICT)

class Chapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

# Same scenario:
author = Author.objects.create(name="Author")
book = Book.objects.create(title="Book", author=author)
chapter = Chapter.objects.create(title="Ch1", book=book)

# Try to delete author
author.delete()  # ❌ RESTRICT error! Book still exists even after cascade checks
```

**Key difference:**
- **PROTECT**: "Stop immediately if ANY child exists"
- **RESTRICT**: "Stop if children exist AFTER cascade deletions"

In practice, **PROTECT is more commonly used** and safer.

---

## Side-by-side comparison

```python
# CASCADE Example
class Order(models.Model):
    customer = models.CharField(max_length=100)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.CharField(max_length=100)

order = Order.objects.create(customer="John")
OrderItem.objects.create(order=order, product="Laptop")

order.delete()  # ✅ Order AND OrderItem both deleted
```

```python
# PROTECT Example
class Category(models.Model):
    name = models.CharField(max_length=100)

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)

category = Category.objects.create(name="Electronics")
Product.objects.create(category=category, name="Laptop")

category.delete()  # ❌ ProtectedError! Products still exist
```

---

## Decision Tree: Which one to use?

```
Can child exist without parent?
│
├─ NO (child meaningless without parent)
│  └─ Use CASCADE
│     Examples: Comments on post, Order items, Log entries
│
└─ YES (child should survive parent deletion or prevent it)
   │
   ├─ Should deletion be blocked?
   │  └─ Use PROTECT or RESTRICT
   │     Examples: Products in category, Books by author
   │
   └─ Should child be orphaned?
       └─ Use SET_NULL (with null=True)
          Examples: Posts by deleted user → "Anonymous"
```

---

## Other options (bonus)

### SET_NULL - Orphan the children
```python
class User(models.Model):
    username = models.CharField(max_length=100)

class Post(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True  # Required!
    )
    content = models.TextField()

user = User.objects.create(username="alice")
post = Post.objects.create(author=user, content="Hello")

user.delete()  # ✅ User deleted, post.author becomes NULL
print(post.author)  # → None
```

### SET_DEFAULT - Set to default value
```python
class Status(models.Model):
    name = models.CharField(max_length=50)

class Task(models.Model):
    status = models.ForeignKey(
        Status,
        on_delete=models.SET_DEFAULT,
        default=1  # Required!
    )
    title = models.CharField(max_length=200)

status_active = Status.objects.create(id=1, name="Active")
status_review = Status.objects.create(id=2, name="Review")
task = Task.objects.create(title="Fix bug", status=status_review)

status_review.delete()  # ✅ Deleted, task.status → status_active
```

### SET() - Custom function
```python
def get_default_category():
    return Category.objects.get(name="Uncategorized").id

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET(get_default_category)
    )
```

### DO_NOTHING - Dangerous! (not recommended)
```python
class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.DO_NOTHING)

author = Author.objects.create(name="Author")
book = Book.objects.create(author=author)

author.delete()  # ✅ Deleted, but book.author_id still points to deleted ID!
# This creates database integrity issues! Avoid unless you know what you're doing.
```

---

## Summary Chart

| Scenario | Best Option | Why |
|----------|-------------|-----|
| Comments on blog post | CASCADE | Comments meaningless without post |
| Order items in order | CASCADE | Items can't exist without order |
| Products in category | PROTECT | Prevent accidental category deletion |
| Books by author | PROTECT | Keep author if books exist |
| Posts by user (deleted account) | SET_NULL | Show posts as "Anonymous" |
| Tasks with status (status deleted) | SET_DEFAULT | Move to default status |
| Audit logs | CASCADE | Logs belong to the entity |

**Rule of thumb:** Use CASCADE when child can't exist independently, use PROTECT when you want safety checks!