"""
Output file management helper for CrewAI flows.

Provides utilities for organizing and saving generated content 
with proper file naming and directory structure.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class OutputHelper:
    """Helper class for managing flow output files."""
    
    def __init__(self, base_output_dir: str = "output"):
        """
        Initialize OutputHelper with base output directory.
        
        Args:
            base_output_dir: Base directory for all outputs (relative to project root)
        """
        self.base_output_dir = Path(base_output_dir)
        
    def _ensure_directory_exists(self, directory_path: Path) -> None:
        """Ensure the specified directory exists."""
        directory_path.mkdir(parents=True, exist_ok=True)
        
    def _generate_timestamp(self) -> str:
        """Generate timestamp string for file naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename by removing/replacing invalid characters."""
        # Remove or replace characters that aren't safe for filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename
        
    def save_content(
        self, 
        flow_name: str, 
        content: str, 
        filename_prefix: str = "output",
        file_extension: str = "md",
        include_timestamp: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save content to a file in the appropriate flow directory.
        
        Args:
            flow_name: Name of the flow (used for subdirectory)
            content: Content to save
            filename_prefix: Prefix for the filename
            file_extension: File extension (without dot)
            include_timestamp: Whether to include timestamp in filename
            metadata: Optional metadata to include at top of file
            
        Returns:
            str: Full path to the saved file
        """
        # Create flow-specific directory
        flow_dir = self.base_output_dir / flow_name
        self._ensure_directory_exists(flow_dir)
        
        # Generate filename
        timestamp = self._generate_timestamp() if include_timestamp else ""
        filename_parts = [filename_prefix]
        if timestamp:
            filename_parts.append(timestamp)
            
        filename = f"{'_'.join(filename_parts)}.{file_extension}"
        filename = self._sanitize_filename(filename)
        
        file_path = flow_dir / filename
        
        # Prepare content with optional metadata
        final_content = content
        if metadata:
            metadata_section = self._format_metadata(metadata)
            final_content = f"{metadata_section}\n\n{content}"
            
        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        return str(file_path)
        
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata as markdown frontmatter or comment section."""
        lines = ["---"]
        for key, value in metadata.items():
            lines.append(f"{key}: {value}")
        lines.append("---")
        return "\n".join(lines)
        
    def save_multiple_outputs(
        self,
        flow_name: str,
        outputs: Dict[str, str],
        filename_prefix: str = "output",
        file_extension: str = "md",
        include_timestamp: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Save multiple outputs (e.g., different content types from same flow).
        
        Args:
            flow_name: Name of the flow
            outputs: Dictionary with output_type -> content mapping
            filename_prefix: Base prefix for filenames
            file_extension: File extension
            include_timestamp: Whether to include timestamp
            metadata: Optional metadata for all files
            
        Returns:
            Dict[str, str]: Mapping of output_type -> saved_file_path
        """
        saved_files = {}
        
        for output_type, content in outputs.items():
            # Create specific filename for this output type
            specific_prefix = f"{filename_prefix}_{output_type}"
            
            file_path = self.save_content(
                flow_name=flow_name,
                content=content,
                filename_prefix=specific_prefix,
                file_extension=file_extension,
                include_timestamp=include_timestamp,
                metadata=metadata
            )
            
            saved_files[output_type] = file_path
            
        return saved_files
        
    def get_output_directory(self, flow_name: str) -> str:
        """Get the output directory path for a specific flow."""
        return str(self.base_output_dir / flow_name)
        
    def list_output_files(self, flow_name: str, file_extension: str = None) -> list:
        """
        List all output files for a specific flow.
        
        Args:
            flow_name: Name of the flow
            file_extension: Optional file extension filter (without dot)
            
        Returns:
            List of file paths
        """
        flow_dir = self.base_output_dir / flow_name
        
        if not flow_dir.exists():
            return []
            
        if file_extension:
            pattern = f"*.{file_extension}"
            files = list(flow_dir.glob(pattern))
        else:
            files = list(flow_dir.iterdir())
            
        # Return only files, not directories
        return [str(f) for f in files if f.is_file()]


# Global instance for easy access
output_helper = OutputHelper()