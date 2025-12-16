# Reset Submissions to Pending

## ✅ Command Executed Successfully!

All submissions have been reset to **pending** status, as if they were just submitted by vendors.

---

## What Happened

### **Before:**
- Some submissions were: ✅ Approved
- Some submissions were: ❌ Rejected
- Some submissions were: ⏳ Pending

### **After:**
- **ALL submissions are now**: ⏳ Pending
- **Verified by**: Cleared (set to None)
- **Verification notes**: Cleared (empty)

---

## Results

```
✅ Successfully reset 14 submission(s) to pending status.

📊 Summary:
   Total submissions: 14
   Reset to pending: 14

✨ All submissions are now in "pending" state, ready for finance review!
```

---

## What This Means

### **For Vendors:**
- All submissions show as "Pending" in their dashboard
- Waiting for finance team review
- Cannot edit or resubmit (pending review)

### **For Finance Team:**
- All 14 submissions appear in "Pending" list
- Can approve or reject each one
- Can click Extract button on any submission (after approving)

---

## How to Use the Command Again

If you need to reset submissions again in the future:

```powershell
# Run this command:
.\venv\Scripts\python manage.py reset_submissions
```

This will:
- Reset all submissions to pending
- Clear verification status
- Clear verification notes

---

## Testing the Reset

### **Step 1: Check Vendor Dashboard**

1. Login as a vendor
2. Go to: http://localhost:8000/vendors/dashboard/
3. See all submissions with status: ⏳ Pending

### **Step 2: Check Finance Dashboard**

1. Login as finance user
2. Go to: http://localhost:8000/finance/dashboard/
3. See statistics:
   - Pending: 14
   - Approved: 0
   - Rejected: 0

### **Step 3: Check Submissions List**

1. Go to: http://localhost:8000/finance/submissions_list/
2. See all 14 submissions with:
   - Status badge: ⏳ Pending
   - Action buttons: ✓ Approve | ✗ Reject

---

## Workflow Now

### **1. Finance Reviews Submission**
- Click "Submissions List"
- Review each pending submission
- Click ✓ Approve or ✗ Reject

### **2. After Approval**
- Submission status changes to: ✅ Approved
- Extract button appears: 🔍 Extract
- Click Extract to process invoice

### **3. Extraction Process**
- Invoice sent to n8n
- Data extracted
- Axpert data fetched (if Oracle configured)
- Results displayed on one page

---

## Command Details

### **File Created:**
`vendors/management/commands/reset_submissions.py`

### **What It Does:**
```python
# Resets all submissions to pending
submissions.update(
    status='pending',
    verified_by=None,
    verification_notes='',
)
```

### **Safe to Run:**
- ✅ Does not delete any data
- ✅ Does not delete submissions
- ✅ Does not delete documents
- ✅ Only changes status fields

---

## Next Steps

1. ✅ **Submissions are reset** (already done!)
2. ⏳ **Login as finance user**
3. ⏳ **Review and approve submissions**
4. ⏳ **Test Extract button** on approved submissions
5. ⏳ **Verify results page** shows all data

---

## Quick Commands

### **Reset all submissions to pending:**
```powershell
.\venv\Scripts\python manage.py reset_submissions
```

### **Check database:**
```powershell
.\venv\Scripts\python manage.py shell
```
```python
from vendors.models import Submission
print(f"Pending: {Submission.objects.filter(status='pending').count()}")
print(f"Approved: {Submission.objects.filter(status='approved').count()}")
print(f"Rejected: {Submission.objects.filter(status='rejected').count()}")
```

---

**Status**: ✅ All submissions reset to pending  
**Date**: 2025-12-08  
**Total**: 14 submissions  
**Ready**: For finance team review!
