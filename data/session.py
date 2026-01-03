"""
Session Management

Organizes test data into sessions with automatic directory creation
and metadata tracking.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class Session:
    """Represents a testing session with metadata and file organization."""

    def __init__(self, session_id: str, base_dir: Path = Path("data/sessions")):
        """
        Initialize session.

        Args:
            session_id: Unique session identifier
            base_dir: Base directory for sessions
        """
        self.session_id = session_id
        self.base_dir = Path(base_dir)
        self.session_dir = self.base_dir / session_id

        # Metadata
        self.metadata = {
            'session_id': session_id,
            'created': datetime.now().isoformat(),
            'platform': 'unknown',
            'hardware': {},
            'tests': [],
            'notes': ''
        }

        # Subdirectories
        self.plots_dir = self.session_dir / 'plots'
        self.data_dir = self.session_dir / 'data'
        self.config_dir = self.session_dir / 'config'

    def create(self, platform: str = 'teensy', hardware_info: dict = None):
        """
        Create session directory structure.

        Args:
            platform: Hardware platform used
            hardware_info: Hardware configuration dict
        """
        # Create directories
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

        # Update metadata
        self.metadata['platform'] = platform
        if hardware_info:
            self.metadata['hardware'] = hardware_info

        # Save metadata
        self.save_metadata()

    def add_test(self, test_id: str, test_type: str, config: dict,
                 data_file: Optional[Path] = None,
                 plot_files: Optional[List[Path]] = None) -> dict:
        """
        Add test to session.

        Args:
            test_id: Unique test identifier
            test_type: Type of test (e.g., 'torque', 'hold')
            config: Test configuration dict
            data_file: Path to CSV data file (relative to session_dir)
            plot_files: List of plot file paths

        Returns:
            Test record dict
        """
        test_record = {
            'test_id': test_id,
            'test_type': test_type,
            'timestamp': datetime.now().isoformat(),
            'config': config,
            'data_file': str(data_file) if data_file else None,
            'plot_files': [str(p) for p in plot_files] if plot_files else [],
            'status': 'completed'
        }

        self.metadata['tests'].append(test_record)
        self.save_metadata()

        return test_record

    def get_test_count(self) -> int:
        """Get number of tests in session."""
        return len(self.metadata['tests'])

    def get_tests_by_type(self, test_type: str) -> List[dict]:
        """Get all tests of a specific type."""
        return [t for t in self.metadata['tests'] if t['test_type'] == test_type]

    def get_latest_test(self) -> Optional[dict]:
        """Get most recent test."""
        if self.metadata['tests']:
            return self.metadata['tests'][-1]
        return None

    def save_metadata(self):
        """Save session metadata to JSON file."""
        metadata_file = self.session_dir / 'session.json'
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def load_metadata(self):
        """Load session metadata from JSON file."""
        metadata_file = self.session_dir / 'session.json'
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                self.metadata = json.load(f)

    def set_notes(self, notes: str):
        """Set session notes."""
        self.metadata['notes'] = notes
        self.save_metadata()

    def get_data_file_path(self, test_id: str, filename: str) -> Path:
        """
        Get path for test data file.

        Args:
            test_id: Test identifier
            filename: Data filename

        Returns:
            Full path for data file
        """
        return self.data_dir / f"{test_id}_{filename}"

    def get_plot_file_path(self, test_id: str, plot_name: str,
                          extension: str = 'png') -> Path:
        """
        Get path for test plot file.

        Args:
            test_id: Test identifier
            plot_name: Plot name
            extension: File extension (default 'png')

        Returns:
            Full path for plot file
        """
        return self.plots_dir / f"{test_id}_{plot_name}.{extension}"

    def exists(self) -> bool:
        """Check if session directory exists."""
        return self.session_dir.exists()

    def delete(self):
        """Delete session directory and all contents."""
        import shutil
        if self.session_dir.exists():
            shutil.rmtree(self.session_dir)

    def get_summary(self) -> dict:
        """
        Get session summary.

        Returns:
            Dict with session statistics
        """
        return {
            'session_id': self.session_id,
            'created': self.metadata.get('created'),
            'platform': self.metadata.get('platform'),
            'num_tests': len(self.metadata['tests']),
            'test_types': list(set(t['test_type'] for t in self.metadata['tests'])),
            'notes': self.metadata.get('notes', '')
        }


class SessionManager:
    """Manages multiple testing sessions."""

    def __init__(self, base_dir: Path = Path("data/sessions")):
        """
        Initialize session manager.

        Args:
            base_dir: Base directory for all sessions
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, prefix: str = "session",
                      platform: str = 'teensy',
                      hardware_info: dict = None) -> Session:
        """
        Create new session with unique ID.

        Args:
            prefix: Session ID prefix
            platform: Hardware platform
            hardware_info: Hardware configuration

        Returns:
            New Session instance
        """
        # Generate unique session ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{timestamp}_{prefix}"

        # Create session
        session = Session(session_id, self.base_dir)
        session.create(platform, hardware_info)

        return session

    def load_session(self, session_id: str) -> Optional[Session]:
        """
        Load existing session.

        Args:
            session_id: Session identifier

        Returns:
            Session instance or None if not found
        """
        session = Session(session_id, self.base_dir)

        if session.exists():
            session.load_metadata()
            return session

        return None

    def list_sessions(self, sort_by: str = 'created') -> List[dict]:
        """
        List all sessions.

        Args:
            sort_by: Sort key ('created', 'session_id', 'num_tests')

        Returns:
            List of session summary dicts
        """
        sessions = []

        # Find all session directories
        for session_dir in self.base_dir.iterdir():
            if session_dir.is_dir():
                session_id = session_dir.name
                session = Session(session_id, self.base_dir)

                if session.exists():
                    try:
                        session.load_metadata()
                        sessions.append(session.get_summary())
                    except Exception as e:
                        print(f"Error loading session {session_id}: {e}")

        # Sort sessions
        if sort_by == 'created':
            sessions.sort(key=lambda s: s.get('created', ''), reverse=True)
        elif sort_by == 'session_id':
            sessions.sort(key=lambda s: s['session_id'], reverse=True)
        elif sort_by == 'num_tests':
            sessions.sort(key=lambda s: s.get('num_tests', 0), reverse=True)

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully
        """
        session = Session(session_id, self.base_dir)
        if session.exists():
            session.delete()
            return True
        return False

    def get_session_count(self) -> int:
        """Get total number of sessions."""
        return len(list(self.base_dir.iterdir()))

    def find_sessions_by_platform(self, platform: str) -> List[dict]:
        """
        Find sessions by platform.

        Args:
            platform: Platform name (e.g., 'teensy', 'mock')

        Returns:
            List of matching session summaries
        """
        all_sessions = self.list_sessions()
        return [s for s in all_sessions if s.get('platform') == platform]

    def find_sessions_by_test_type(self, test_type: str) -> List[dict]:
        """
        Find sessions containing a specific test type.

        Args:
            test_type: Test type (e.g., 'torque', 'hold')

        Returns:
            List of matching session summaries
        """
        matching_sessions = []

        for session_dir in self.base_dir.iterdir():
            if session_dir.is_dir():
                session_id = session_dir.name
                session = Session(session_id, self.base_dir)

                try:
                    session.load_metadata()
                    test_types = [t['test_type'] for t in session.metadata['tests']]

                    if test_type in test_types:
                        matching_sessions.append(session.get_summary())
                except:
                    continue

        return matching_sessions
