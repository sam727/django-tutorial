from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower, Upper

class User(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    class Meta:
        indexes = [
            # Index on lowercase username (case-insensitive search)
            models.Index(Lower('username'), name='username_lower_idx'),
            
            # Index on uppercase email
            models.Index(Upper('email'), name='email_upper_idx'),
            
            # Index on expression
            models.Index(
                F('first_name') + F('last_name'),
                name='full_name_idx'
            ),
            
            
            
            # Index on single field
            models.Index(fields=['title']),
            
            # Index on multiple fields (composite index)
            models.Index(fields=['author', '-published_date']),
            
            
            models.Index(
                fields=['title'],
                name='book_title_large_idx',
                condition=Q(pages__gt=400),
            ),
        ]
        


class MyModel(models.Model):
    field1 = models.CharField(max_length=100)
    field2 = models.IntegerField()
    field3 = models.DateField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(
                fields=['field1', '-field2'],  # Ascending field1, descending field2
                name='custom_index_name',       # Custom name (max 30 chars)
                db_tablespace='fast_indexes',   # Custom tablespace
                condition=Q(is_active=True),    # Partial index (PostgreSQL)
                opclasses=['varchar_pattern_ops', 'int4_ops'],  # PostgreSQL operator classes
            ),
        ]
        