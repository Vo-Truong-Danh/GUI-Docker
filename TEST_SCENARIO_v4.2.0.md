# 🧪 Test Scenario - Container Conflict Auto-Resolution

## 📋 Test Case: Switching Docker Compose Files

### Prerequisites
- ✅ Docker Desktop running
- ✅ Two different docker-compose.yml files
- ✅ Spark Runner GUI v4.2.0 installed

---

## 🎯 Test Scenario

### Test 1: Normal Start (No Conflict)
**Steps:**
1. Open Spark Runner GUI
2. Click "▶️ Start Docker"
3. Wait for completion

**Expected Result:**
```log
[22:10:00] 🐳 Starting Docker containers...
[22:10:00] 📄 Using: docker-compose.yml
[22:10:05] ✅ Docker containers started successfully
```
✅ Status: Running (Green)

---

### Test 2: Container Conflict (Auto-Resolution)
**Steps:**
1. Start Docker with File A
2. Click "⏹️ Stop Docker" (important: STOP, not CLEAN)
3. Change compose file to File B in Config section
   - Click 📂 Browse button
   - Select different docker-compose.yml
   - Click "💾 Save Configuration"
4. Click "▶️ Start Docker"
5. Watch the logs

**Expected Result:**
```log
[22:15:00] 🐳 Starting Docker containers...
[22:15:00] 📄 Using: docker-compose-new.yml
[22:15:03] ⚠️ Detected container name conflict
[22:15:03] 💡 Old containers still exist, auto-cleaning...
[22:15:03] 🧹 Removing conflicting containers...
[22:15:05] 💻 $ docker-compose -f D:/path/to/docker-compose-new.yml down
[22:15:08] ✅ Old containers removed
[22:15:08] 🔄 Retrying start...
[22:15:08] 💻 $ docker-compose -f D:/path/to/docker-compose-new.yml up -d
[22:15:15] ✅ Docker containers started successfully
```
✅ Status: Running (Green)
✅ No dialog boxes appeared
✅ No user interaction needed

---

### Test 3: Multiple Conflicts
**Steps:**
1. Stop Docker
2. Manually create containers: `docker run -d --name test1 nginx`
3. Start Docker (conflict expected)
4. Observe auto-resolution

**Expected Result:**
- App detects conflict
- Runs `down` command
- Retries `up` command
- Success!

---

### Test 4: File Not Found
**Steps:**
1. In Config section, type non-existent path: `C:/fake/docker-compose.yml`
2. Click "💾 Save Configuration"
3. Click "▶️ Start Docker"

**Expected Result:**
```
┌─────────────────────────────────────────┐
│  Error: File Not Found                  │
├─────────────────────────────────────────┤
│  Docker Compose file not found:         │
│  C:/fake/docker-compose.yml             │
│                                          │
│  Please check the path in Config        │
│  section or use Browse button to        │
│  select the correct file.               │
└─────────────────────────────────────────┘
```
✅ Clear error message
✅ Helpful suggestions

---

### Test 5: Docker Compose Editor Sync
**Steps:**
1. Go to "Docker Compose Editor" tab
2. Click "Browse File" → Select different compose file
3. Go back to "Spark Runner" tab
4. Check Config section

**Expected Result:**
- ✅ Compose file path updated automatically
- ✅ Both tabs show same file path

---

## 📊 Success Criteria

| Test | Criterion | Status |
|------|-----------|--------|
| Test 1 | Normal start works | ✅ |
| Test 2 | Auto-resolves conflict | ✅ |
| Test 2 | No dialog boxes | ✅ |
| Test 2 | Logs are clear | ✅ |
| Test 3 | Multiple conflicts handled | ✅ |
| Test 4 | Validation catches missing file | ✅ |
| Test 4 | Error message helpful | ✅ |
| Test 5 | Path syncs between tabs | ✅ |

---

## 🐛 Known Issues (If Any)

### Issue 1: Clean fails due to permissions
**Symptoms:**
```log
❌ Failed to remove old containers
Error: permission denied
```
**Workaround:**
- Run Docker Desktop as Administrator
- Or manually: `docker rm -f $(docker ps -aq)`

### Issue 2: Network conflict after clean
**Symptoms:**
```log
Error: network already exists
```
**Workaround:**
- Use "🧹 Clean Docker" button (includes network cleanup)
- Or manually: `docker network prune -f`

---

## 📝 Log Checklist

When conflict occurs, you should see:
- [ ] ⚠️ Detected container name conflict
- [ ] 💡 Old containers still exist, auto-cleaning...
- [ ] 🧹 Removing conflicting containers...
- [ ] 💻 $ docker-compose down
- [ ] ✅ Old containers removed
- [ ] 🔄 Retrying start...
- [ ] 💻 $ docker-compose up -d
- [ ] ✅ Docker containers started successfully

**All 8 log messages = Perfect auto-resolution!** ✨

---

## 🎯 Performance Metrics

Expected timing:
- Normal start: 5-10 seconds
- Conflict detection: +1 second
- Clean operation: 3-5 seconds
- Retry start: 5-10 seconds
- **Total with conflict: 15-25 seconds**

Still faster than manual cleanup! 🚀

---

## 💡 Tips for Testing

1. **Use Docker Desktop UI** to verify containers are removed
2. **Check logs carefully** - every step should be logged
3. **Try different compose files** - ensure path management works
4. **Test edge cases** - missing files, permission errors
5. **Monitor status badge** - should update correctly

---

## ✅ Test Complete

After running all tests:
- [ ] All features work as expected
- [ ] No errors in console
- [ ] Logs are clear and helpful
- [ ] Status badge updates correctly
- [ ] No memory leaks or hangs

**Ready for production!** 🎉
