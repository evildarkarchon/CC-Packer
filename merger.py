import os
import shutil
import subprocess
import logging
import struct
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Dict, Any, List, Tuple

# Note: strings_generator is no longer used - original STRINGS files are preserved
# inside the merged BA2 archives, and our ESL placeholder doesn't need localization.


class BSArchError(Exception):
    """Custom exception for BSArch operations with detailed error info."""
    def __init__(self, message: str, operation: str, archive_path: str = None, 
                 return_code: int = None, stdout: str = None, stderr: str = None):
        self.operation = operation
        self.archive_path = archive_path
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        
        # Build detailed message
        details = [f"BSArch {operation} failed"]
        if archive_path:
            details.append(f"Archive: {archive_path}")
        if return_code is not None:
            details.append(f"Exit code: {return_code}")
        if stderr and stderr.strip():
            details.append(f"Error output: {stderr.strip()}")
        if stdout and stdout.strip():
            details.append(f"Output: {stdout.strip()}")
        if message:
            details.append(f"Details: {message}")
            
        super().__init__("\n".join(details))


class CCMerger:
    def __init__(self):
        self.logger = logging.getLogger("CCPacker")
        logging.basicConfig(level=logging.INFO)
        self._last_error_details = None  # Store detailed error info
        self._bsarch_path = None  # Cache bsarch.exe path

    def _find_bsarch(self) -> str:
        """Find bsarch.exe bundled with the application.
        
        Returns:
            Path to bsarch.exe
            
        Raises:
            BSArchError if bsarch.exe is not found
        """
        if self._bsarch_path and os.path.exists(self._bsarch_path):
            return self._bsarch_path
        
        # When running as a PyInstaller bundle, files are extracted to a temp directory
        # sys._MEIPASS contains the path to that directory
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            bundle_dir = getattr(sys, '_MEIPASS', Path(sys.executable).parent)
        else:
            # Running as script
            bundle_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        
        possible_paths = [
            Path(bundle_dir) / "bsarch.exe",  # PyInstaller bundle or same dir as script
            Path(sys.executable).parent / "bsarch.exe",  # Same dir as exe
            Path(".") / "bsarch.exe",  # Current directory
        ]
        
        for p in possible_paths:
            if p.exists():
                self._bsarch_path = str(p.resolve())
                return self._bsarch_path
        
        raise BSArchError(
            message="bsarch.exe not found. It should be bundled with CC-Packer.",
            operation="initialization"
        )

    def _run_bsarch(self, args: List[str], operation: str, 
                    archive_name: str = None, progress_callback: Callable = None,
                    timeout: int = 600) -> subprocess.CompletedProcess:
        """Run bsarch.exe with comprehensive error handling.
        
        Args:
            args: Command line arguments for bsarch
            operation: Description of operation (e.g., 'unpack', 'pack')
            archive_name: Name of archive being processed (for error messages)
            progress_callback: Optional callback for progress messages
            timeout: Timeout in seconds (default 10 minutes)
            
        Returns:
            CompletedProcess on success
            
        Raises:
            BSArchError: On any failure
        """
        bsarch_path = self._find_bsarch()
        cmd = [bsarch_path] + args
        
        try:
            if progress_callback:
                progress_callback(f"  Running: bsarch {' '.join(args[:3])}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                error_msg = self._parse_bsarch_error(result.stderr, result.stdout, result.returncode)
                raise BSArchError(
                    message=error_msg,
                    operation=operation,
                    archive_path=archive_name,
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )
            
            return result
            
        except subprocess.TimeoutExpired:
            raise BSArchError(
                message=f"Operation timed out after {timeout} seconds",
                operation=operation,
                archive_path=archive_name
            )
        except FileNotFoundError:
            raise BSArchError(
                message=f"bsarch.exe not found at: {bsarch_path}",
                operation=operation,
                archive_path=archive_name
            )
        except PermissionError:
            raise BSArchError(
                message="Permission denied - try running as Administrator",
                operation=operation,
                archive_path=archive_name
            )
        except Exception as e:
            raise BSArchError(
                message=str(e),
                operation=operation,
                archive_path=archive_name
            )

    def _parse_bsarch_error(self, stderr: str, stdout: str, return_code: int) -> str:
        """Parse bsarch output to provide user-friendly error messages."""
        combined = f"{stderr} {stdout}".lower()
        
        if "access" in combined and "denied" in combined:
            return "Access denied - the file may be in use or you need Administrator privileges"
        elif "disk" in combined and ("full" in combined or "space" in combined):
            return "Insufficient disk space to complete operation"
        elif "not found" in combined or "cannot find" in combined:
            return "Source file or directory not found"
        elif "corrupt" in combined or "invalid" in combined:
            return "Archive appears to be corrupted or in an invalid format"
        elif "in use" in combined or "locked" in combined:
            return "File is locked by another process (possibly the game or another tool)"
        elif return_code != 0:
            # Generic error - provide context
            if stderr.strip():
                return f"BSArch reported an error: {stderr.strip()}"
            elif stdout.strip():
                return f"BSArch output: {stdout.strip()}"
            else:
                return "BSArch failed without providing details. Check disk space and file permissions."
        else:
            return f"Unexpected error (code {return_code})"

    def _extract_archive(self, ba2_path: Path, output_dir: Path, 
                        progress_callback: Callable = None) -> None:
        """Extract a BA2 archive using bsarch.
        
        Args:
            ba2_path: Path to the BA2 file to extract
            output_dir: Directory to extract files to
            progress_callback: Optional callback for progress messages
            
        Raises:
            BSArchError on failure
        """
        # bsarch unpack <archive> [folder] [-mt]
        args = ["unpack", str(ba2_path), str(output_dir), "-mt"]
        self._run_bsarch(args, operation="unpack", archive_name=ba2_path.name, 
                        progress_callback=progress_callback)

    def _pack_general_archive(self, source_dir: Path, output_path: Path,
                              compress: bool = True,
                              progress_callback: Callable = None) -> None:
        """Create a general (GNRL) BA2 archive using bsarch.
        
        Args:
            source_dir: Directory containing files to pack
            output_path: Path for the output BA2 file
            compress: Whether to compress the archive (default True)
            progress_callback: Optional callback for progress messages
            
        Raises:
            BSArchError on failure
        """
        # bsarch pack <folder> <archive> -fo4 [-z] [-mt] [-share]
        args = ["pack", str(source_dir), str(output_path), "-fo4", "-mt", "-share"]
        if compress:
            args.append("-z")
        self._run_bsarch(args, operation="pack", archive_name=output_path.name,
                        progress_callback=progress_callback)

    def _pack_texture_archive(self, source_dir: Path, output_path: Path,
                              progress_callback: Callable = None) -> None:
        """Create a texture (DX10) BA2 archive using bsarch.
        
        Note: Texture archives are always compressed per bsarch requirements.
        
        Args:
            source_dir: Directory containing texture files to pack
            output_path: Path for the output BA2 file
            progress_callback: Optional callback for progress messages
            
        Raises:
            BSArchError on failure
        """
        # bsarch pack <folder> <archive> -fo4dds -z [-mt] [-share]
        # Note: -fo4dds requires -z (compression) per bsarch docs
        args = ["pack", str(source_dir), str(output_path), "-fo4dds", "-z", "-mt", "-share"]
        self._run_bsarch(args, operation="pack", archive_name=output_path.name,
                        progress_callback=progress_callback)

    def _pack_sound_archive(self, source_dir: Path, output_path: Path,
                            progress_callback: Callable = None) -> None:
        """Create an uncompressed general BA2 archive for sound files.
        
        Note: Sound files should not be compressed for optimal game compatibility.
        
        Args:
            source_dir: Directory containing sound files to pack
            output_path: Path for the output BA2 file
            progress_callback: Optional callback for progress messages
            
        Raises:
            BSArchError on failure
        """
        # bsarch pack <folder> <archive> -fo4 [-mt] [-share]
        # No -z flag = uncompressed
        args = ["pack", str(source_dir), str(output_path), "-fo4", "-mt", "-share"]
        self._run_bsarch(args, operation="pack", archive_name=output_path.name,
                        progress_callback=progress_callback)

    def _get_archive_file_list(self, ba2_path: Path) -> Tuple[bool, List[str], int, str]:
        """Get the list of files in a BA2 archive using bsarch.
        
        Args:
            ba2_path: Path to the BA2 file
            
        Returns:
            Tuple of (success, file_list, file_count, error_message)
        """
        try:
            bsarch_path = self._find_bsarch()
            result = subprocess.run(
                [bsarch_path, str(ba2_path), "-list"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for listing
            )
            
            if result.returncode != 0:
                return False, [], 0, f"BSArch failed: {result.stderr.strip() or 'Unknown error'}"
            
            # Parse the output - BSArch shows header info first, then file list
            files = []
            file_count = 0
            in_file_list = False
            
            for line in result.stdout.strip().split('\n'):
                line = line.strip()
                if not line:
                    in_file_list = True  # Empty line separates header from file list
                    continue
                
                # Parse file count from header
                if line.startswith('Files:'):
                    try:
                        file_count = int(line.split(':')[1].strip())
                    except:
                        pass
                    continue
                
                # Skip header lines
                if ':' in line and not in_file_list:
                    continue
                if line.startswith('BSArch') or line.startswith('The Source') or line.startswith('https:'):
                    continue
                if line.startswith('Packer and unpacker'):
                    continue
                
                # This is a file entry
                if in_file_list and line and not line.startswith(' '):
                    # Normalize path separators
                    normalized = line.replace('/', '\\').lower()
                    files.append(normalized)
            
            return True, files, file_count, ""
            
        except subprocess.TimeoutExpired:
            return False, [], 0, "BSArch timed out listing archive contents"
        except FileNotFoundError:
            return False, [], 0, "BSArch not found"
        except Exception as e:
            return False, [], 0, str(e)

    def _get_ba2_file_count(self, ba2_path: Path) -> Tuple[bool, int, str]:
        """Read the file count from a BA2 archive header.
        
        Args:
            ba2_path: Path to the BA2 file
            
        Returns:
            Tuple of (success, file_count, error_message)
        """
        try:
            with open(ba2_path, 'rb') as f:
                # Read and verify BA2 magic number
                magic = f.read(4)
                if magic != b'BTDX':
                    return False, 0, f"Invalid BA2 header: {ba2_path.name}"
                
                # Skip version (4 bytes) and archive type (4 bytes)
                f.read(8)
                
                # Read file count
                file_count = struct.unpack('<I', f.read(4))[0]
                return True, file_count, ""
                
        except Exception as e:
            return False, 0, f"Error reading BA2 header: {e}"

    def _verify_extraction(self, ba2_path: Path, extract_dir: Path, 
                          progress_callback: Callable = None) -> Tuple[bool, str]:
        """Verify that extraction completed by comparing file lists.
        
        Args:
            ba2_path: Path to the original BA2 file
            extract_dir: Directory where files were extracted
            progress_callback: Optional callback for progress messages
            
        Returns:
            Tuple of (success, error_message)
        """
        # Try bsarch -list first for accurate file list verification
        success, expected_files, file_count, error = self._get_archive_file_list(ba2_path)
        
        if success and expected_files:
            # Build set of extracted files (normalized paths relative to extract_dir)
            extracted_files = set()
            for f in extract_dir.rglob("*"):
                if f.is_file():
                    rel_path = str(f.relative_to(extract_dir)).lower()
                    extracted_files.add(rel_path)
            
            # Check for missing files
            missing_files = []
            for expected in expected_files:
                if expected not in extracted_files:
                    # Try matching just the filename
                    expected_name = os.path.basename(expected)
                    found = any(os.path.basename(ext) == expected_name for ext in extracted_files)
                    if not found:
                        missing_files.append(expected)
            
            if missing_files:
                missing_count = len(missing_files)
                if missing_count <= 3:
                    return False, f"Missing {missing_count} files: {', '.join(missing_files)}"
                else:
                    return False, f"Missing {missing_count}/{len(expected_files)} files (e.g., {missing_files[0]})"
            
            return True, ""
        elif error:
            if progress_callback:
                progress_callback(f"  Warning: BSArch verification failed: {error}")
        
        # Fallback: Use header file count
        success, expected_count, error = self._get_ba2_file_count(ba2_path)
        
        if not success:
            if progress_callback:
                progress_callback(f"  Warning: Could not read archive header: {error}")
            # Can't verify, but don't fail - just check something was extracted
            extracted_count = sum(1 for _ in extract_dir.rglob("*") if _.is_file())
            if extracted_count == 0:
                return False, f"No files extracted from {ba2_path.name}"
            return True, ""
        
        if expected_count == 0:
            if progress_callback:
                progress_callback(f"  Warning: Archive reports 0 files: {ba2_path.name}")
            return True, ""
        
        # Count extracted files in the directory
        extracted_count = sum(1 for _ in extract_dir.rglob("*") if _.is_file())
        
        # Allow for some tolerance (90% threshold)
        min_expected = int(expected_count * 0.9)
        
        if extracted_count < min_expected:
            return False, f"Extraction incomplete: expected ~{expected_count} files, got {extracted_count}"
        
        return True, ""

    def verify_ba2_integrity(self, ba2_path: Path, 
                             progress_callback: Callable = None) -> Tuple[bool, str]:
        """Verify a BA2 archive is valid and not corrupted.
        
        Args:
            ba2_path: Path to the BA2 file to verify
            progress_callback: Optional callback for status messages
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not ba2_path.exists():
            return False, f"Archive not found: {ba2_path.name}"
        
        file_size = ba2_path.stat().st_size
        
        # Check minimum file size (BA2 header is at least 24 bytes)
        if file_size < 24:
            return False, f"Archive too small ({file_size} bytes): {ba2_path.name}"
        
        try:
            with open(ba2_path, 'rb') as f:
                # Read and verify BA2 magic number
                magic = f.read(4)
                if magic != b'BTDX':
                    return False, f"Invalid BA2 header (expected 'BTDX'): {ba2_path.name}"
                
                # Read version
                # Known BA2 versions:
                # - Version 1: Original Fallout 4 (2015)
                # - Version 7: Fallout 76 (not used in FO4)
                # - Version 8: Fallout 4 Next-Gen Update (April 2024)
                # We accept 1 and 8 for Fallout 4 compatibility
                version = struct.unpack('<I', f.read(4))[0]
                if version not in [1, 8]:
                    return False, f"Unexpected BA2 version {version} (expected 1 or 8): {ba2_path.name}"
                
                # Read archive type
                # GNRL = General (meshes, scripts, sounds, etc.)
                # DX10 = Textures (DirectX 10 format DDS)
                archive_type = f.read(4).decode('ascii', errors='ignore').strip('\x00')
                if archive_type not in ['GNRL', 'DX10']:
                    return False, f"Unknown archive type '{archive_type}' (expected GNRL or DX10): {ba2_path.name}"
                
                # Read file count
                file_count = struct.unpack('<I', f.read(4))[0]
                
                # Read name table offset
                name_table_offset = struct.unpack('<Q', f.read(8))[0]
                
                # Verify name table offset is within file
                if name_table_offset > file_size:
                    return False, f"Corrupted archive (name table beyond EOF): {ba2_path.name}"
                
                # Use bsarch -list for additional validation
                try:
                    success, files, count, error = self._get_archive_file_list(ba2_path)
                    if not success:
                        if progress_callback:
                            progress_callback(f"  Note: Could not list archive contents: {error}")
                except Exception as e:
                    if progress_callback:
                        progress_callback(f"  Note: Could not run BSArch validation: {e}")
                
                return True, f"Verified: {ba2_path.name} ({file_count} files, {file_size / (1024*1024):.1f} MB)"
                
        except struct.error as e:
            return False, f"Corrupted archive header: {ba2_path.name}"
        except IOError as e:
            return False, f"Cannot read archive: {e}"
        except Exception as e:
            return False, f"Verification error: {e}"

    def merge_cc_content(self, fo4_path, progress_callback):
        """Main merge operation - combines CC archives into optimized merged archives.
        
        Args:
            fo4_path: Path to Fallout 4 installation directory
            progress_callback: Callback function for progress updates
            
        Returns:
            Dict with 'success' bool and either 'summary' or 'error'
        """
        data_path = Path(fo4_path) / "Data"
        backup_dir = data_path / "CC_Backup"
        temp_dir = data_path / "CC_Temp"
        
        if not data_path.exists():
            return {"success": False, "error": "Data folder not found."}

        # Verify bsarch is available
        try:
            bsarch_path = self._find_bsarch()
            progress_callback(f"Using BSArch: {bsarch_path}")
        except BSArchError as e:
            return {"success": False, "error": str(e)}

        # 1. Identify CC Files (exclude CCMerged files created by this tool)
        all_cc_files = list(data_path.glob("cc*.ba2"))
        # Filter out any CCMerged archives to prevent re-packing previously merged content
        cc_files = [f for f in all_cc_files if not f.name.lower().startswith("ccmerged")]
        
        if not cc_files:
            if all_cc_files:
                return {"success": False, "error": "Only previously merged (CCMerged) archives found. No new CC files to merge."}
            else:
                return {"success": False, "error": "No Creation Club (cc*.ba2) files found."}

        progress_callback(f"Found {len(cc_files)} CC archives.")

        # Check if merged files already exist (optional cleanup warning)
        existing_merged = list(data_path.glob("CCMerged*.ba2"))
        if existing_merged:
            progress_callback(f"Warning: Found {len(existing_merged)} previously merged archive(s). These will be replaced.")

        # 2. Clean up old merged files and their ESLs
        progress_callback("Cleaning up old merged files...")
        for f in data_path.glob("CCMerged*.*"):
            try:
                f.unlink()
            except Exception as e:
                progress_callback(f"Warning: Could not delete {f.name}: {e}")

        # Also clean up old STRINGS files
        strings_dir = data_path / "Strings"
        if strings_dir.exists():
            for f in strings_dir.glob("CCMerged*.*"):
                try:
                    f.unlink()
                except Exception as e:
                    progress_callback(f"Warning: Could not delete STRINGS file {f.name}: {e}")

        # 3. Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup = backup_dir / timestamp
        current_backup.mkdir(parents=True, exist_ok=True)
        
        progress_callback(f"Backing up files to {current_backup}...")
        for f in cc_files:
            shutil.copy2(f, current_backup / f.name)

        # 4. Extract
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        general_dir = temp_dir / "General"
        textures_dir = temp_dir / "Textures"
        general_dir.mkdir()
        textures_dir.mkdir()

        main_ba2s = [f for f in cc_files if "texture" not in f.name.lower()]
        texture_ba2s = [f for f in cc_files if "texture" in f.name.lower()]

        # Extract Main archives with verification after each
        for i, f in enumerate(main_ba2s):
            progress_callback(f"Extracting Main [{i+1}/{len(main_ba2s)}]: {f.name}")
            try:
                self._extract_archive(f, general_dir, progress_callback)
                
                # Verify extraction completed successfully
                verify_ok, verify_error = self._verify_extraction(f, general_dir, progress_callback)
                if not verify_ok:
                    return {"success": False, "error": f"Verification failed for {f.name}: {verify_error}"}
                progress_callback(f"  ✓ Verified: {f.name}")
                
            except BSArchError as e:
                return {"success": False, "error": str(e)}

        # Extract Textures with verification after each
        for i, f in enumerate(texture_ba2s):
            progress_callback(f"Extracting Textures [{i+1}/{len(texture_ba2s)}]: {f.name}")
            try:
                self._extract_archive(f, textures_dir, progress_callback)
                
                # Verify extraction completed successfully
                verify_ok, verify_error = self._verify_extraction(f, textures_dir, progress_callback)
                if not verify_ok:
                    return {"success": False, "error": f"Verification failed for {f.name}: {verify_error}"}
                progress_callback(f"  ✓ Verified: {f.name}")
                
            except BSArchError as e:
                return {"success": False, "error": str(e)}

        # Handle Strings - Move to Data/Strings (Force loose files)
        progress_callback("Moving STRINGS files to Data/Strings...")
        target_strings_dir = data_path / "Strings"
        target_strings_dir.mkdir(exist_ok=True)
        
        moved_strings = []
        # Recursively find all string files
        for f in general_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in ['.strings', '.dlstrings', '.ilstrings']:
                target_file = target_strings_dir / f.name
                try:
                    # Use copy instead of copy2 to update timestamp (helps with archive invalidation)
                    shutil.copy(f, target_file)
                    f.unlink() # Remove from temp dir so it's not packed into the archive
                    moved_strings.append(f.name)
                except Exception as e:
                    progress_callback(f"Warning: Failed to move {f.name}: {e}")

        if moved_strings:
            progress_callback(f"Moved {len(moved_strings)} string files to Data/Strings")
            with open(current_backup / "moved_strings.txt", "w", encoding="utf-8") as f:
                for s in moved_strings:
                    f.write(f"{s}\n")
        else:
            progress_callback("Warning: No STRINGS files found in extracted content.")

        # 5. Separate Sounds (Uncompressed)
        sounds_dir = temp_dir / "Sounds"
        sounds_dir.mkdir(exist_ok=True)
        sound_files = []
        
        progress_callback("Separating sound files...")
        for f in general_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in ['.xwm', '.wav', '.fuz', '.lip']:
                rel_path = f.relative_to(general_dir)
                target_path = sounds_dir / rel_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(f, target_path)
                sound_files.append(target_path)
        
        created_esls = []

        # 6. Repack Sounds (Uncompressed)
        created_archives = []  # Track created archives for verification
        
        if sound_files:
            output_name_sounds = "CCMerged_Sounds"
            merged_sounds = data_path / f"{output_name_sounds} - Main.ba2"
            progress_callback("Repacking Sounds Archive (Uncompressed)...")
            try:
                self._pack_sound_archive(sounds_dir, merged_sounds, progress_callback)
                created_archives.append(merged_sounds)
            except BSArchError as e:
                return {"success": False, "error": str(e)}
            
            sounds_esl = f"{output_name_sounds}.esl"
            self._create_vanilla_esl(data_path / sounds_esl)
            created_esls.append(sounds_esl)

        # 7. Repack Main (Compressed)
        output_name = "CCMerged"
        merged_main = data_path / f"{output_name} - Main.ba2"
        
        if list(general_dir.rglob("*")):
            progress_callback("Repacking Main Archive (Compressed)...")
            try:
                self._pack_general_archive(general_dir, merged_main, compress=True, 
                                          progress_callback=progress_callback)
                created_archives.append(merged_main)
            except BSArchError as e:
                return {"success": False, "error": str(e)}
            
            main_esl = f"{output_name}.esl"
            self._create_vanilla_esl(data_path / main_esl)
            created_esls.append(main_esl)

        # 8. Repack Textures (Smart Splitting with Vanilla-style Naming)
        texture_files = []
        for f in textures_dir.rglob("*"):
            if f.is_file():
                texture_files.append((f, f.stat().st_size))
        
        # Split textures by 7GB uncompressed (typically compresses to ~3.5GB)
        MAX_SIZE = int(7.0 * 1024 * 1024 * 1024) 
        
        groups = []
        current_group = []
        current_size = 0
        
        for f_path, f_size in texture_files:
            if current_size + f_size > MAX_SIZE and current_group:
                groups.append(current_group)
                current_group = []
                current_size = 0
            current_group.append(f_path)
            current_size += f_size
        if current_group:
            groups.append(current_group)

        for idx, group in enumerate(groups):
            # Use vanilla-style numbering: Textures1, Textures2, etc. (1-indexed)
            texture_num = idx + 1
            # Each texture archive needs its own ESL to load properly
            texture_plugin_name = f"{output_name}_Textures{texture_num}"
            archive_name = f"{texture_plugin_name} - Textures.ba2"
            target_path = data_path / archive_name
            
            progress_callback(f"Repacking Textures {texture_num}/{len(groups)}: {archive_name}")
            
            # Move files to temp split dir
            split_dir = temp_dir / f"split_{idx}"
            split_dir.mkdir(exist_ok=True)
            
            for f_path in group:
                rel = f_path.relative_to(textures_dir)
                dest = split_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f_path, dest)
            
            try:
                self._pack_texture_archive(split_dir, target_path, progress_callback)
                created_archives.append(target_path)
            except BSArchError as e:
                return {"success": False, "error": str(e)}
            
            # Create ESL for this texture archive
            texture_esl = f"{texture_plugin_name}.esl"
            self._create_vanilla_esl(data_path / texture_esl)
            created_esls.append(texture_esl)
            progress_callback(f"  Created {texture_esl} for {archive_name}")

        progress_callback("STRINGS files moved to Data/Strings.")

        # 9. Add to plugins.txt
        progress_callback("Enabling plugins...")
        self._add_to_plugins_txt(created_esls)

        # 10. Cleanup
        progress_callback("Cleaning up original CC files...")
        for f in cc_files:
            try:
                f.unlink()
            except Exception as e:
                progress_callback(f"Warning: Could not delete {f.name}: {e}")
        
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            progress_callback(f"Warning: Could not clean up temp directory: {e}")

        # Build summary
        summary = {
            "archives_created": len(created_archives),
            "files_processed": len(cc_files),
            "esls_created": len(created_esls)
        }
        progress_callback(f"\nSummary: Created {summary['archives_created']} archives from {summary['files_processed']} CC files.")

        return {"success": True, "summary": summary}

    def restore_backup(self, fo4_path, progress_callback):
        data_path = Path(fo4_path) / "Data"
        backup_dir = data_path / "CC_Backup"
        
        if not backup_dir.exists():
            return {"success": False, "error": "No backup folder found."}
            
        # Find most recent backup
        backups = sorted([d for d in backup_dir.iterdir() if d.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
        if not backups:
            return {"success": False, "error": "No backups found."}
            
        latest_backup = backups[0]
        progress_callback(f"Restoring from {latest_backup.name}...")

        # Delete merged files
        merged_esls = []
        for f in data_path.glob("CCMerged*.*"):
            if f.suffix.lower() == ".esl":
                merged_esls.append(f.name)
            f.unlink()

        # Delete merged STRINGS files
        strings_dir = data_path / "Strings"
        if strings_dir.exists():
            for f in strings_dir.glob("CCMerged*.*"):
                try:
                    f.unlink()
                    progress_callback(f"Removed STRINGS file: {f.name}")
                except Exception as e:
                    progress_callback(f"Warning: Could not delete {f.name}: {e}")

            # Clean up extracted STRINGS files
            manifest_file = latest_backup / "moved_strings.txt"
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r", encoding="utf-8") as f:
                        moved_strings = [l.strip() for l in f.readlines()]
                    
                    progress_callback("Cleaning up extracted STRINGS files...")
                    for s in moved_strings:
                        s_path = strings_dir / s
                        if s_path.exists():
                            try:
                                s_path.unlink()
                            except Exception as e:
                                progress_callback(f"Warning: Could not delete {s}: {e}")
                except Exception as e:
                    progress_callback(f"Warning: Could not read moved_strings.txt: {e}")

        # Remove from plugins.txt
        self._remove_from_plugins_txt(merged_esls)

        # Restore files
        backup_files = list(latest_backup.glob("*"))
        for i, f in enumerate(backup_files):
            if f.name == "moved_strings.txt":
                continue
            shutil.copy2(f, data_path / f.name)

        # Clean up old backups, keeping only the most recent one
        if len(backups) > 1:
            progress_callback("Cleaning up old backups...")
            for old_backup in backups[1:]:
                try:
                    shutil.rmtree(old_backup)
                    progress_callback(f"Removed old backup: {old_backup.name}")
                except Exception as e:
                    progress_callback(f"Warning: Could not remove {old_backup.name}: {e}")
            
        return {"success": True}

    def _get_plugins_txt(self):
        local_app_data = os.environ.get('LOCALAPPDATA')
        if not local_app_data:
            return None
        return Path(local_app_data) / "Fallout4" / "plugins.txt"

    def _add_to_plugins_txt(self, esl_names):
        plugins_txt = self._get_plugins_txt()
        if not plugins_txt or not plugins_txt.parent.exists():
            return

        if not plugins_txt.exists():
            lines = []
        else:
            try:
                with open(plugins_txt, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = [l.strip() for l in f.readlines()]
            except:
                return

        modified = False
        for esl in esl_names:
            entry = f"*{esl}"
            if entry not in lines and esl not in lines:
                lines.append(entry)
                modified = True
        
        if modified:
            try:
                with open(plugins_txt, 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines))
            except Exception as e:
                self.logger.error(f"Failed to write plugins.txt: {e}")

    def _remove_from_plugins_txt(self, esl_names):
        plugins_txt = self._get_plugins_txt()
        if not plugins_txt or not plugins_txt.exists():
            return

        try:
            with open(plugins_txt, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l.strip() for l in f.readlines()]
        except:
            return

        new_lines = []
        modified = False
        for line in lines:
            clean_line = line.lstrip("*")
            if clean_line in esl_names:
                modified = True
                continue
            new_lines.append(line)

        if modified:
            try:
                with open(plugins_txt, 'w', encoding='utf-8') as f:
                    f.write("\n".join(new_lines))
            except Exception as e:
                self.logger.error(f"Failed to write plugins.txt: {e}")

    def _create_vanilla_esl(self, path):
        # Create vanilla-compatible ESL matching Bethesda's format exactly
        # Reference: https://en.uesp.net/wiki/Skyrim_Mod:Mod_File_Format/TES4
        data = bytearray()
        
        # TES4 Record Header
        data.extend(b'TES4')
        size_placeholder = len(data)
        data.extend(b'\x00\x00\x00\x00')  # Record size (placeholder)
        
        # Flags for ESL (Light Master):
        # 0x00000001 = Master file (ESM)
        # 0x00000200 = Light Master (ESL)
        # Combined: 0x201 = Master + Light Master
        # Note: We do NOT set the Localized flag (0x80) because our ESL is a placeholder
        # with no records. The original CC plugins handle their own localization via
        # STRINGS files that are preserved in the merged BA2.
        flags = 0x00000001 | 0x00000200  # 0x201
        data.extend(flags.to_bytes(4, 'little'))
        
        data.extend(b'\x00\x00\x00\x00')  # Form ID (unused for TES4)
        data.extend(b'\x00\x00\x00\x00')  # Timestamp & Version Control
        data.extend(b'\x00\x00\x00\x00')  # Form Version & Unknown
        
        # HEDR subrecord (Header) - Required
        data.extend(b'HEDR')
        data.extend(b'\x0c\x00')  # Data size (12 bytes)
        data.extend(b'\x00\x00\x80\x3f')  # Version 1.0 (float)
        data.extend(b'\x00\x00\x00\x00')  # Number of records
        data.extend(b'\x00\x00\x00\x00')  # Next object ID
        
        # CNAM subrecord (Creator name) - null-terminated string
        creator = b'CC-Packer\x00'
        data.extend(b'CNAM')
        data.extend(len(creator).to_bytes(2, 'little'))
        data.extend(creator)
        
        # SNAM subrecord (Summary/Description) - null-terminated string
        summary = b'Merged Creation Club Content - Localization Ready\x00'
        data.extend(b'SNAM')
        data.extend(len(summary).to_bytes(2, 'little'))
        data.extend(summary)
        
        # INTV subrecord (Internal Version) - used for tagified strings count
        # Setting to 0 indicates no tagified master strings
        data.extend(b'INTV')
        data.extend(b'\x04\x00')  # Data size (4 bytes)
        data.extend(b'\x00\x00\x00\x00')  # Tagified string count = 0
        
        # Update record size (total size - 24-byte TES4 header)
        # TES4 header is: 4 (type) + 4 (size) + 4 (flags) + 4 (formid) + 4 (timestamp) + 4 (version)
        record_size = len(data) - 24
        data[size_placeholder:size_placeholder+4] = record_size.to_bytes(4, 'little')
        
        with open(path, 'wb') as f:
            f.write(data)
