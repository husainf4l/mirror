# Code Fixes for Guest Management Issues

This document contains ready-to-implement code fixes for the identified issues.

---

## Fix 1: Add Input Validation to Update Endpoint

**File:** `/backend/app/api/v1/api.py`  
**Location:** Lines 569-621 (update_guest function)

### Current Code Issue
No validation for required fields or phone uniqueness.

### Fixed Code

```python
@api_router.put("/guests/{guest_id}")
def update_guest(guest_id: int, request: Request, authenticated: bool = Depends(require_auth)):
    """Update an existing guest with proper validation"""
    try:
        import json
        body = asyncio.run(request.body())
        data = json.loads(body.decode())
        
        # === NEW: Input Validation ===
        # Validate required fields
        if 'first_name' in data and not data['first_name'].strip():
            return JSONResponse({
                "success": False,
                "message": "First name cannot be empty"
            }, status_code=400)
            
        if 'last_name' in data and not data['last_name'].strip():
            return JSONResponse({
                "success": False,
                "message": "Last name cannot be empty"
            }, status_code=400)
        
        # Validate phone format (if provided)
        if data.get("phone"):
            phone = data["phone"].strip()
            # Remove spaces and dashes for validation
            clean_phone = phone.replace(" ", "").replace("-", "")
            if not clean_phone.replace("+", "").isdigit():
                return JSONResponse({
                    "success": False,
                    "message": "Invalid phone number format"
                }, status_code=400)
        
        # Validate field lengths
        if 'first_name' in data and len(data['first_name']) > 100:
            return JSONResponse({
                "success": False,
                "message": "First name too long (max 100 characters)"
            }, status_code=400)
            
        if 'last_name' in data and len(data['last_name']) > 100:
            return JSONResponse({
                "success": False,
                "message": "Last name too long (max 100 characters)"
            }, status_code=400)
        # === END NEW ===
        
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import Guest
        
        # Find the guest
        guest = session.query(Guest).filter_by(id=guest_id).first()
        if not guest:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Guest not found"
            }, status_code=404)
        
        # === NEW: Check phone uniqueness ===
        if data.get("phone") and data["phone"] != guest.phone:
            existing_phone = session.query(Guest).filter(
                Guest.phone == data["phone"],
                Guest.id != guest_id
            ).first()
            if existing_phone:
                session.close()
                return JSONResponse({
                    "success": False,
                    "message": f"Phone number already registered to {existing_phone.first_name} {existing_phone.last_name}"
                }, status_code=400)
        # === END NEW ===
        
        # Update guest fields with strip() to remove whitespace
        guest.first_name = data.get("first_name", guest.first_name).strip() if data.get("first_name") else guest.first_name
        guest.last_name = data.get("last_name", guest.last_name).strip() if data.get("last_name") else guest.last_name
        guest.phone = data.get("phone", guest.phone)
        guest.seat_number = data.get("seat_number", guest.seat_number)
        guest.relation = data.get("relation", guest.relation)
        guest.relation_type_id = data.get("relation_type_id", guest.relation_type_id)
        guest.message = data.get("message", guest.message)
        guest.story = data.get("story", guest.story)
        guest.about = data.get("about", guest.about)
        guest.updated_at = datetime.utcnow()
        
        session.commit()
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Guest updated successfully"
        })
        
    except Exception as e:
        print(f"Error updating guest: {e}")
        return JSONResponse({
            "success": False,
            "message": "An error occurred while updating the guest"
        }, status_code=500)
```

---

## Fix 2: Add Duplicate Detection to Excel Import

**File:** `/backend/app/api/v1/api.py`  
**Location:** Lines 668-698 (import_guests_excel function)

### Current Code Issue
No duplicate detection - can import same guest multiple times.

### Fixed Code

Replace the for loop in import_guests_excel with this:

```python
        imported_count = 0
        skipped_count = 0
        updated_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # === NEW: Extract and clean data ===
                first_name = str(row.get("First Name", "")).strip()
                last_name = str(row.get("Last Name", "")).strip()
                phone = str(row.get("Phone", "")).strip() if pd.notna(row.get("Phone")) else None
                
                # Skip if no name
                if not first_name or not last_name:
                    errors.append(f"Row {index + 2}: Missing required fields (first name or last name)")
                    continue
                
                # === NEW: Check for duplicates ===
                # Strategy 1: Check by phone if provided
                existing_guest = None
                if phone:
                    existing_guest = session.query(Guest).filter(
                        Guest.phone == phone
                    ).first()
                
                # Strategy 2: Check by full name if no phone match
                if not existing_guest:
                    existing_guest = session.query(Guest).filter(
                        Guest.first_name.ilike(first_name),
                        Guest.last_name.ilike(last_name)
                    ).first()
                
                # If duplicate found, update instead of insert
                if existing_guest:
                    # Update existing guest
                    existing_guest.phone = phone or existing_guest.phone
                    existing_guest.seat_number = str(row.get("Seat Number", "")).strip() if pd.notna(row.get("Seat Number")) else existing_guest.seat_number
                    existing_guest.relation = str(row.get("Relation", "")).strip() if pd.notna(row.get("Relation")) else existing_guest.relation
                    existing_guest.message = str(row.get("Message", "")).strip() if pd.notna(row.get("Message")) else existing_guest.message
                    existing_guest.story = str(row.get("Story", "")).strip() if pd.notna(row.get("Story")) else existing_guest.story
                    existing_guest.about = str(row.get("About", "")).strip() if pd.notna(row.get("About")) else existing_guest.about
                    existing_guest.updated_at = datetime.utcnow()
                    updated_count += 1
                    continue
                # === END NEW ===
                
                # Map relation type name to ID
                relation_type_id = None
                if pd.notna(row.get("Relation Type", "")):
                    relation_type_id = relation_types.get(str(row["Relation Type"]))
                
                # Create new guest
                new_guest = Guest(
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    seat_number=str(row.get("Seat Number", "")).strip() if pd.notna(row.get("Seat Number")) else None,
                    relation=str(row.get("Relation", "")).strip() if pd.notna(row.get("Relation")) else None,
                    relation_type_id=relation_type_id,
                    message=str(row.get("Message", "")).strip() if pd.notna(row.get("Message")) else None,
                    story=str(row.get("Story", "")).strip() if pd.notna(row.get("Story")) else None,
                    about=str(row.get("About", "")).strip() if pd.notna(row.get("About")) else None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(new_guest)
                imported_count += 1
                
            except Exception as row_error:
                errors.append(f"Row {index + 2}: {str(row_error)}")
        
        if imported_count > 0 or updated_count > 0:
            session.commit()
        
        session.close()
        
        # === NEW: Enhanced response message ===
        message_parts = []
        if imported_count > 0:
            message_parts.append(f"imported {imported_count} new guests")
        if updated_count > 0:
            message_parts.append(f"updated {updated_count} existing guests")
        if skipped_count > 0:
            message_parts.append(f"skipped {skipped_count} duplicates")
            
        message = "Successfully " + ", ".join(message_parts) if message_parts else "No changes made"
        # === END NEW ===
        
        return JSONResponse({
            "success": True,
            "message": message,
            "imported_count": imported_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "errors": errors
        })
```

---

## Fix 3: Add File Upload Validation

**File:** `/backend/app/api/v1/api.py`  
**Location:** Lines 668-698 (import_guests_excel function)

### Current Code Issue
No file size or type validation.

### Fixed Code

Add this validation at the beginning of `import_guests_excel`:

```python
@api_router.post("/guests/import")
def import_guests_excel(request: Request, authenticated: bool = Depends(require_auth)):
    """Import guests from Excel file with validation"""
    try:
        import pandas as pd
        import base64
        from io import BytesIO
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime
        import json
        
        body = asyncio.run(request.body())
        data = json.loads(body.decode())
        
        # Get the base64 encoded file
        file_content = data.get("file_content")
        if not file_content:
            return JSONResponse({
                "success": False,
                "message": "No file content provided"
            }, status_code=400)
        
        # === NEW: File validation ===
        # Check if it's a valid base64 data URL
        if not file_content.startswith('data:'):
            return JSONResponse({
                "success": False,
                "message": "Invalid file format"
            }, status_code=400)
        
        # Extract MIME type and data
        try:
            header, encoded = file_content.split(',', 1)
            mime_type = header.split(':')[1].split(';')[0]
        except:
            return JSONResponse({
                "success": False,
                "message": "Invalid file encoding"
            }, status_code=400)
        
        # Validate MIME type
        allowed_types = [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
            'application/vnd.ms-excel',  # .xls
        ]
        
        if mime_type not in allowed_types:
            return JSONResponse({
                "success": False,
                "message": f"Invalid file type: {mime_type}. Please upload an Excel file (.xlsx or .xls)"
            }, status_code=400)
        
        # Decode and check file size
        try:
            file_bytes = base64.b64decode(encoded)
        except:
            return JSONResponse({
                "success": False,
                "message": "Failed to decode file"
            }, status_code=400)
        
        # Check file size (5MB limit)
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        file_size = len(file_bytes)
        
        if file_size > MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return JSONResponse({
                "success": False,
                "message": f"File too large ({size_mb:.2f}MB). Maximum size is 5MB"
            }, status_code=400)
        
        if file_size == 0:
            return JSONResponse({
                "success": False,
                "message": "File is empty"
            }, status_code=400)
        # === END NEW ===
        
        excel_buffer = BytesIO(file_bytes)
        
        # === NEW: Try to read Excel with error handling ===
        try:
            df = pd.read_excel(excel_buffer)
        except Exception as excel_error:
            return JSONResponse({
                "success": False,
                "message": f"Failed to read Excel file: {str(excel_error)}"
            }, status_code=400)
        
        # Validate DataFrame
        if df.empty:
            return JSONResponse({
                "success": False,
                "message": "Excel file is empty"
            }, status_code=400)
        
        # Check for required columns
        required_columns = ["First Name", "Last Name"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return JSONResponse({
                "success": False,
                "message": f"Missing required columns: {', '.join(missing_columns)}"
            }, status_code=400)
        
        # Check row count
        if len(df) > 10000:
            return JSONResponse({
                "success": False,
                "message": f"Too many rows ({len(df)}). Maximum is 10,000 rows"
            }, status_code=400)
        # === END NEW ===
        
        # ... rest of the import logic ...
```

---

## Fix 4: Remove Phone Unique Constraint

**File:** `/backend/models.py`  
**Location:** Line 19

### Current Code
```python
phone = Column(String(20), nullable=True, unique=True)
```

### Fixed Code
```python
phone = Column(String(20), nullable=True, unique=False)
```

### Migration Required

Create a migration file:

```bash
# In terminal
cd /home/husain/Desktop/mirror
source venv/bin/activate
alembic revision -m "remove_phone_unique_constraint"
```

Then edit the migration file:

```python
def upgrade():
    op.drop_constraint('guests_phone_key', 'guests', type_='unique')

def downgrade():
    op.create_unique_constraint('guests_phone_key', 'guests', ['phone'])
```

Run migration:

```bash
alembic upgrade head
```

---

## Fix 5: Add Soft Delete

**File:** `/backend/models.py`

### Add field to Guest model

```python
class Guest(Base):
    __tablename__ = "guests"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False, index=True)
    last_name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), nullable=True, unique=False)
    seat_number = Column(String(10), nullable=True)
    relation = Column(String(100), nullable=True)
    relation_type_id = Column(Integer, ForeignKey("relation_types.id"), nullable=True)
    message = Column(Text, nullable=True)
    story = Column(Text, nullable=True)
    about = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)  # === NEW ===
    
    # Relationship
    relation_type = relationship("RelationType", back_populates="guests")
    
    # === NEW: Add property to check if deleted ===
    @property
    def is_deleted(self):
        return self.deleted_at is not None
    # === END NEW ===
```

### Update Delete Endpoint

**File:** `/backend/app/api/v1/api.py`

```python
@api_router.delete("/guests/{guest_id}")
def delete_guest(guest_id: int, authenticated: bool = Depends(require_auth)):
    """Soft delete a guest"""
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os
        from datetime import datetime  # === NEW ===
        
        database_url = os.getenv("DATABASE_URL")
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        engine = create_engine(sync_database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from models import Guest
        
        # Find the guest
        guest = session.query(Guest).filter_by(id=guest_id).first()
        if not guest:
            session.close()
            return JSONResponse({
                "success": False,
                "message": "Guest not found"
            }, status_code=404)
        
        # === NEW: Soft delete instead of hard delete ===
        guest.deleted_at = datetime.utcnow()
        session.commit()
        # === END NEW ===
        
        # OLD: session.delete(guest)
        
        session.close()
        
        return JSONResponse({
            "success": True,
            "message": "Guest deleted successfully"
        })
        
    except Exception as e:
        print(f"Error deleting guest: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Error deleting guest: {str(e)}"
        }, status_code=500)
```

### Update List Guests Endpoint

Filter out deleted guests:

```python
@api_router.get("/guests")
def list_guests(authenticated: bool = Depends(require_auth)):
    """Get all non-deleted guests from the database"""
    try:
        # ... database connection code ...
        
        # === NEW: Filter out deleted guests ===
        guests = session.query(Guest).filter(
            Guest.deleted_at.is_(None)
        ).join(RelationType, Guest.relation_type_id == RelationType.id, isouter=True).all()
        # === END NEW ===
        
        # ... rest of the code ...
```

---

## Fix 6: Frontend File Validation

**File:** `/livekit-react/src/components/GuestManagement.tsx`  
**Location:** handleImportExcel function (around line 208)

### Current Code Issue
No client-side validation.

### Fixed Code

```typescript
const handleImportExcel = async (e: React.ChangeEvent<HTMLInputElement>) => {
  const file = e.target.files?.[0];
  if (!file) return;

  // === NEW: Client-side validation ===
  // Check file type
  const allowedTypes = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
    'application/vnd.ms-excel' // .xls
  ];
  
  if (!allowedTypes.includes(file.type)) {
    showMessage('Invalid file type. Please upload an Excel file (.xlsx or .xls)', 'error');
    e.target.value = '';
    return;
  }
  
  // Check file size (5MB limit)
  const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
  if (file.size > MAX_FILE_SIZE) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    showMessage(`File too large (${sizeMB}MB). Maximum size is 5MB`, 'error');
    e.target.value = '';
    return;
  }
  
  if (file.size === 0) {
    showMessage('File is empty', 'error');
    e.target.value = '';
    return;
  }
  // === END NEW ===

  try {
    const reader = new FileReader();
    reader.onload = async (event) => {
      const fileContent = event.target?.result as string;
      
      const response = await fetch('/api/guests/import', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          file_content: fileContent
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // === NEW: Show detailed success message ===
        let message = 'Import completed: ';
        const details = [];
        if (data.imported_count > 0) details.push(`${data.imported_count} imported`);
        if (data.updated_count > 0) details.push(`${data.updated_count} updated`);
        if (data.skipped_count > 0) details.push(`${data.skipped_count} skipped`);
        message += details.join(', ');
        showMessage(message, 'success');
        // === END NEW ===
        
        await fetchGuests();
      } else {
        showMessage(data.message || 'Import failed', 'error');
      }
    };
    
    // === NEW: Add error handler ===
    reader.onerror = () => {
      showMessage('Failed to read file', 'error');
    };
    // === END NEW ===
    
    reader.readAsDataURL(file);
  } catch (error) {
    showMessage('Error importing guests', 'error');
  }
  
  // Reset file input
  e.target.value = '';
};
```

---

## Fix 7: Add Agent Update Functions

**File:** `/agent/tools/agent_functions.py`

### Add these new functions:

```python
@function_tool
async def update_guest_seat(guest_name: str, new_seat: str) -> str:
    """Update a guest's seat number in the wedding database."""
    print(f"[DEBUG] update_guest_seat called: {guest_name} -> seat {new_seat}")
    
    # First search for the guest
    url = "http://localhost:8000/api/guest/search"
    
    try:
        payload = {"name": guest_name.strip()}
        
        async with aiohttp.ClientSession() as session:
            # Search for guest
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    return f"Failed to find guest {guest_name}"
                
                import json
                guest_data = json.loads(await response.text())
                
                if not guest_data.get("found"):
                    return f"Guest {guest_name} not found in database"
                
                guest_info = guest_data.get("guest", {})
                guest_id = guest_info.get("id")
                
                if not guest_id:
                    return f"Could not get guest ID for {guest_name}"
                
                # Update the seat
                update_url = f"http://localhost:8000/api/guests/{guest_id}"
                update_payload = {"seat_number": new_seat}
                
                async with session.put(
                    update_url,
                    json=update_payload,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as update_response:
                    
                    update_data = json.loads(await update_response.text())
                    
                    if update_response.status == 200 and update_data.get("success"):
                        full_name = guest_info.get("name", guest_name)
                        return f"Successfully updated {full_name}'s seat to {new_seat}"
                    else:
                        error_msg = update_data.get("message", "Unknown error")
                        return f"Failed to update seat: {error_msg}"
                        
    except aiohttp.ClientError as e:
        print(f"[DEBUG] Client error: {e}")
        return f"Cannot connect to backend. Is it running?"
    except Exception as e:
        print(f"[DEBUG] Exception: {str(e)}")
        return f"Error updating guest: {str(e)}"


@function_tool
async def update_guest_phone(guest_name: str, new_phone: str) -> str:
    """Update a guest's phone number in the wedding database."""
    print(f"[DEBUG] update_guest_phone called: {guest_name} -> {new_phone}")
    
    # Similar implementation to update_guest_seat
    # ... (follow same pattern)
```

---

## Testing Checklist

After implementing these fixes, test the following:

### Update Guest Tests
- [ ] Update guest with valid data
- [ ] Try to update with empty name (should fail)
- [ ] Try to update with duplicate phone (should fail)
- [ ] Update guest with special characters in name
- [ ] Update guest with very long name (should fail)

### Delete Guest Tests
- [ ] Delete guest (should soft delete)
- [ ] Verify deleted guest not in list
- [ ] Check database - deleted_at should be set
- [ ] Try to delete same guest again (should fail)

### Excel Import Tests
- [ ] Import file with new guests
- [ ] Import file with duplicate guests (should update)
- [ ] Import file > 5MB (should fail)
- [ ] Import wrong file type (should fail)
- [ ] Import file with missing columns (should fail)

### Agent Tests
- [ ] Update guest seat via agent
- [ ] Update guest phone via agent
- [ ] Try to update non-existent guest

---

## Deployment Instructions

1. **Backup Database:**
   ```bash
   pg_dump wedding_mirror > backup_$(date +%Y%m%d).sql
   ```

2. **Apply Code Changes:**
   ```bash
   git pull origin main
   ```

3. **Run Database Migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Restart Services:**
   ```bash
   # Backend
   systemctl restart wedding-mirror-api
   
   # Agent
   systemctl restart wedding-mirror-agent
   
   # Frontend
   npm run build
   systemctl restart nginx
   ```

5. **Verify:**
   - [ ] Backend health check: `curl http://localhost:8000/api/`
   - [ ] Frontend loads: `http://localhost:3000`
   - [ ] Agent connects: Check logs

---

**End of Code Fixes Document**
