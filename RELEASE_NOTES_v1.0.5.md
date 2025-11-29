# CC-Packer v1.0.5 Release Notes

**Release Date:** November 29, 2025

## Overview

This release disables the post-merge archive validation that was causing issues for some users. The merge process now completes without the BA2 verification step.

## Changes

### Disabled Archive Validation

The BA2 archive verification step that ran after merge completion has been temporarily disabled. This resolves issues where the validation was incorrectly rejecting valid archives created by Archive2.exe.

**What this means:**
- The merge process now completes without checking the created archives
- Archive2.exe errors during extraction/creation are still caught and reported
- The verification code remains in the codebase for potential future use

## Technical Details

- Commented out the `verify_ba2_integrity()` call in `merger.py`
- The verification method is preserved but not called during merge
- No other functional changes

## Compatibility

- Windows 10/11
- Fallout 4 (all versions including Next-Gen Update)
- Fallout 4 Creation Kit (for Archive2.exe)

## Changelog Summary

### v1.0.5 (November 29, 2025)

- Disabled post-merge archive validation

### v1.0.4 (November 28, 2025)

- Enhanced BA2 validation error messages
- Better inline code documentation

### v1.0.3 (November 28, 2025)

- Separate audio archive for sound files
- Loose strings extraction
- Administrator elevation check
- BA2 integrity verification
- Next-Gen BA2 version 8 support
- Vanilla-style texture naming

### v1.0.2 (November 26, 2025)

- Full FO4 localization support in ESL files

### v1.0.1 (November 26, 2025)

- Fixed sound playback issues

### v1.0.0 (November 25, 2025)

- Initial release
