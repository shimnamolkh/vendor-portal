# Dashboard Click Error - Troubleshooting

## Issue

When clicking on the statistics in the Finance Dashboard:
- Clicking "13 entries" → Error
- Clicking "5 approved" → Error

## Possible Causes

### 1. **Django Server Not Fully Started**
The server might still be loading. Wait a few seconds after seeing:
```
Starting development server at http://127.0.0.1:8000/
```

### 2. **Browser Cache**
Clear browser cache and refresh:
- Press `Ctrl+Shift+R` (hard refresh)
- Or clear browser cache completely

### 3. **Check Django Terminal for Error**
Look at the Django terminal for the actual error message. It should show something like:
```
[08/Dec/2025 15:26:00] "GET /finance/submissions/?type=inward HTTP/1.1" 500
```

## Quick Fixes

### **Fix 1: Restart Django Server**

```powershell
# In Django terminal:
# Press Ctrl+C, then:
.\venv\Scripts\python manage.py runserver
```

Wait for:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

Then try clicking again.

### **Fix 2: Clear Browser Cache**

1. Press `Ctrl+Shift+Delete`
2. Select "Cached images and files"
3. Click "Clear data"
4. Refresh page with `Ctrl+F5`

### **Fix 3: Check URL Manually**

Try accessing the URLs directly:

1. **All Inward Submissions**:
   ```
   http://localhost:8000/finance/submissions/?type=inward
   ```

2. **Approved Inward**:
   ```
   http://localhost:8000/finance/submissions/?type=inward&status=approved
   ```

3. **All Direct Purchase**:
   ```
   http://localhost:8000/finance/submissions/?type=direct
   ```

If these work, the issue is with the dashboard links.

### **Fix 4: Check for JavaScript Errors**

1. Press `F12` to open browser console
2. Go to "Console" tab
3. Look for any red error messages
4. Share the error if you see one

## Expected Behavior

When clicking on statistics, you should:

1. Click "13" (Total Entries) → See all 13 submissions
2. Click "8" (Pending) → See only pending submissions
3. Click "5" (Approved) → See only approved submissions
4. Click "0" (Rejected) → See only rejected submissions

## Testing Steps

### **Step 1: Verify Server is Running**

Check Django terminal shows:
```
Watching for file changes with StatReloader
Performing system checks...
System check identified no issues (0 silenced).
December 08, 2025 - 15:24:20
Django version 5.2.8, using settings 'vendor_portal.settings'
Starting development server at http://127.0.0.1:8000/
```

### **Step 2: Access Dashboard**

Go to: http://localhost:8000/finance/dashboard/

Should see:
- Supplier Inward card with statistics
- Direct Purchase card with statistics

### **Step 3: Click Statistics**

Click on any number in the statistics.

**If it works**: You'll see the submissions list filtered correctly.

**If it doesn't work**: Check the Django terminal for error message.

## Common Errors and Solutions

### **Error: "NoReverseMatch"**
**Cause**: URL pattern not found

**Solution**: Check `finance/urls.py` has:
```python
path('submissions/', views.submissions_list, name='submissions_list'),
```

### **Error**: "TemplateDoesNotExist"
**Cause**: Template file missing

**Solution**: Check file exists:
```
templates/finance/submissions_list.html
```

### **Error**: "AttributeError"
**Cause**: View function issue

**Solution**: Check `finance/views.py` has `submissions_list` function

## Debug Information to Collect

If the error persists, collect this information:

1. **Django Terminal Output**:
   - Copy the error message from terminal
   - Include the full traceback

2. **Browser Console**:
   - Press F12
   - Go to Console tab
   - Copy any error messages

3. **URL Being Accessed**:
   - What URL shows in browser address bar when error occurs

4. **Screenshot**:
   - Screenshot of the error page

## Quick Test

Run this in a new terminal to test the URLs:

```powershell
# Test all submissions
Invoke-WebRequest -Uri "http://localhost:8000/finance/submissions/" -UseBasicParsing

# Test filtered submissions
Invoke-WebRequest -Uri "http://localhost:8000/finance/submissions/?type=inward&status=approved" -UseBasicParsing
```

If these return 200 OK, the URLs are working.

## Next Steps

1. ✅ Restart Django server
2. ✅ Clear browser cache
3. ✅ Try accessing URLs manually
4. ✅ Check Django terminal for errors
5. ✅ Share error message if persists

---

**Status**: Troubleshooting  
**Date**: 2025-12-08  
**Issue**: Dashboard statistics clicks showing error  
**Next**: Collect error details from Django terminal
