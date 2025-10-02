# 🚀 Quick Start: What Changed & How to Deploy

## ✅ All Fixes Applied!

### What's Fixed:
1. ✅ Phone numbers - no more unique constraint
2. ✅ Soft delete - guests are hidden, not destroyed
3. ✅ Import duplicates - updates instead of creating copies
4. ✅ Input validation - no empty names
5. ✅ Agent updates - voice-activated guest management
6. ✅ Better statistics - see imported, updated, skipped counts

---

## 🔧 Deploy in 3 Steps:

### Step 1: Database Migration
```bash
cd /home/husain/Desktop/mirror
source venv/bin/activate

# Quick method (development):
psql -d wedding_mirror -c "ALTER TABLE guests DROP CONSTRAINT IF EXISTS guests_phone_key;"
psql -d wedding_mirror -c "ALTER TABLE guests ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP;"
```

### Step 2: Restart Backend
```bash
# Kill old process
pkill -f "uvicorn backend.app.main"

# Start new
cd /home/husain/Desktop/mirror
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
```

### Step 3: Restart Agent
```bash
# Kill old process
pkill -f "agent.py"

# Start new
cd /home/husain/Desktop/mirror/agent
source ../venv/bin/activate
python agent.py dev &
```

---

## 🧪 Quick Test:

```bash
# Test 1: Import with duplicates
# - Go to http://localhost:3000/guests
# - Upload an Excel file twice
# - Should see "updated X existing guests"

# Test 2: Soft delete
# - Delete a guest
# - Check database: SELECT * FROM guests WHERE deleted_at IS NOT NULL;
# - Guest should still exist with deleted_at timestamp

# Test 3: Phone sharing
# - Create two guests with same phone
# - Both should save successfully

# Test 4: Agent updates
# - Say "Update [guest name]'s seat to table 5"
# - Agent should confirm update
```

---

## 📋 What Each File Does Now:

### `/backend/models.py`
- `phone` → No longer unique (families can share)
- `deleted_at` → New field for soft delete
- `is_deleted` → Property to check if deleted

### `/backend/app/api/v1/api.py`
- **Guest search** → Returns ID (agent needs this)
- **List guests** → Filters out deleted guests
- **Delete guest** → Sets deleted_at instead of removing
- **Update guest** → Validates empty names
- **Import Excel** → Checks for duplicates, updates if found
- **Export Excel** → Excludes deleted guests

### `/livekit-react/src/components/GuestManagement.tsx`
- **Import success** → Shows detailed stats (imported, updated, skipped)

### `/agent/tools/agent_functions.py`
- **update_guest_seat()** → NEW! Voice-activated seat updates
- **update_guest_phone()** → NEW! Voice-activated phone updates

---

## 💡 Common Issues & Fixes:

### "Phone already exists" error
**Fixed!** Multiple guests can now share phone numbers.

### Imported duplicates
**Fixed!** Import now updates existing guests instead of creating duplicates.

### Can't find deleted guest
**Working as intended!** Deleted guests are hidden. Check database directly if needed:
```sql
SELECT * FROM guests WHERE deleted_at IS NOT NULL;
```

### Agent can't update
**Fixed!** Agent now has `update_guest_seat()` and `update_guest_phone()` functions.

### Empty names saved
**Fixed!** Update endpoint now validates that names aren't empty.

---

## 📊 Before vs After:

| Feature | Before | After |
|---------|--------|-------|
| Duplicate phones | ❌ Error | ✅ Allowed |
| Delete guest | ❌ Permanent | ✅ Soft delete |
| Import duplicates | ❌ Creates copies | ✅ Updates existing |
| Empty name update | ❌ Saved | ✅ Rejected |
| Agent updates | ❌ Read-only | ✅ Can update |
| Import stats | 🟡 Basic | ✅ Detailed |

---

## 🎯 Test Scenarios:

```
✓ Create guest "John Doe" with phone "123-456-7890"
✓ Create guest "Jane Doe" with phone "123-456-7890" → Both exist
✓ Update John's name to "" → Error
✓ Update John's name to "Jonathan" → Success
✓ Delete Jane → Hidden from list
✓ Export guests → Jane not in export
✓ Import Excel with John (existing) → Updates John, not duplicate
✓ Say to agent: "Update John's seat to B5" → Success
✓ Say to agent: "Change John's phone to 999-888-7777" → Success
```

---

## 🔍 Verify It's Working:

### Check Soft Delete:
```sql
-- See all guests including deleted
SELECT first_name, last_name, deleted_at FROM guests;

-- See only active guests (what API returns)
SELECT first_name, last_name FROM guests WHERE deleted_at IS NULL;
```

### Check Phone Constraint:
```sql
-- Try to insert duplicate phones (should work now)
INSERT INTO guests (first_name, last_name, phone) 
VALUES ('Test1', 'User1', '000-000-0000'),
       ('Test2', 'User2', '000-000-0000');
-- Should succeed!
```

### Check Agent Functions:
```bash
# Look at agent log when it starts
grep -i "update_guest" agent.log
# Should see the new functions registered
```

---

## 🐛 Troubleshooting:

### Backend won't start
```bash
# Check for errors
tail -f /var/log/wedding-mirror/backend.log

# Or run in foreground to see errors
cd /home/husain/Desktop/mirror
source venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Agent functions not available
```bash
# Make sure agent restarted
ps aux | grep agent.py

# Check agent can import aiohttp
cd /home/husain/Desktop/mirror
source venv/bin/activate
python -c "import aiohttp; print('OK')"
```

### Database migration failed
```bash
# Manual SQL approach
psql -d wedding_mirror

-- Check if deleted_at exists
\d guests

-- Add manually if needed
ALTER TABLE guests ADD COLUMN deleted_at TIMESTAMP;
ALTER TABLE guests DROP CONSTRAINT guests_phone_key;
```

---

## 📞 Quick Reference:

**Backend Port:** 8000  
**Frontend Port:** 3000  
**Database:** wedding_mirror  

**Start Backend:** `uvicorn backend.app.main:app --port 8000`  
**Start Agent:** `python agent.py dev`  
**Start Frontend:** `npm start`  

**Admin URL:** http://localhost:3000/guests  
**API Docs:** http://localhost:8000/docs (if enabled)  

---

## ✨ New Capabilities:

### Voice Commands (Agent):
- "Update [name]'s seat to [seat number]"
- "Change [name]'s phone to [phone number]"
- "Who is [name]?" (still works)
- "Tell me about [name]" (still works)

### Import Behavior:
- Detects duplicates by name or phone
- Updates existing guest data
- Shows detailed statistics
- No more duplicate entries!

### Data Safety:
- Deleted guests recoverable
- Can't accidentally delete important data
- Audit trail maintained

---

**That's it! Your system is upgraded and ready to use! 🎉**

For detailed information, see `FIXES_APPLIED.md`
