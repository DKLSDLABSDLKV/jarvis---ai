"""
File Manager Module for Secure Intelligent Desktop Assistant
File operations: create, delete, search, list
"""

import os
import shutil
import logging
import json
from pathlib import Path
from datetime import datetime
import sys

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class FileManager:
    """
    File Management System
    Handles file operations with logging and confirmation
    """
    
    def __init__(self, log_file=None):
        """
        Initialize file manager
        
        Args:
            log_file: Optional log file for file operations
        """
        self.logger = logging.getLogger('DesktopAssistant.FileManager')
        self.operation_log = []
        
        self.logger.info("File Manager initialized")
    
    def _log_operation(self, operation, path, success=True, error=None):
        """
        Log file operation
        
        Args:
            operation: Operation type
            path: File path
            success: Whether operation succeeded
            error: Error message if failed
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'path': str(path),
            'success': success,
            'error': str(error) if error else None
        }
        
        self.operation_log.append(log_entry)
        
        if success:
            self.logger.info(f"File operation: {operation} - {path}")
        else:
            self.logger.error(f"File operation failed: {operation} - {path} - {error}")
    
    def create_file(self, file_path, content=""):
        """
        Create a new file
        
        Args:
            file_path: Path to create file
            content: Optional file content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directories if needed
            parent = Path(file_path).parent
            parent.mkdir(parents=True, exist_ok=True)
            
            # Create file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_operation('create', file_path)
            return True
        
        except Exception as e:
            self._log_operation('create', file_path, success=False, error=str(e))
            return False
    
    def create_directory(self, dir_path):
        """
        Create a new directory
        
        Args:
            dir_path: Path to create directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            self._log_operation('create_dir', dir_path)
            return True
        
        except Exception as e:
            self._log_operation('create_dir', dir_path, success=False, error=str(e))
            return False
    
    def delete_file(self, file_path, confirm=True):
        """
        Delete a file
        
        Args:
            file_path: Path to delete
            confirm: Whether to require confirmation (unused, for API compatibility)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                self._log_operation('delete', file_path, success=False, error="File not found")
                return False
            
            # Check if it's a directory or file
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            
            self._log_operation('delete', file_path)
            return True
        
        except Exception as e:
            self._log_operation('delete', file_path, success=False, error=str(e))
            return False
    
    def move_file(self, source, destination):
        """
        Move/rename a file
        
        Args:
            source: Source path
            destination: Destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            shutil.move(source, destination)
            self._log_operation('move', f"{source} -> {destination}")
            return True
        
        except Exception as e:
            self._log_operation('move', source, success=False, error=str(e))
            return False
    
    def copy_file(self, source, destination):
        """
        Copy a file
        
        Args:
            source: Source path
            destination: Destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dest_path = Path(destination)
            if dest_path.is_dir():
                shutil.copy2(source, dest_path / Path(source).name)
            else:
                shutil.copy2(source, destination)
            
            self._log_operation('copy', f"{source} -> {destination}")
            return True
        
        except Exception as e:
            self._log_operation('copy', source, success=False, error=str(e))
            return False
    
    def read_file(self, file_path):
        """
        Read file content
        
        Args:
            file_path: Path to read
            
        Returns:
            File content or None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._log_operation('read', file_path)
            return content
        
        except Exception as e:
            self._log_operation('read', file_path, success=False, error=str(e))
            return None
    
    def write_file(self, file_path, content):
        """
        Write content to file
        
        Args:
            file_path: Path to write
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_operation('write', file_path)
            return True
        
        except Exception as e:
            self._log_operation('write', file_path, success=False, error=str(e))
            return False
    
    def append_file(self, file_path, content):
        """
        Append content to file
        
        Args:
            file_path: Path to append
            content: Content to append
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            self._log_operation('append', file_path)
            return True
        
        except Exception as e:
            self._log_operation('append', file_path, success=False, error=str(e))
            return False
    
    def list_files(self, directory, pattern=None):
        """
        List files in directory
        
        Args:
            directory: Directory to list
            pattern: Optional file pattern
            
        Returns:
            List of file paths
        """
        try:
            path = Path(directory)
            
            if not path.exists():
                return []
            
            if pattern:
                files = list(path.glob(pattern))
            else:
                files = [f for f in path.iterdir() if f.is_file()]
            
            return [str(f) for f in files]
        
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
    
    def search_files(self, search_dir, filename, recursive=True):
        """
        Search for files by name
        
        Args:
            search_dir: Directory to search
            filename: Filename to find
            recursive: Whether to search recursively
            
        Returns:
            List of matching file paths
        """
        matches = []
        
        try:
            path = Path(search_dir)
            
            if not path.exists():
                return matches
            
            if recursive:
                for file_path in path.rglob(filename):
                    matches.append(str(file_path))
            else:
                for file_path in path.glob(filename):
                    matches.append(str(file_path))
            
            self._log_operation('search', f"{search_dir}/{filename}")
        
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
        
        return matches
    
    def get_file_info(self, file_path):
        """
        Get file information
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return None
            
            stat = path.stat()
            
            return {
                'name': path.name,
                'path': str(path.absolute()),
                'size_bytes': stat.st_size,
                'size_kb': round(stat.st_size / 1024, 2),
                'size_mb': round(stat.st_size / (1024**2), 2),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'extension': path.suffix
            }
        
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return None
    
    def get_directory_size(self, directory):
        """
        Get total size of directory
        
        Args:
            directory: Directory path
            
        Returns:
            Size in bytes
        """
        total_size = 0
        
        try:
            path = Path(directory)
            
            for item in path.rglob('*'):
                if item.is_file():
                    total_size += item.stat().st_size
        
        except Exception as e:
            self.logger.error(f"Error calculating directory size: {e}")
        
        return total_size
    
    def confirm_delete(self, file_path, voice_engine=None):
        """
        Get confirmation for deletion
        
        Args:
            file_path: Path to delete
            voice_engine: Voice engine for confirmation
            
        Returns:
            True if confirmed, False otherwise
        """
        if voice_engine:
            return voice_engine.confirm_action(f"delete {file_path}")
        
        # Default to True if no voice engine
        return True
    
    def get_operation_log(self):
        """
        Get operation log
        
        Returns:
            List of operation log entries
        """
        return self.operation_log
    
    def clear_operation_log(self):
        """Clear operation log"""
        self.operation_log = []
    
    def save_operation_log(self, file_path):
        """
        Save operation log to file
        
        Args:
            file_path: Path to save log
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.operation_log, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving operation log: {e}")
            return False


# ============================================
# Main function for testing
# ============================================

def test_file_manager():
    """Test file manager"""
    print("Testing File Manager...")
    
    manager = FileManager()
    
    # Test file operations
    test_dir = Path("./test_files")
    test_file = test_dir / "test.txt"
    
    # Create directory
    print(f"\nCreating directory: {test_dir}")
    manager.create_directory(test_dir)
    
    # Create file
    print(f"Creating file: {test_file}")
    manager.create_file(test_file, "Hello, World!")
    
    # Read file
    print(f"Reading file: {test_file}")
    content = manager.read_file(test_file)
    print(f"Content: {content}")
    
    # List files
    print(f"\nListing files in: {test_dir}")
    files = manager.list_files(test_dir)
    print(f"Files: {files}")
    
    # Get file info
    print(f"\nGetting file info: {test_file}")
    info = manager.get_file_info(test_file)
    print(f"Info: {info}")
    
    # Delete file
    print(f"\nDeleting file: {test_file}")
    manager.delete_file(test_file)
    
    # Operation log
    print(f"\nOperation log:")
    for entry in manager.get_operation_log():
        print(f"  {entry}")
    
    # Clean up test directory
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    return manager


if __name__ == "__main__":
    test_file_manager()
