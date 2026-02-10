# CC-Packer v3.0.0 Release Notes

**Release Date:** February 10, 2026

## 🎉 Major Release: Content Integrity & Documentation

Version 3.0.0 adds robust detection and handling of incomplete or orphaned Creation Club content, comprehensive code documentation, and improved user guidance for working with Creation Club items.

## ✨ New Features

### Orphaned CC Content Detection
- **Integrity Validation**: CC-Packer validates Creation Club content before merging by checking that each CC plugin file has both required BA2 archives (Main and Textures)
- **Orphaned Item Identification**: Incomplete or orphaned items are automatically detected and reported to the user
- **Detailed Warnings**: When issues are found, users see a detailed warning dialog that includes:
  - List of affected CC items with missing files
  - Explanation of the issue (known Fallout 4 download engine bug)
  - Clickable link to documentation for more information

### Automatic Orphaned Content Cleanup
- **Three Action Options**:
  - Delete Orphaned CC Content And Quit
  - Delete Orphaned CC Content and Continue (merges remaining valid items)
  - Quit CC Packer Now
- **Safety First**: Users have full control over how to handle incomplete CC downloads

### Plugin-First Detection
- **More Reliable Scanning**: CC content is now identified by finding plugin files (cc*.esl, cc*.esp, cc*.esm) first, then validating their BA2 archives exist
- **Accurate Reporting**: Provides more accurate detection of Creation Club items compared to simple file scanning

### Smart Mixed Content Handling
- **Automatic Repack Option**: When both CCPacked archives and new unmerged CC files are detected, users are prompted to automatically restore and repack all CC items together
- **Optimal Results**: Ensures the best outcome when adding new Creation Club content after a previous merge
- **User Choice**: Users can choose to skip repacking if they prefer

### Comprehensive Code Documentation
- **Full API Documentation**: Added extensive documentation to all Python modules including:
  - Detailed module-level docstrings explaining architecture and purpose
  - Complete class documentation with attribute descriptions
  - Method docstrings with Args, Returns, Examples, and Notes sections
  - Inline comments explaining complex logic and algorithms
  - Usage examples for key functions
- **Better Maintainability**: Makes it easier for developers to understand and modify the application

## 🔧 Technical Improvements

- **Content Detection**: Refactored merge process to detect Creation Club content by scanning for plugin files first, then validating BA2 archives
- **Validation Workflow**: Integrity validation now occurs before merge starts, allowing users to address issues proactively
- **Plugin Management**: Original CC plugin files remain in the Data folder (they contain game records); only BA2 asset archives are merged
- **Better Error Messages**: Orphaned content warnings provide detailed information about which files are missing for each CC item

## 🐛 Bug Fixes

### Main Archive ESL Conflict (v2.0 → v3.0.0)
- **Issue**: Named main archive from `CCPacked.esl` / `CCPacked - Main.ba2` was activating all BA2 archives due to prefix matching, including `CCPacked_Sounds - Main.ba2` and `CCPacked_Textures1 - Textures.ba2`
- **Solution**: Renamed to `CCPacked_Main.esl` / `CCPacked_Main - Main.ba2` with unique prefixes for proper isolation
- **Impact**: Each archive now activates only its intended BA2 file

### v1.x Upgrade Cleanup
- **Issue**: Users upgrading from v1.x had leftover `CCMerged*` files after using v2.0
- **Solution**: Merge and restore operations now properly delete old v1.x `CCMerged` files alongside v2.0 `CCPacked` files

## 📦 What's Included

- `CCPacker.exe` - Main application v3.0.0
- `bsarch.exe` - Archive tool (bundled)
- `BSARCH_LICENSE.txt` - BSArch MPL 2.0 license
- `LICENSE` - CC-Packer MIT license
- `README.md` - Complete documentation

## 📋 Requirements

- Windows 10/11 (64-bit)
- Fallout 4 with Creation Club content
- No external tools required (bsarch.exe bundled)

## 🔄 v2.0 → v3.0.0 Migration

If you're upgrading from v2.0:

1. **Start Fresh**: We recommend using Restore to return to original state first
   ```
   Click "Restore Original CC Archives" button
   ```

2. **Run v3.0.0**: Launch CCPacker v3.0.0
3. **Handle Any Issues**: If orphaned content is detected, choose your action
4. **Merge**: Click "Merge CC Archives" to merge your CC content
5. **Verify**: Check your game logs for any issues

## 📝 Changelog Summary

### v3.0.0 (February 10, 2026)
- Added orphaned CC content detection and validation
- Automatic orphaned content cleanup with user options
- Plugin-first detection for more accurate identification
- Comprehensive code documentation throughout codebase
- Smart mixed content handling for seamless repacking
- Fixed main archive ESL naming conflict
- Fixed v1.x upgrade cleanup issues
- Improved error messages and user guidance

### v2.0 (January 30, 2026)
- Replaced Archive2.exe with bundled bsarch.exe
- Removed Archive2 path from UI
- Added registry-based FO4 auto-detection
- Renamed output files to CCPacked*
- Fixed bsarch path prefix issue

### Previous Versions
See CHANGELOG.md for complete version history.

## 💬 Support

If you encounter any issues:
1. Check the troubleshooting section in README.md
2. Verify your Fallout 4 installation is complete
3. Ensure all Creation Club content is fully downloaded
4. Check CC-Packer logs for detailed error information

## 🙏 Credits

- **[BSArch Authors](https://github.com/TES5Edit/TES5Edit)** - zilav, ElminsterAU, and Sheson for the archive tool
- **Fallout 4 Community** - For bug reports and feature requests that drove this release
