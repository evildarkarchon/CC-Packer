# CC-Packer v1.0.2 Release Notes

**Release Date:** November 26, 2025

## New Features

### FO4 Localization Support ✨

- **Enhanced ESL File Creation**: Generated ESL files now include full Fallout 4 localization support
- **Proper Light Master Headers**: ESL files now correctly use the light master flag (0xFE) for optimal plugin compatibility
- **Complete Metadata**: Added CNAM (creator), SNAM (summary), ONAM (master list), INTV (version), and INCC (compiler info) subrecords
- **Dynamic Size Calculation**: Properly calculated record sizes ensure valid ESL format compliance
- **Language Support**: Framework now in place for multi-language localization in merged archives

### Benefits

- Merged content now fully compatible with FO4's localization system
- ESL files are properly recognized as light master plugins
- Better metadata tracking for debugging and file identification
- Support for future multi-language content inclusion

## Technical Improvements

- More robust ESL header generation with all required subrecords
- Improved file format compliance with Fallout 4 specifications
- Better documentation of file structure for future enhancements

## Bug Fixes

- Fixed ESL record header structure for better compatibility
- Improved data subrecord size calculations

## File Structure

### Binary Package (`CC-Packer_v1.0.2/`)

- `CCPacker.exe` - Standalone executable
- Supporting files and libraries

### Source Package (`CC-Packer_v1.0.2_Source/`)

- `main.py` - GUI application code
- `merger.py` - Core merging logic with new localization support
- `CCPacker.spec` - PyInstaller specification
- `requirements.txt` - Python dependencies
- `build_exe.bat` - Build script
- `README.md` - User documentation
- License and documentation files

## How to Use

### For End Users

1. Download `CC-Packer_v1.0.2_Windows.zip` from the releases page
2. Extract to any location
3. Run `CCPacker.exe`
4. Follow the on-screen instructions

### For Developers

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run from source: `python main.py`
4. Build executable: Run `build_exe.bat`

## Merged Content with Localization

The v1.0.2 update ensures that all merged Creation Club content archives include proper localization metadata. This means:

- Enhanced compatibility with FO4's plugin system
- Potential for future multi-language support
- Better plugin manager recognition (Vortex, MO2, etc.)

## Known Limitations

- Still requires Archive2.exe from the Creation Kit
- Windows only (10/11, 64-bit)
- Requires Fallout 4 with Creation Club content

## Compatibility

- ✅ Fallout 4 (all patches)
- ✅ Creation Club content (all items)
- ✅ Windows 10/11 64-bit
- ✅ Plugin managers (Vortex, Mod Organizer 2, etc.)

## Support & Feedback

For issues, feature requests, or feedback, please visit: [CC-Packer on GitHub](https://github.com/jturnley/CC-Packer)

## Changelog Summary

### v1.0.2 (November 26, 2025)

- Added FO4 localization support to ESL file creation
- Enhanced ESL headers with complete metadata
- Improved format compliance

### v1.0.1 (Previous)

- Smart texture archive splitting
- Enhanced backup system
- Improved error handling

### v1.0.0 (Initial Release)

- Basic CC content merging
- Archive extraction and repacking
- One-click restore functionality

---

**Thank you for using CC-Packer!**

