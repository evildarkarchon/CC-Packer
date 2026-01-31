# CC-Packer v2.0 Release Notes

**Release Date:** January 30, 2026

## 🎉 Major Release: Standalone Operation

Version 2.0 is a major refactor that eliminates the Archive2.exe dependency, making CC-Packer fully standalone and easier to use.

## ✨ New Features

### Bundled BSArch
- **No More Archive2 Dependency**: CC-Packer now bundles bsarch.exe, eliminating the need for Creation Kit installation
- **Simplified Setup**: Just download and run - no configuration required
- **Automatic Path Handling**: Correct archive paths guaranteed for game compatibility

### Improved Auto-Detection
- **Registry-Based FO4 Detection**: Automatically finds Fallout 4 via Windows Registry
- **More Reliable**: Works even with non-standard Steam library locations

### Cleaner Interface
- **Removed Archive2 Path Input**: No longer needed since bsarch is bundled
- **Simplified UI**: Fewer fields to configure

### Output Naming
- **Renamed Output Files**: Merged archives now named `CCPacked*.ba2` instead of `CCMerged*.ba2`
- **Clearer Identification**: Easier to distinguish merged content from original files

## 🔧 Technical Improvements

- **BSArch Integration**: Full integration with [BSArch](https://www.nexusmods.com/newvegas/mods/64745) v1.0 x64 (MPL 2.0 licensed)
- **Fixed Archive Paths**: Resolved issue where files were stored with incorrect path prefixes
- **Working Directory Control**: Pack operations now use correct cwd for proper path resolution
- **Absolute Path Resolution**: Output paths resolved to absolute before packing

## 🙏 Credits

- **[zilav, ElminsterAU, Sheson](https://github.com/TES5Edit/TES5Edit)** - Authors of BSArch, the archive tool bundled with CC-Packer
- BSArch is part of the [xEdit](https://github.com/TES5Edit/TES5Edit) project
- Download BSArch standalone: [Nexus Mods](https://www.nexusmods.com/newvegas/mods/64745)

## 📦 What's Included

- `CCPacker.exe` - Main application
- `bsarch.exe` - Archive tool (bundled)
- `BSARCH_LICENSE.txt` - BSArch MPL 2.0 license
- `LICENSE` - CC-Packer MIT license
- `README.md` - Documentation

## 📋 Requirements

- Windows 10/11 (64-bit)
- Fallout 4 with Creation Club content
- **No longer requires**: Creation Kit or Archive2.exe

## 🔄 Migration from v1.x

If you have previously merged CC content with v1.x:
1. Use the Restore function to restore original files (optional)
2. Run the merge with v2.0
3. Your new archives will be named `CCPacked*.ba2` instead of `CCMerged*.ba2`

## 📝 Changelog Summary

### v2.0 (January 30, 2026)
- Replaced Archive2.exe with bundled bsarch.exe
- Removed Archive2 path from UI
- Added registry-based FO4 auto-detection
- Renamed output files to CCPacked*
- Fixed bsarch path prefix issue for correct archive paths
- Added BSARCH_LICENSE.txt for MPL 2.0 compliance

### Previous Versions
See CHANGELOG.md for complete version history.
