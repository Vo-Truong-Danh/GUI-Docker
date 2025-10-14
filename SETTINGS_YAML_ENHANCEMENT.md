# Settings Tab YAML Port Management Enhancement

## Overview
Enhanced the Settings tab (`settings_tab_v4.py`) to support dynamic port configuration with YAML file import/export capabilities.

## New Features

### 1. YAML Import/Export
- **Load from YAML**: Import port configurations from external YAML files
- **Save to YAML**: Export current port settings to YAML format with metadata
- **Docker Compose Support**: Automatically detects and parses Docker Compose YAML format

### 2. Dynamic Port Management
- **Add Custom Ports**: Add new port configurations through a dialog interface
- **Delete Ports**: Remove port configurations with confirmation dialog
- **Validation**: Validates port numbers (1024-65535 range)

### 3. Enhanced UI
- **Toolbar**: Added buttons for YAML operations and port management
- **Visual Feedback**: Clear labels and organization
- **Error Handling**: Comprehensive error messages for invalid operations

## Technical Changes

### Data Structure Update
Changed `port_entries` from simple dictionary to nested structure:

**Before:**
```python
self.port_entries = {
    'spark_master_ui': Entry_widget,
    'jupyter': Entry_widget,
    ...
}
```

**After:**
```python
self.port_entries = {
    'spark_master_ui': {
        'entry': Entry_widget,
        'label': Label_widget,
        'row': row_number
    },
    'jupyter': {
        'entry': Entry_widget,
        'label': Label_widget,
        'row': row_number
    },
    ...
}
```

### New Methods Added

#### `load_ports_from_yaml()`
```python
def load_ports_from_yaml(self):
    """Load port configurations from YAML file"""
```
- Opens file dialog for YAML file selection
- Supports multiple YAML formats (flat, nested, Docker Compose)
- Updates UI with loaded port configurations
- Creates new port entries for unknown ports

#### `save_ports_to_yaml()`
```python
def save_ports_to_yaml(self):
    """Save current port configurations to YAML file"""
```
- Exports all ports to YAML format
- Includes metadata (timestamp, application info)
- Saves with `.yaml` extension

#### `add_new_port()`
```python
def add_new_port(self):
    """Add a new custom port configuration"""
```
- Opens dialog for port name and number input
- Validates port number (1024-65535)
- Checks for duplicate port names
- Creates new port entry in UI

#### `delete_port(key)`
```python
def delete_port(self, key):
    """Delete a port configuration"""
```
- Confirms deletion with user
- Prevents deletion of default ports
- Removes port entry from UI and configuration

#### `_create_port_row(key, port_number, row)`
```python
def _create_port_row(self, key, port_number, row):
    """Helper to create a port configuration row"""
```
- Creates label, entry, and delete button
- Manages grid layout
- Stores port data in structured format

### Updated Methods

#### `save_settings()`
Updated to use new nested structure:
```python
for key, port_data in self.port_entries.items():
    self.config['ports'][key] = port_data['entry'].get()
```

#### `reset_to_default()`
Updated port entry access:
```python
for key, port_data in self.port_entries.items():
    entry = port_data['entry']
    entry.delete(0, tk.END)
    entry.insert(0, defaults.get(key, ""))
```

#### `test_connections()`
Updated to access nested entry:
```python
for key, port_data in self.port_entries.items():
    port = port_data['entry'].get()
```

#### `open_in_browser(port_key)`
Updated port retrieval:
```python
port = self.port_entries[port_key]['entry'].get()
```

## YAML Format Support

### Standard Format
```yaml
ports:
  spark_master_ui: 9090
  spark_worker_ui: 8081
  hdfs_namenode_ui: 9870
  jupyter: 8888
```

### Flat Format
```yaml
spark_master_ui: 9090
spark_worker_ui: 8081
hdfs_namenode_ui: 9870
jupyter: 8888
```

### Docker Compose Format
```yaml
services:
  spark-master:
    ports:
      - "9090:8080"
  jupyter:
    ports:
      - "8888:8888"
```

## Usage Instructions

### Load Ports from YAML
1. Click **"Load from YAML"** button in Settings tab
2. Select a YAML file containing port configurations
3. Ports will be imported and UI updated automatically
4. New ports will be added, existing ports will be updated

### Save Ports to YAML
1. Configure ports in the Settings tab
2. Click **"Save to YAML"** button
3. Choose location and filename
4. YAML file will be created with current port configurations

### Add Custom Port
1. Click **"Add Port"** button
2. Enter port name (e.g., "custom_service")
3. Enter port number (1024-65535)
4. Click OK to create the port entry

### Delete Port
1. Click the **🗑️** button next to any custom port
2. Confirm deletion in the dialog
3. Port will be removed from UI and configuration

## Validation Rules

### Port Names
- Cannot be empty
- Cannot contain spaces or special characters (except underscores)
- Cannot duplicate existing port names

### Port Numbers
- Must be numeric
- Must be in range 1024-65535 (non-privileged ports)
- Cannot be empty

### Protected Ports
Default ports cannot be deleted:
- spark_master_ui
- spark_worker_ui
- hdfs_namenode_ui
- hdfs_datanode_ui
- history_server
- jupyter

## Benefits

### For Users
✅ Easy import/export of port configurations
✅ Backup and restore port settings
✅ Share configurations across environments
✅ Quick setup from Docker Compose files
✅ Custom port management without code changes

### For Developers
✅ Structured data format for easier maintenance
✅ Extensible architecture for future enhancements
✅ Clean separation of UI and data
✅ Comprehensive error handling
✅ Type-safe port access

## Error Handling

### YAML Import Errors
- Invalid YAML syntax → Shows error message
- File not found → Shows file dialog again
- Missing ports section → Attempts to parse alternative formats

### Port Validation Errors
- Invalid port number → Shows validation error
- Duplicate port name → Prevents creation
- Out of range port → Shows range requirement

### Save Errors
- Write permission denied → Shows error message
- Invalid file path → Returns to file dialog

## Testing Recommendations

### Test Cases
1. **Load Standard YAML**: Verify ports are imported correctly
2. **Load Docker Compose**: Ensure port mapping is parsed
3. **Add Custom Port**: Validate new port creation
4. **Delete Custom Port**: Verify removal works
5. **Save to YAML**: Check exported format is valid
6. **Reset to Default**: Ensure custom ports are preserved/reset appropriately
7. **Save Settings**: Verify configuration is saved correctly
8. **Test Connections**: Check port accessibility testing works

### Edge Cases
- Empty YAML file
- YAML with no ports section
- Invalid port numbers in YAML
- Very large number of ports (50+)
- Special characters in port names

## Future Enhancements

### Possible Additions
- Port conflict detection
- Auto-suggest available ports
- Port usage history
- Import from multiple YAML files
- Export to Docker Compose format
- Port validation against running services
- Batch port operations
- Port templates/presets

## Compatibility

### Python Version
- Python 3.7+
- PyYAML library required

### Dependencies
```python
import yaml  # Added to requirements.txt
import tkinter
from tkinter import filedialog, messagebox
```

### Configuration File
- Backward compatible with existing `spark_runner_config.json`
- YAML import/export is optional feature
- Existing configurations continue to work

## Conclusion

This enhancement provides a professional, user-friendly port management system with YAML integration. Users can now easily manage, backup, and share port configurations while maintaining compatibility with existing systems.

---

**Version**: 1.0  
**Date**: 2024-10-14  
**Author**: GitHub Copilot  
**File Modified**: `run_spark_gui/settings_tab_v4.py`
