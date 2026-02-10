# CC-Packer v2.1.0 Release Notes

**Release Date:** February 10, 2026

## 🐛 Bug Fixes

### Fixed ESL Archive Loading Issue

**Problem:** The main ESL file (`CCPacked.esl`) was causing the game to load archive files for other archives (textures, sounds) even when their respective ESL files were not enabled.

**Root Cause:** Archive naming conflict - all archives shared the `CCPacked` prefix, causing Fallout 4 to load multiple archives when searching for matches based on the plugin name.

**Solution:** Changed the main archive naming scheme to use a unique identifier:
- **Old naming:** `CCPacked - Main.ba2` → `CCPacked.esl`
- **New naming:** `CCPacked_Main - General.ba2` → `CCPacked_Main.esl`

Now each ESL has a completely unique base name:
- `CCPacked_Main.esl` → `CCPacked_Main - General.ba2` (main archive only)
- `CCPacked_Sounds.esl` → `CCPacked_Sounds - Main.ba2` (sounds only)
- `CCPacked_Textures1.esl` → `CCPacked_Textures1 - Textures.ba2` (textures only)

**Result:** Each ESL now activates ONLY its own archive when enabled. No more cross-loading of unrelated archives.

## 📝 Changelog Summary

### v2.1.0 (February 10, 2026)
- Fixed ESL archive loading - main ESL no longer activates texture/sound archives
- Renamed main archive from `CCPacked - Main.ba2` to `CCPacked_Main - General.ba2`
- Renamed main ESL from `CCPacked.esl` to `CCPacked_Main.esl`
- Updated archive cleanup logic to handle new naming scheme

### Previous Versions
See CHANGELOG.md for complete version history.

## Migration from v2.0

If you previously merged CC content with v2.0:

1. **Restore the old archives** (recommended):
   - Use the Restore function to restore original CC files
   - Delete the old merged files manually if needed

2. **Run the new merge** with v2.1.0:
   - Your new archives will use the corrected naming scheme
   - Archive files will now follow the pattern: `CCPacked_Main - General.ba2`, `CCPacked_Sounds - Main.ba2`, `CCPacked_Textures*.ba2`

3. **Update your load order**:
   - Old plugins: `CCPacked.esl` (remove)
   - New plugins: `CCPacked_Main.esl` (add)
   - Texture & sound plugins remain: `CCPacked_Textures*.esl`, `CCPacked_Sounds.esl`
