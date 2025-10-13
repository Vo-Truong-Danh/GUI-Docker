# 📁 Extract Behavior Update - v5.2.1

## 🎯 What Changed?

### Before (v5.2.0)
Files were extracted to a **subdirectory** with the ZIP filename:
```
/input/                                    ← Upload path
├── mydata.zip                            ← Original ZIP
└── mydata/                               ← Subdirectory created ❌
    ├── file1.csv
    ├── file2.json
    └── data/
        └── file3.txt
```

### After (v5.2.1) ✅
Files are extracted **directly** to the specified upload path:
```
/input/                                    ← Upload path
├── mydata.zip                            ← Original ZIP
├── file1.csv                             ← Files directly here ✅
├── file2.json                            ← No subdirectory!
└── data/                                 ← Structure preserved
    └── file3.txt
```

---

## 📊 Examples

### Example 1: Flat ZIP (no internal folders)
**ZIP content:**
```
mydata.zip
├── file1.csv
├── file2.json
└── file3.txt
```

**Upload to:** `/input`  
**Result:**
```
/input/
├── mydata.zip
├── file1.csv
├── file2.json
└── file3.txt
```
✅ All files directly in `/input/`

---

### Example 2: Nested ZIP (with internal folders)
**ZIP content:**
```
dataset.zip
├── data/
│   ├── train.csv
│   └── test.csv
├── models/
│   └── model.pkl
└── README.txt
```

**Upload to:** `/input`  
**Result:**
```
/input/
├── dataset.zip
├── data/
│   ├── train.csv
│   └── test.csv
├── models/
│   └── model.pkl
└── README.txt
```
✅ Structure preserved, no extra `dataset/` folder

---

### Example 3: Single file in ZIP
**ZIP content:**
```
posts.zip
└── the-antiwork-subreddit-dataset-posts.csv
```

**Upload to:** `/input`  
**Result:**
```
/input/
├── posts.zip
└── the-antiwork-subreddit-dataset-posts.csv
```
✅ File directly in `/input/`, no subdirectory

---

## 🔧 Technical Details

### Code Change
```python
# Before (v5.2.0)
extract_dir_name = filename.rsplit('.zip', 1)[0]
hdfs_target = f"{hdfs_path.rstrip('/')}/{extract_dir_name}"  # Creates subdirectory

# After (v5.2.1)
hdfs_target = hdfs_path.rstrip('/')  # Direct to specified path
```

### Why This Change?
1. **User Expectation:** When specifying `/input`, users expect files in `/input`, not `/input/subdir`
2. **Consistency:** Matches behavior of manual file uploads
3. **Simplicity:** Cleaner HDFS structure
4. **Flexibility:** ZIP structure is preserved if needed

---

## 🎓 Best Practices

### Practice 1: Clean Upload Path
Before uploading, ensure your target path is clean:
```bash
docker exec namenode hdfs dfs -ls /input
```

### Practice 2: Check ZIP Structure
Know what's inside your ZIP before uploading:
- Flat structure → Files go directly to upload path
- Nested structure → Folders are preserved

### Practice 3: Use Meaningful Paths
```bash
# Good
/input/datasets/
/input/raw_data/
/input/processed/

# Avoid
/input/  (everything mixed together)
```

### Practice 4: Archive Strategy
If you want subdirectories, create them **inside the ZIP**:
```
myproject.zip
└── myproject/     ← Create this inside ZIP
    ├── data/
    ├── code/
    └── config/
```

Result in HDFS:
```
/input/
└── myproject/     ← Preserved!
    ├── data/
    ├── code/
    └── config/
```

---

## 🧪 Testing the New Behavior

### Test 1: Upload a Flat ZIP
```python
# Create test ZIP
import zipfile
with zipfile.ZipFile('test.zip', 'w') as zf:
    zf.writestr('file1.txt', 'Test 1')
    zf.writestr('file2.txt', 'Test 2')

# Upload with auto-extract
# Files will be in /input/ directly
```

### Test 2: Upload a Nested ZIP
```python
# Create nested ZIP
import zipfile
with zipfile.ZipFile('nested.zip', 'w') as zf:
    zf.writestr('data/train.csv', 'Training data')
    zf.writestr('data/test.csv', 'Test data')
    zf.writestr('README.txt', 'Info')

# Upload with auto-extract
# Structure preserved: /input/data/, /input/README.txt
```

---

## ⚠️ Important Notes

### Note 1: Original ZIP Kept
The original ZIP file is **always kept** in HDFS after extraction:
```
/input/
├── mydata.zip      ← Original kept
├── file1.csv       ← Extracted
└── file2.csv       ← Extracted
```

If you want to remove it:
```bash
docker exec namenode hdfs dfs -rm /input/mydata.zip
```

### Note 2: Overwrite Existing Files
If files with the same name exist, they will be **overwritten**:
```bash
# Existing
/input/data.csv

# After uploading data.zip containing data.csv
/input/data.csv  ← Overwritten with new content
```

### Note 3: Case Sensitive
HDFS is **case-sensitive**:
```
/input/File.csv  ≠  /input/file.csv
```

---

## 🔄 Migration Guide

### If You Were Using v5.2.0
Your existing files may be in subdirectories:
```
/input/
└── mydata/          ← Old behavior
    ├── file1.csv
    └── file2.csv
```

To move them to root:
```bash
# Method 1: Move files (preferred)
docker exec namenode hdfs dfs -mv /input/mydata/* /input/

# Method 2: Delete and re-upload
docker exec namenode hdfs dfs -rm -r /input/mydata
# Then re-upload ZIP with auto-extract
```

---

## 📊 Comparison Table

| Aspect | v5.2.0 | v5.2.1 |
|--------|--------|--------|
| **Extract Location** | `/input/zipname/` | `/input/` |
| **Subdirectory Created** | Yes ❌ | No ✅ |
| **Structure Preserved** | Yes | Yes |
| **User Expectation** | Confusing | Clear |
| **HDFS Cleanliness** | More folders | Cleaner |

---

## 🎯 Summary

### What You Need to Know
1. ✅ **Files go directly to specified path** (e.g., `/input/`)
2. ✅ **No extra subdirectory** with ZIP filename
3. ✅ **Internal ZIP structure preserved** if any
4. ✅ **Original ZIP file kept** for reference

### Quick Example
```
Upload: mydata.zip → /input
Result: 
  /input/mydata.zip  (original)
  /input/file1.csv   (extracted)
  /input/file2.csv   (extracted)
```

**This matches user expectations! 🎉**

---

## 📞 Questions?

### Q: What if I want a subdirectory?
**A:** Create it **inside the ZIP file**:
```
mydata.zip
└── mysubdir/
    ├── file1.csv
    └── file2.csv
```
Result: `/input/mysubdir/file1.csv`

### Q: What if files conflict?
**A:** They will be **overwritten**. Backup important files first!

### Q: Can I disable auto-extract?
**A:** Yes! Uncheck "Auto-extract compressed files" in GUI.

### Q: How do I see what's in my ZIP?
**A:** Check the extraction log - it shows all files being uploaded.

---

*Version: 5.2.1*  
*Date: October 13, 2025*  
*Extract Behavior: Direct to specified path ✅*
