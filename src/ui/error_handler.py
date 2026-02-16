"""
Comprehensive Error Handler with Recovery Mechanisms

This module provides user-friendly error handling, loading indicators,
confirmation messages, and real-time input validation for the Smart Bus Dashboard.

Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Any, Dict, List
import streamlit as st
import time
from contextlib import contextmanager


class ErrorSeverity(Enum):
    """Error severity levels for appropriate user feedback."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Classification of error types for targeted recovery strategies."""
    DATA_MISSING = "data_missing"
    DATA_CORRUPTED = "data_corrupted"
    DATA_FORMAT = "data_format"
    NETWORK = "network"
    PERMISSION = "permission"
    VALIDATION = "validation"
    SYSTEM = "system"
    EXPORT = "export"
    IMPORT = "import"
    CACHE = "cache"
    CONFIGURATION = "configuration"


@dataclass
class ErrorMessage:
    """Structured error message with recovery guidance."""
    title: str
    description: str
    severity: ErrorSeverity
    error_type: ErrorType
    suggested_solutions: List[str]
    recovery_actions: List[Dict[str, Any]]
    technical_details: Optional[str] = None
    
    def display(self) -> None:
        """Display the error message with appropriate Streamlit component."""
        # Choose appropriate Streamlit display method based on severity
        if self.severity == ErrorSeverity.INFO:
            st.info(f"**{self.title}**\n\n{self.description}")
        elif self.severity == ErrorSeverity.WARNING:
            st.warning(f"**{self.title}**\n\n{self.description}")
        elif self.severity == ErrorSeverity.ERROR:
            st.error(f"**{self.title}**\n\n{self.description}")
        elif self.severity == ErrorSeverity.CRITICAL:
            st.error(f"🚨 **{self.title}**\n\n{self.description}")
        
        # Display suggested solutions
        if self.suggested_solutions:
            st.markdown("**💡 Suggested Solutions:**")
            for i, solution in enumerate(self.suggested_solutions, 1):
                st.markdown(f"{i}. {solution}")
        
        # Display recovery actions as buttons
        if self.recovery_actions:
            st.markdown("**🔧 Recovery Actions:**")
            cols = st.columns(len(self.recovery_actions))
            for idx, action in enumerate(self.recovery_actions):
                with cols[idx]:
                    if st.button(action.get('label', 'Retry'), key=f"recovery_{id(self)}_{idx}"):
                        callback = action.get('callback')
                        if callback and callable(callback):
                            callback()
        
        # Show technical details in expander
        if self.technical_details:
            with st.expander("🔍 Technical Details"):
                st.code(self.technical_details)


@dataclass
class ConfirmationMessage:
    """Structured confirmation message for successful operations."""
    title: str
    description: str
    icon: str = "✅"
    duration: float = 3.0
    
    def display(self) -> None:
        """Display the confirmation message."""
        st.success(f"{self.icon} **{self.title}**\n\n{self.description}")


@dataclass
class ValidationResult:
    """Result of input validation with feedback."""
    is_valid: bool
    message: str
    field_name: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    
    def display(self) -> None:
        """Display validation feedback."""
        if self.is_valid:
            st.success(f"✓ {self.field_name}: {self.message}")
        else:
            if self.severity == ErrorSeverity.WARNING:
                st.warning(f"⚠ {self.field_name}: {self.message}")
            else:
                st.error(f"✗ {self.field_name}: {self.message}")


class LoadingIndicator:
    """Context manager for displaying loading indicators during operations."""
    
    def __init__(self, message: str = "Processing...", show_spinner: bool = True):
        """
        Initialize loading indicator.
        
        Args:
            message: Message to display during loading
            show_spinner: Whether to show spinner animation
        """
        self.message = message
        self.show_spinner = show_spinner
        self.spinner_context = None
        self.progress_bar = None
        self.status_text = None
        
    def __enter__(self):
        """Start displaying loading indicator."""
        if self.show_spinner:
            self.spinner_context = st.spinner(self.message)
            self.spinner_context.__enter__()
        else:
            self.status_text = st.empty()
            self.status_text.info(f"⏳ {self.message}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop displaying loading indicator."""
        if self.spinner_context:
            self.spinner_context.__exit__(exc_type, exc_val, exc_tb)
        if self.status_text:
            self.status_text.empty()
        if self.progress_bar:
            self.progress_bar.empty()
        return False
    
    def update_progress(self, progress: float, message: Optional[str] = None):
        """
        Update progress indicator.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional message to display with progress
        """
        if not self.progress_bar:
            self.progress_bar = st.progress(0)
        
        self.progress_bar.progress(progress)
        
        if message and self.status_text:
            self.status_text.info(f"⏳ {message}")


class ErrorHandler:
    """
    Comprehensive error handler with recovery mechanisms.
    
    Provides user-friendly error messages, loading indicators, confirmation messages,
    and real-time input validation for the Smart Bus Dashboard.
    
    Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
    """
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_log: List[ErrorMessage] = []
        
    def handle_data_missing_error(
        self,
        file_path: str,
        recovery_callback: Optional[Callable] = None
    ) -> ErrorMessage:
        """
        Handle missing data file errors with recovery guidance.
        
        Args:
            file_path: Path to the missing file
            recovery_callback: Optional callback for recovery action
            
        Returns:
            ErrorMessage with recovery guidance
            
        Validates: Requirements 4.1, 4.4
        """
        recovery_actions = []
        if recovery_callback:
            recovery_actions.append({
                'label': 'Browse for File',
                'callback': recovery_callback
            })
        
        error = ErrorMessage(
            title="Data File Not Found",
            description=f"The required data file could not be found: `{file_path}`",
            severity=ErrorSeverity.ERROR,
            error_type=ErrorType.DATA_MISSING,
            suggested_solutions=[
                f"Verify that the file `{file_path}` exists in the correct location",
                "Check file permissions to ensure the application can read the file",
                "If the file was moved or renamed, update the configuration",
                "Upload a new data file using the file browser"
            ],
            recovery_actions=recovery_actions,
            technical_details=f"File path: {file_path}"
        )
        
        self.error_log.append(error)
        return error
    
    def handle_data_corrupted_error(
        self,
        file_path: str,
        error_details: str,
        recovery_callback: Optional[Callable] = None
    ) -> ErrorMessage:
        """
        Handle corrupted data file errors with recovery guidance.
        
        Args:
            file_path: Path to the corrupted file
            error_details: Details about the corruption
            recovery_callback: Optional callback for recovery action
            
        Returns:
            ErrorMessage with recovery guidance
            
        Validates: Requirements 4.1, 4.4
        """
        recovery_actions = []
        if recovery_callback:
            recovery_actions.append({
                'label': 'Upload New File',
                'callback': recovery_callback
            })
        
        error = ErrorMessage(
            title="Data File Corrupted",
            description=f"The data file appears to be corrupted or invalid: `{file_path}`",
            severity=ErrorSeverity.ERROR,
            error_type=ErrorType.DATA_CORRUPTED,
            suggested_solutions=[
                "Restore the file from a backup if available",
                "Re-download or regenerate the data file",
                "Check if the file was partially downloaded or transferred",
                "Verify the file format matches the expected structure",
                "Upload a new valid data file"
            ],
            recovery_actions=recovery_actions,
            technical_details=f"File: {file_path}\nError: {error_details}"
        )
        
        self.error_log.append(error)
        return error
    
    def handle_data_format_error(
        self,
        file_path: str,
        expected_format: str,
        actual_format: str,
        recovery_callback: Optional[Callable] = None
    ) -> ErrorMessage:
        """
        Handle data format mismatch errors with conversion guidance.
        
        Args:
            file_path: Path to the file with format issues
            expected_format: Expected file format
            actual_format: Actual detected format
            recovery_callback: Optional callback for recovery action
            
        Returns:
            ErrorMessage with recovery guidance
            
        Validates: Requirements 4.1, 4.4
        """
        recovery_actions = []
        if recovery_callback:
            recovery_actions.append({
                'label': 'Convert Format',
                'callback': recovery_callback
            })
        
        error = ErrorMessage(
            title="Data Format Mismatch",
            description=f"The file format does not match the expected format.\n\nExpected: `{expected_format}`\nFound: `{actual_format}`",
            severity=ErrorSeverity.WARNING,
            error_type=ErrorType.DATA_FORMAT,
            suggested_solutions=[
                f"Convert the file to {expected_format} format",
                "Verify you're using the correct file for this operation",
                "Check the file extension matches the content",
                "Use the automatic format conversion tool if available"
            ],
            recovery_actions=recovery_actions,
            technical_details=f"File: {file_path}\nExpected: {expected_format}\nActual: {actual_format}"
        )
        
        self.error_log.append(error)
        return error
    
    def handle_validation_error(
        self,
        field_name: str,
        value: Any,
        constraint: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> ErrorMessage:
        """
        Handle input validation errors with real-time feedback.
        
        Args:
            field_name: Name of the field being validated
            value: The invalid value
            constraint: Description of the constraint that was violated
            severity: Severity level of the validation error
            
        Returns:
            ErrorMessage with validation guidance
            
        Validates: Requirements 4.5
        """
        error = ErrorMessage(
            title=f"Invalid Input: {field_name}",
            description=f"The value `{value}` does not meet the required constraints.",
            severity=severity,
            error_type=ErrorType.VALIDATION,
            suggested_solutions=[
                f"Ensure the value meets this requirement: {constraint}",
                "Check for typos or formatting issues",
                "Refer to the help documentation for valid input examples"
            ],
            recovery_actions=[],
            technical_details=f"Field: {field_name}\nValue: {value}\nConstraint: {constraint}"
        )
        
        self.error_log.append(error)
        return error
    
    def handle_export_error(
        self,
        export_format: str,
        error_details: str,
        retry_callback: Optional[Callable] = None
    ) -> ErrorMessage:
        """
        Handle export operation errors with retry mechanisms.
        
        Args:
            export_format: The format that failed to export
            error_details: Details about the export failure
            retry_callback: Optional callback to retry the export
            
        Returns:
            ErrorMessage with recovery guidance
            
        Validates: Requirements 4.1
        """
        recovery_actions = []
        if retry_callback:
            recovery_actions.append({
                'label': 'Retry Export',
                'callback': retry_callback
            })
        
        error = ErrorMessage(
            title=f"Export Failed: {export_format}",
            description=f"Failed to export data in {export_format} format.",
            severity=ErrorSeverity.ERROR,
            error_type=ErrorType.EXPORT,
            suggested_solutions=[
                "Try exporting in a different format (CSV, PDF, or Excel)",
                "Check available disk space",
                "Verify you have write permissions to the download location",
                "Reduce the amount of data being exported",
                "Close other applications that might be using the file"
            ],
            recovery_actions=recovery_actions,
            technical_details=f"Format: {export_format}\nError: {error_details}"
        )
        
        self.error_log.append(error)
        return error
    
    def handle_system_error(
        self,
        operation: str,
        error_details: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> ErrorMessage:
        """
        Handle general system errors with appropriate guidance.
        
        Args:
            operation: The operation that failed
            error_details: Details about the system error
            severity: Severity level of the error
            
        Returns:
            ErrorMessage with recovery guidance
            
        Validates: Requirements 4.1
        """
        error = ErrorMessage(
            title=f"System Error: {operation}",
            description=f"An unexpected error occurred during {operation}.",
            severity=severity,
            error_type=ErrorType.SYSTEM,
            suggested_solutions=[
                "Refresh the page and try again",
                "Clear your browser cache and cookies",
                "Check your internet connection",
                "Try using a different browser",
                "Contact support if the problem persists"
            ],
            recovery_actions=[],
            technical_details=f"Operation: {operation}\nError: {error_details}"
        )
        
        self.error_log.append(error)
        return error
    
    def show_confirmation(
        self,
        title: str,
        description: str,
        icon: str = "✅",
        duration: float = 3.0
    ) -> None:
        """
        Display a confirmation message for successful operations.
        
        Args:
            title: Title of the confirmation
            description: Description of what succeeded
            icon: Icon to display (default: ✅)
            duration: How long to display (for future auto-dismiss)
            
        Validates: Requirements 4.3
        """
        confirmation = ConfirmationMessage(
            title=title,
            description=description,
            icon=icon,
            duration=duration
        )
        confirmation.display()
    
    def validate_input(
        self,
        field_name: str,
        value: Any,
        validator: Callable[[Any], tuple[bool, str]],
        display_feedback: bool = True
    ) -> ValidationResult:
        """
        Validate user input with real-time feedback.
        
        Args:
            field_name: Name of the field being validated
            value: The value to validate
            validator: Function that returns (is_valid, message)
            display_feedback: Whether to display feedback immediately
            
        Returns:
            ValidationResult with validation outcome
            
        Validates: Requirements 4.5
        """
        is_valid, message = validator(value)
        
        result = ValidationResult(
            is_valid=is_valid,
            message=message,
            field_name=field_name,
            severity=ErrorSeverity.ERROR if not is_valid else ErrorSeverity.INFO
        )
        
        if display_feedback:
            result.display()
        
        return result
    
    @contextmanager
    def loading_operation(
        self,
        message: str = "Processing...",
        show_spinner: bool = True
    ):
        """
        Context manager for operations that need loading indicators.
        
        Args:
            message: Message to display during loading
            show_spinner: Whether to show spinner animation
            
        Yields:
            LoadingIndicator instance for progress updates
            
        Validates: Requirements 4.2
        
        Example:
            with error_handler.loading_operation("Loading data...") as loader:
                # Perform operation
                loader.update_progress(0.5, "Processing records...")
                # Continue operation
        """
        indicator = LoadingIndicator(message, show_spinner)
        with indicator:
            yield indicator
    
    def get_error_log(self) -> List[ErrorMessage]:
        """
        Get the log of all errors that have occurred.
        
        Returns:
            List of ErrorMessage objects
        """
        return self.error_log.copy()
    
    def clear_error_log(self) -> None:
        """Clear the error log."""
        self.error_log.clear()


# Singleton instance for global access
_error_handler_instance: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """
    Get the global ErrorHandler instance.
    
    Returns:
        Global ErrorHandler instance
    """
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
    return _error_handler_instance


# Convenience functions for common operations

def show_error(
    title: str,
    description: str,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    suggested_solutions: Optional[List[str]] = None,
    technical_details: Optional[str] = None
) -> None:
    """
    Show a simple error message.
    
    Args:
        title: Error title
        description: Error description
        severity: Error severity level
        suggested_solutions: Optional list of suggested solutions
        technical_details: Optional technical details
        
    Validates: Requirements 4.1
    """
    error = ErrorMessage(
        title=title,
        description=description,
        severity=severity,
        error_type=ErrorType.SYSTEM,
        suggested_solutions=suggested_solutions or [],
        recovery_actions=[],
        technical_details=technical_details
    )
    error.display()


def show_success(title: str, description: str, icon: str = "✅") -> None:
    """
    Show a success confirmation message.
    
    Args:
        title: Success title
        description: Success description
        icon: Icon to display
        
    Validates: Requirements 4.3
    """
    get_error_handler().show_confirmation(title, description, icon)


def with_loading(message: str = "Processing..."):
    """
    Decorator for functions that need loading indicators.
    
    Args:
        message: Message to display during loading
        
    Returns:
        Decorated function
        
    Validates: Requirements 4.2
    
    Example:
        @with_loading("Loading data...")
        def load_data():
            # Function implementation
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with get_error_handler().loading_operation(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator
