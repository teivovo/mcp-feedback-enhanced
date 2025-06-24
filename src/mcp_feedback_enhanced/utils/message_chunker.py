#!/usr/bin/env python3
"""
Intelligent Message Chunking and Formatting System
==================================================

Sophisticated message chunking system that splits large MCP outputs into
appropriately sized Telegram messages while preserving formatting and context.
Handles code blocks, markdown, and maintains readability across chunks.

Key Features:
- Smart content-aware chunking algorithms
- Markdown and code block preservation
- Context preservation across chunks
- Multiple chunking strategies for different content types
- Chunk numbering and navigation
- Preview and summary generation
- Telegram message size optimization

Author: MCP Feedback Enhanced Team
"""

import re
import json
import math
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from ..debug import debug_log


class ChunkType(Enum):
    """Types of content chunks"""
    TEXT = "text"
    CODE = "code"
    JSON = "json"
    LIST = "list"
    TABLE = "table"
    MIXED = "mixed"


class ChunkStrategy(Enum):
    """Chunking strategies for different content types"""
    SENTENCE_BOUNDARY = "sentence_boundary"
    PARAGRAPH_BOUNDARY = "paragraph_boundary"
    CODE_BLOCK_BOUNDARY = "code_block_boundary"
    LINE_BOUNDARY = "line_boundary"
    WORD_BOUNDARY = "word_boundary"
    CHARACTER_BOUNDARY = "character_boundary"


@dataclass
class ChunkMetadata:
    """Metadata for a message chunk"""
    chunk_index: int
    total_chunks: int
    chunk_type: ChunkType
    strategy_used: ChunkStrategy
    original_length: int
    chunk_length: int
    has_code: bool
    has_markdown: bool
    context_preserved: bool
    continuation_marker: Optional[str] = None


@dataclass
class MessageChunk:
    """A single message chunk with metadata"""
    content: str
    metadata: ChunkMetadata
    preview: Optional[str] = None
    navigation_info: Optional[str] = None
    
    def to_telegram_message(self, include_metadata: bool = True) -> str:
        """Convert chunk to Telegram message format"""
        lines = []
        
        # Add navigation info if available
        if self.navigation_info and include_metadata:
            lines.append(self.navigation_info)
            lines.append("")
        
        # Add main content
        lines.append(self.content)
        
        # Add continuation marker if needed
        if self.metadata.continuation_marker:
            lines.append("")
            lines.append(self.metadata.continuation_marker)
        
        # Add metadata footer if requested
        if include_metadata and self.metadata.total_chunks > 1:
            lines.append("")
            lines.append(f"📄 Part {self.metadata.chunk_index + 1}/{self.metadata.total_chunks} "
                        f"({self.metadata.chunk_length} chars, {self.metadata.chunk_type.value})")
        
        return "\n".join(lines)


class MessageChunker:
    """
    Intelligent message chunking system for Telegram integration.
    
    This class provides sophisticated algorithms for splitting large content
    into appropriately sized chunks while preserving formatting, context,
    and readability across multiple Telegram messages.
    """
    
    # Telegram message limits
    MAX_MESSAGE_LENGTH = 4096
    SAFE_MESSAGE_LENGTH = 3800  # Leave room for metadata and formatting
    
    # Content type patterns
    CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    INLINE_CODE_PATTERN = re.compile(r'`[^`]+`')
    MARKDOWN_PATTERNS = {
        'bold': re.compile(r'\*\*[^*]+\*\*'),
        'italic': re.compile(r'\*[^*]+\*'),
        'underline': re.compile(r'__[^_]+__'),
        'strikethrough': re.compile(r'~~[^~]+~~'),
        'link': re.compile(r'\[([^\]]+)\]\(([^)]+)\)'),
    }
    
    def __init__(self, 
                 max_chunk_size: int = SAFE_MESSAGE_LENGTH,
                 preserve_code_blocks: bool = True,
                 preserve_markdown: bool = True,
                 add_navigation: bool = True,
                 add_previews: bool = True):
        """
        Initialize the message chunker.
        
        Args:
            max_chunk_size: Maximum size for each chunk
            preserve_code_blocks: Whether to preserve code block integrity
            preserve_markdown: Whether to preserve markdown formatting
            add_navigation: Whether to add navigation info to chunks
            add_previews: Whether to add content previews
        """
        self.max_chunk_size = max_chunk_size
        self.preserve_code_blocks = preserve_code_blocks
        self.preserve_markdown = preserve_markdown
        self.add_navigation = add_navigation
        self.add_previews = add_previews
        
        debug_log("MessageChunker initialized", "CHUNKER")
    
    def chunk_message(self, 
                     content: str, 
                     title: Optional[str] = None,
                     content_type: Optional[ChunkType] = None) -> List[MessageChunk]:
        """
        Chunk a message into appropriately sized pieces.
        
        Args:
            content: Content to chunk
            title: Optional title for the content
            content_type: Hint about the content type
            
        Returns:
            List of MessageChunk objects
        """
        if not content or not content.strip():
            return []
        
        # Detect content type if not provided
        if content_type is None:
            content_type = self._detect_content_type(content)
        
        # Add title if provided
        if title:
            content = f"**{title}**\n\n{content}"
        
        # Check if chunking is needed
        if len(content) <= self.max_chunk_size:
            chunk = MessageChunk(
                content=content,
                metadata=ChunkMetadata(
                    chunk_index=0,
                    total_chunks=1,
                    chunk_type=content_type,
                    strategy_used=ChunkStrategy.SENTENCE_BOUNDARY,
                    original_length=len(content),
                    chunk_length=len(content),
                    has_code=self._has_code_blocks(content),
                    has_markdown=self._has_markdown(content),
                    context_preserved=True
                )
            )
            return [chunk]
        
        # Choose chunking strategy based on content type
        strategy = self._choose_chunking_strategy(content, content_type)
        
        # Perform chunking
        chunks = self._chunk_by_strategy(content, strategy, content_type)
        
        # Add navigation and metadata
        self._add_chunk_metadata(chunks, content, content_type)
        
        debug_log(f"Chunked message into {len(chunks)} parts using {strategy.value}", "CHUNKER")
        return chunks
    
    def chunk_mcp_response(self, 
                          mcp_data: Dict[str, Any],
                          include_metadata: bool = True) -> List[MessageChunk]:
        """
        Chunk an MCP response with intelligent formatting.
        
        Args:
            mcp_data: MCP response data
            include_metadata: Whether to include MCP metadata
            
        Returns:
            List of MessageChunk objects
        """
        # Format MCP response
        formatted_content = self._format_mcp_response(mcp_data, include_metadata)
        
        # Determine content type based on MCP data
        content_type = self._detect_mcp_content_type(mcp_data)
        
        # Extract title from MCP data
        title = self._extract_mcp_title(mcp_data)
        
        return self.chunk_message(formatted_content, title, content_type)
    
    def chunk_code_output(self, 
                         code: str, 
                         language: str = "text",
                         title: Optional[str] = None) -> List[MessageChunk]:
        """
        Chunk code output with syntax preservation.
        
        Args:
            code: Code content
            language: Programming language for syntax highlighting
            title: Optional title for the code
            
        Returns:
            List of MessageChunk objects
        """
        # Wrap in code block
        if not code.startswith("```"):
            code = f"```{language}\n{code}\n```"
        
        return self.chunk_message(code, title, ChunkType.CODE)
    
    def chunk_json_data(self, 
                       data: Union[Dict, List, str],
                       title: Optional[str] = None) -> List[MessageChunk]:
        """
        Chunk JSON data with proper formatting.
        
        Args:
            data: JSON data (dict, list, or string)
            title: Optional title for the data
            
        Returns:
            List of MessageChunk objects
        """
        # Convert to formatted JSON string
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                pass  # Keep as string
        
        if isinstance(data, (dict, list)):
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            json_str = str(data)
        
        # Wrap in code block
        formatted_json = f"```json\n{json_str}\n```"
        
        return self.chunk_message(formatted_json, title, ChunkType.JSON)
    
    def create_summary_chunk(self, 
                           chunks: List[MessageChunk],
                           original_content: str) -> MessageChunk:
        """
        Create a summary chunk for large content.
        
        Args:
            chunks: List of content chunks
            original_content: Original content before chunking
            
        Returns:
            Summary MessageChunk
        """
        # Generate summary
        summary_lines = [
            "📋 **Content Summary**",
            "",
            f"📊 **Statistics:**",
            f"• Total length: {len(original_content):,} characters",
            f"• Number of parts: {len(chunks)}",
            f"• Content type: {chunks[0].metadata.chunk_type.value if chunks else 'unknown'}",
            ""
        ]
        
        # Add content preview
        preview = self._generate_content_preview(original_content, max_length=200)
        if preview:
            summary_lines.extend([
                "🔍 **Preview:**",
                f"```\n{preview}\n```",
                ""
            ])
        
        # Add chunk breakdown
        if len(chunks) > 1:
            summary_lines.extend([
                "📄 **Parts:**",
                *[f"• Part {i+1}: {chunk.metadata.chunk_length:,} chars ({chunk.metadata.chunk_type.value})"
                  for i, chunk in enumerate(chunks)],
                ""
            ])
        
        summary_lines.append("💡 Use the numbered parts below to read the complete content.")
        
        summary_content = "\n".join(summary_lines)
        
        return MessageChunk(
            content=summary_content,
            metadata=ChunkMetadata(
                chunk_index=-1,  # Special index for summary
                total_chunks=len(chunks) + 1,
                chunk_type=ChunkType.MIXED,
                strategy_used=ChunkStrategy.SENTENCE_BOUNDARY,
                original_length=len(original_content),
                chunk_length=len(summary_content),
                has_code=False,
                has_markdown=True,
                context_preserved=True
            ),
            navigation_info="📋 **SUMMARY** (Read this first)"
        )
    
    def _detect_content_type(self, content: str) -> ChunkType:
        """Detect the type of content"""
        # Check for code blocks
        if self.CODE_BLOCK_PATTERN.search(content):
            return ChunkType.CODE
        
        # Check for JSON-like content
        stripped = content.strip()
        if (stripped.startswith('{') and stripped.endswith('}')) or \
           (stripped.startswith('[') and stripped.endswith(']')):
            try:
                json.loads(stripped)
                return ChunkType.JSON
            except json.JSONDecodeError:
                pass
        
        # Check for list-like content
        lines = content.split('\n')
        list_lines = sum(1 for line in lines if re.match(r'^\s*[-*•]\s+', line))
        if list_lines > len(lines) * 0.5:
            return ChunkType.LIST
        
        # Check for table-like content
        table_lines = sum(1 for line in lines if '|' in line)
        if table_lines > len(lines) * 0.3:
            return ChunkType.TABLE
        
        # Default to text
        return ChunkType.TEXT
    
    def _detect_mcp_content_type(self, mcp_data: Dict[str, Any]) -> ChunkType:
        """Detect content type from MCP data"""
        # Check for code in response
        if any(key in mcp_data for key in ['code', 'script', 'command']):
            return ChunkType.CODE
        
        # Check for structured data
        if any(key in mcp_data for key in ['data', 'result', 'response_data']):
            return ChunkType.JSON
        
        # Check for lists
        if any(isinstance(value, list) for value in mcp_data.values()):
            return ChunkType.LIST
        
        return ChunkType.MIXED
    
    def _has_code_blocks(self, content: str) -> bool:
        """Check if content has code blocks"""
        return bool(self.CODE_BLOCK_PATTERN.search(content) or 
                   self.INLINE_CODE_PATTERN.search(content))
    
    def _has_markdown(self, content: str) -> bool:
        """Check if content has markdown formatting"""
        return any(pattern.search(content) for pattern in self.MARKDOWN_PATTERNS.values())
    
    def _choose_chunking_strategy(self, content: str, content_type: ChunkType) -> ChunkStrategy:
        """Choose the best chunking strategy for the content"""
        if content_type == ChunkType.CODE:
            if self.preserve_code_blocks:
                return ChunkStrategy.CODE_BLOCK_BOUNDARY
            else:
                return ChunkStrategy.LINE_BOUNDARY
        
        elif content_type == ChunkType.JSON:
            return ChunkStrategy.LINE_BOUNDARY
        
        elif content_type == ChunkType.LIST:
            return ChunkStrategy.LINE_BOUNDARY
        
        elif content_type == ChunkType.TABLE:
            return ChunkStrategy.LINE_BOUNDARY
        
        else:  # TEXT or MIXED
            # Check for paragraphs
            if '\n\n' in content:
                return ChunkStrategy.PARAGRAPH_BOUNDARY
            else:
                return ChunkStrategy.SENTENCE_BOUNDARY
    
    def _chunk_by_strategy(self, 
                          content: str, 
                          strategy: ChunkStrategy,
                          content_type: ChunkType) -> List[MessageChunk]:
        """Chunk content using the specified strategy"""
        if strategy == ChunkStrategy.CODE_BLOCK_BOUNDARY:
            return self._chunk_by_code_blocks(content, content_type)
        elif strategy == ChunkStrategy.PARAGRAPH_BOUNDARY:
            return self._chunk_by_paragraphs(content, content_type)
        elif strategy == ChunkStrategy.SENTENCE_BOUNDARY:
            return self._chunk_by_sentences(content, content_type)
        elif strategy == ChunkStrategy.LINE_BOUNDARY:
            return self._chunk_by_lines(content, content_type)
        elif strategy == ChunkStrategy.WORD_BOUNDARY:
            return self._chunk_by_words(content, content_type)
        else:  # CHARACTER_BOUNDARY
            return self._chunk_by_characters(content, content_type)
    
    def _chunk_by_code_blocks(self, content: str, content_type: ChunkType) -> List[MessageChunk]:
        """Chunk content preserving code block boundaries"""
        chunks = []
        current_chunk = ""
        
        # Split by code blocks
        parts = self.CODE_BLOCK_PATTERN.split(content)
        code_blocks = self.CODE_BLOCK_PATTERN.findall(content)
        
        i = 0
        code_index = 0
        
        while i < len(parts):
            # Add text part
            if parts[i]:
                if len(current_chunk + parts[i]) <= self.max_chunk_size:
                    current_chunk += parts[i]
                else:
                    if current_chunk:
                        chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.CODE_BLOCK_BOUNDARY))
                    current_chunk = parts[i]
            
            # Add code block if available
            if code_index < len(code_blocks):
                code_block = code_blocks[code_index]
                if len(current_chunk + code_block) <= self.max_chunk_size:
                    current_chunk += code_block
                else:
                    if current_chunk:
                        chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.CODE_BLOCK_BOUNDARY))
                    # Handle large code blocks
                    if len(code_block) > self.max_chunk_size:
                        # Split large code block by lines
                        code_chunks = self._chunk_large_code_block(code_block)
                        chunks.extend(code_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = code_block
                code_index += 1
            
            i += 1
        
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.CODE_BLOCK_BOUNDARY))
        
        return chunks
    
    def _chunk_by_paragraphs(self, content: str, content_type: ChunkType) -> List[MessageChunk]:
        """Chunk content by paragraph boundaries"""
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
            
            # Check if adding this paragraph would exceed the limit
            test_chunk = current_chunk + ('\n\n' if current_chunk else '') + paragraph
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                # Save current chunk if it has content
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.PARAGRAPH_BOUNDARY))
                
                # Handle large paragraphs
                if len(paragraph) > self.max_chunk_size:
                    # Split large paragraph by sentences
                    sentence_chunks = self._chunk_by_sentences(paragraph, content_type)
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.PARAGRAPH_BOUNDARY))
        
        return chunks
    
    def _chunk_by_sentences(self, content: str, content_type: ChunkType) -> List[MessageChunk]:
        """Chunk content by sentence boundaries"""
        # Simple sentence splitting (can be improved with NLP)
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            test_chunk = current_chunk + (' ' if current_chunk else '') + sentence
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.SENTENCE_BOUNDARY))
                
                # Handle very long sentences
                if len(sentence) > self.max_chunk_size:
                    word_chunks = self._chunk_by_words(sentence, content_type)
                    chunks.extend(word_chunks)
                    current_chunk = ""
                else:
                    current_chunk = sentence
        
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.SENTENCE_BOUNDARY))
        
        return chunks
    
    def _chunk_by_lines(self, content: str, content_type: ChunkType) -> List[MessageChunk]:
        """Chunk content by line boundaries"""
        lines = content.split('\n')
        chunks = []
        current_chunk = ""
        
        for line in lines:
            test_chunk = current_chunk + ('\n' if current_chunk else '') + line
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.LINE_BOUNDARY))
                
                # Handle very long lines
                if len(line) > self.max_chunk_size:
                    word_chunks = self._chunk_by_words(line, content_type)
                    chunks.extend(word_chunks)
                    current_chunk = ""
                else:
                    current_chunk = line
        
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.LINE_BOUNDARY))
        
        return chunks
    
    def _chunk_by_words(self, content: str, content_type: ChunkType) -> List[MessageChunk]:
        """Chunk content by word boundaries"""
        words = content.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            test_chunk = current_chunk + (' ' if current_chunk else '') + word
            
            if len(test_chunk) <= self.max_chunk_size:
                current_chunk = test_chunk
            else:
                if current_chunk:
                    chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.WORD_BOUNDARY))
                
                # Handle very long words
                if len(word) > self.max_chunk_size:
                    char_chunks = self._chunk_by_characters(word, content_type)
                    chunks.extend(char_chunks)
                    current_chunk = ""
                else:
                    current_chunk = word
        
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, content_type, ChunkStrategy.WORD_BOUNDARY))
        
        return chunks
    
    def _chunk_by_characters(self, content: str, content_type: ChunkType) -> List[MessageChunk]:
        """Chunk content by character boundaries (last resort)"""
        chunks = []
        
        for i in range(0, len(content), self.max_chunk_size):
            chunk_content = content[i:i + self.max_chunk_size]
            chunks.append(self._create_chunk(chunk_content, content_type, ChunkStrategy.CHARACTER_BOUNDARY))
        
        return chunks
    
    def _chunk_large_code_block(self, code_block: str) -> List[MessageChunk]:
        """Handle large code blocks by splitting them intelligently"""
        # Extract language and content
        lines = code_block.split('\n')
        if lines[0].startswith('```'):
            language = lines[0][3:].strip()
            code_content = '\n'.join(lines[1:-1])
            has_closing = lines[-1] == '```'
        else:
            language = ""
            code_content = code_block
            has_closing = False
        
        # Split code content by lines
        code_lines = code_content.split('\n')
        chunks = []
        current_lines = []
        
        for line in code_lines:
            # Calculate size with code block wrapper
            test_content = '\n'.join(current_lines + [line])
            test_block = f"```{language}\n{test_content}\n```"
            
            if len(test_block) <= self.max_chunk_size:
                current_lines.append(line)
            else:
                if current_lines:
                    # Create chunk with code block wrapper
                    chunk_content = f"```{language}\n{chr(10).join(current_lines)}\n```"
                    chunks.append(self._create_chunk(chunk_content, ChunkType.CODE, ChunkStrategy.CODE_BLOCK_BOUNDARY))
                current_lines = [line]
        
        if current_lines:
            chunk_content = f"```{language}\n{chr(10).join(current_lines)}\n```"
            chunks.append(self._create_chunk(chunk_content, ChunkType.CODE, ChunkStrategy.CODE_BLOCK_BOUNDARY))
        
        return chunks
    
    def _create_chunk(self, 
                     content: str, 
                     content_type: ChunkType,
                     strategy: ChunkStrategy) -> MessageChunk:
        """Create a MessageChunk with basic metadata"""
        return MessageChunk(
            content=content,
            metadata=ChunkMetadata(
                chunk_index=0,  # Will be updated later
                total_chunks=0,  # Will be updated later
                chunk_type=content_type,
                strategy_used=strategy,
                original_length=0,  # Will be updated later
                chunk_length=len(content),
                has_code=self._has_code_blocks(content),
                has_markdown=self._has_markdown(content),
                context_preserved=True
            )
        )
    
    def _add_chunk_metadata(self, 
                           chunks: List[MessageChunk], 
                           original_content: str,
                           content_type: ChunkType):
        """Add metadata to all chunks"""
        total_chunks = len(chunks)
        original_length = len(original_content)
        
        for i, chunk in enumerate(chunks):
            # Update metadata
            chunk.metadata.chunk_index = i
            chunk.metadata.total_chunks = total_chunks
            chunk.metadata.original_length = original_length
            
            # Add navigation info
            if self.add_navigation and total_chunks > 1:
                chunk.navigation_info = f"📄 **Part {i + 1} of {total_chunks}**"
            
            # Add continuation marker
            if i < total_chunks - 1:
                chunk.metadata.continuation_marker = "⬇️ *Continued in next message...*"
            
            # Add preview for first chunk
            if i == 0 and self.add_previews and total_chunks > 1:
                preview = self._generate_content_preview(original_content, max_length=100)
                if preview:
                    chunk.preview = f"Preview: {preview}..."
    
    def _format_mcp_response(self, mcp_data: Dict[str, Any], include_metadata: bool) -> str:
        """Format MCP response data for display"""
        lines = []
        
        # Add main content
        if 'content' in mcp_data:
            lines.append(str(mcp_data['content']))
        elif 'message' in mcp_data:
            lines.append(str(mcp_data['message']))
        elif 'result' in mcp_data:
            if isinstance(mcp_data['result'], (dict, list)):
                lines.append(json.dumps(mcp_data['result'], indent=2, ensure_ascii=False))
            else:
                lines.append(str(mcp_data['result']))
        
        # Add metadata if requested
        if include_metadata:
            metadata_items = []
            for key, value in mcp_data.items():
                if key not in ['content', 'message', 'result']:
                    if isinstance(value, (dict, list)):
                        metadata_items.append(f"**{key}:** {json.dumps(value, ensure_ascii=False)}")
                    else:
                        metadata_items.append(f"**{key}:** {value}")
            
            if metadata_items:
                lines.extend(["", "---", "**Metadata:**"] + metadata_items)
        
        return "\n".join(lines)
    
    def _extract_mcp_title(self, mcp_data: Dict[str, Any]) -> Optional[str]:
        """Extract title from MCP data"""
        for key in ['title', 'name', 'tool', 'command']:
            if key in mcp_data:
                return str(mcp_data[key])
        return None
    
    def _generate_content_preview(self, content: str, max_length: int = 200) -> str:
        """Generate a preview of the content"""
        # Remove extra whitespace
        preview = ' '.join(content.split())
        
        # Truncate if too long
        if len(preview) > max_length:
            preview = preview[:max_length - 3] + "..."
        
        return preview


# Convenience functions for common use cases
def chunk_text(text: str, 
               max_size: int = MessageChunker.SAFE_MESSAGE_LENGTH,
               title: Optional[str] = None) -> List[MessageChunk]:
    """Convenience function to chunk plain text"""
    chunker = MessageChunker(max_chunk_size=max_size)
    return chunker.chunk_message(text, title)


def chunk_code(code: str, 
               language: str = "text",
               title: Optional[str] = None,
               max_size: int = MessageChunker.SAFE_MESSAGE_LENGTH) -> List[MessageChunk]:
    """Convenience function to chunk code"""
    chunker = MessageChunker(max_chunk_size=max_size)
    return chunker.chunk_code_output(code, language, title)


def chunk_json(data: Union[Dict, List, str],
               title: Optional[str] = None,
               max_size: int = MessageChunker.SAFE_MESSAGE_LENGTH) -> List[MessageChunk]:
    """Convenience function to chunk JSON data"""
    chunker = MessageChunker(max_chunk_size=max_size)
    return chunker.chunk_json_data(data, title)


def chunk_mcp_response(mcp_data: Dict[str, Any],
                      include_metadata: bool = True,
                      max_size: int = MessageChunker.SAFE_MESSAGE_LENGTH) -> List[MessageChunk]:
    """Convenience function to chunk MCP response"""
    chunker = MessageChunker(max_chunk_size=max_size)
    return chunker.chunk_mcp_response(mcp_data, include_metadata)