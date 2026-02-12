# CC-Packer v3.1.0 Release Notes

**Release Date:** February 12, 2026

## 🎉 Patch Release: Improved CC Detection & Background Processing

Version 3.1.0 improves Content Creator (CC) file detection accuracy, optimizes background processing with silent operations, and enhances the workflow for managing mixed packed/unpacked CC content.

## ✨ New Features

### Enhanced CC Detection via CCList.txt

- **Accurate CC Identification**: CC detection is now limited to actual Creation Club files registered in the included `CCList.txt` file
- **Reduced False Positives**: Eliminates false detection of non-CC files that might match CC file naming patterns
- **Official CC Registry**: Uses the exclusive list of official Creation Club items for precise detection
- **Custom Content Warning**: While `CCList.txt` *can* be edited to add non-CC items, this is **NOT** a supported operating mode. Users who attempt this do so at their own risk and without official support.

### Background Processing Without Popups

- **Silent Packing Routine**: The packing routine now runs completely in the background without spawning popup windows
- **Cleaner User Experience**: Users see progress in the main application window instead of distracting console/dialog windows
- **Improved Stability**: Eliminates potential issues from popup window interactions with the GUI
- **Code Optimizations**: Additional performance improvements and optimizations throughout the packing process
- **Enhanced Documentation**: Comprehensive code documentation added via advanced AI optimization

### Automatic Restore & Repack for Mixed Content

- **One-Click Solution**: When users click the Merge button with a mixture of packed (merged) and unpacked CC content present, CC-Packer automatically:
  1. Detects the mixed state
  2. Restores from backup to original state
  3. Re-runs the full packing process with all CC items together
- **Append-Like Functionality**: Provides the closest equivalent to an "append" function possible, since BA2 archives don't support adding new files once they're packed
- **Seamless Workflow**: Users can add new CC content and simply click Merge again to update their archives - no manual restore step required
- **Safety Preserved**: Original files remain backed up throughout the process

## 🔧 Technical Improvements

- **CC List Integration**: All CC detection now validates against `CCList.txt` for 100% accuracy
- **Process Management**: Launch packing operations in background processes with proper I/O redirection
- **Window Suppression**: No console windows appear during bg round processing
- **Error Handling**: Better error handling for background process operations
- **Code Quality**: Enhanced documentation and optimized code structure

## 🐛 Bug Fixes

- **Reduced False CC Detection**: No longer incorrectly identifies non-CC mods as Creation Club content
- **Cleaner Output**: Eliminates unwanted popup windows during packing operations

## 📦 What's Included

- `CCPacker.exe` - Main application v3.1.0
- `bsarch.exe` - Archive tool (bundled)
- `CCList.txt` - Official Creation Club file registry
- `BSARCH_LICENSE.txt` - BSArch MPL 2.0 license
- `LICENSE` - CC-Packer MIT license
- `README.md` - Complete documentation

## 📋 Requirements

- Windows 10/11 (64-bit)
- Fallout 4 with Creation Club content
- No external tools required (bsarch.exe bundled)

## 🔄 v3.0.0 → v3.1.0 Upgrade

If you're upgrading from v3.0.0:

1. **Simple Update**: Just download the new executable and replace the old one
2. **Data Preserved**: Your existing backups and configurations are unaffected
3. **New Features**: Enjoy more accurate CC detection and seamless mixed content handling
4. **No Migration Needed**: No additional steps required to upgrade

## 💬 Usage Notes

### Adding New CC Content After Merge

1. Download and install new Creation Club content in Fallout 4
2. Open CC-Packer
3. Click "Merge/Repack" button
4. CC-Packer automatically detects mixed content and:
   - Restores original state
   - Re-packs all CC items together
5. Done! Your archives are updated

### Custom CC List (Advanced Users - Not Supported)

If you want to add non-CC items to the packing list by editing `CCList.txt`:

- ⚠️ **WARNING**: This is not supported
- ⚠️ **NO GUARANTEES**: Behavior is undefined
- ⚠️ **USE AT YOUR OWN RISK**: May cause unexpected results or corruption
- Edit `CCList.txt` at your own discretion if you understand the risks

## 📊 Version History

### v3.1.0 (February 12, 2026)

- Limited CC detection to CCList.txt entries
- Silent background processing for packing operations
- Automatic restore & repack for mixed packed/unpacked content
- Code optimizations and enhanced documentation

### v3.0.0 (February 10, 2026)

- Content integrity and orphaned CC detection
- Automatic cleanup of incomplete CC downloads
- Plugin-first detection system
- Smart mixed content handling
- Comprehensive code documentation

### v2.0 (Dates vary)

- Major archive name refactoring
- Fixed ESL conflict issues
- Improved archive organization

### v1.x (Dates vary)

- Initial release versions

## 🎯 Next Steps

- Download v3.1.0 from the [releases page](https://github.com/jturnley/CC-Packer/releases)
- Replace your existing `CCPacker.exe` with the new version
- Continue using CC-Packer as normal
- Enjoy more accurate CC detection and seamless content management!

## 📞 Support

For issues, questions, or feature requests:

- Open an issue on GitHub
- Check the README.md for detailed documentation
- Review RELEASE_NOTES_v3.0.0.md and earlier for historical context

---

**Release Type**: Patch Release (Maintenance/Feature Enhancement)  
**Backward Compatibility**: Fully compatible with v3.0.0, v2.0, and earlier  
**Breaking Changes**: None
