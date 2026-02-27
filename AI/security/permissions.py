"""
Permission Manager Module for Secure Intelligent Desktop Assistant
Role-based access control system
"""

import logging
import json
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


class PermissionManager:
    """
    Role-Based Permission System
    Manages user roles and permissions
    """
    
    def __init__(self):
        """Initialize permission manager"""
        self.logger = logging.getLogger('DesktopAssistant.Permissions')
        self.role_permissions = config.ROLE_PERMISSIONS.copy()
        self.user_roles = {}
        self.session_data = {}
        
        self.logger.info("Permission Manager initialized")
    
    def set_user_role(self, user, role):
        """
        Set user role
        
        Args:
            user: Username
            role: Role (admin, user, guest)
            
        Returns:
            True if successful
        """
        if role not in [config.UserRole.ADMIN, config.UserRole.USER, config.UserRole.GUEST]:
            self.logger.warning(f"Invalid role: {role}")
            return False
        
        self.user_roles[user] = role
        self.logger.info(f"Set role {role} for user {user}")
        return True
    
    def get_user_role(self, user):
        """
        Get user role
        
        Args:
            user: Username
            
        Returns:
            Role or None
        """
        return self.user_roles.get(user)
    
    def has_permission(self, user, permission):
        """
        Check if user has permission
        
        Args:
            user: Username
            permission: Permission name
            
        Returns:
            True if user has permission
        """
        role = self.get_user_role(user)
        
        if not role:
            self.logger.warning(f"User {user} has no role assigned")
            return False
        
        permissions = self.role_permissions.get(role, [])
        
        has_perm = permission in permissions
        
        if not has_perm:
            self.logger.warning(f"Permission denied: {user} for {permission}")
        
        return has_perm
    
    def grant_permission(self, role, permission):
        """
        Grant permission to role
        
        Args:
            role: Role name
            permission: Permission name
            
        Returns:
            True if successful
        """
        if role not in self.role_permissions:
            self.role_permissions[role] = []
        
        if permission not in self.role_permissions[role]:
            self.role_permissions[role].append(permission)
            self.logger.info(f"Granted {permission} to {role}")
            return True
        
        return False
    
    def revoke_permission(self, role, permission):
        """
        Revoke permission from role
        
        Args:
            role: Role name
            permission: Permission name
            
        Returns:
            True if successful
        """
        if role in self.role_permissions:
            if permission in self.role_permissions[role]:
                self.role_permissions[role].remove(permission)
                self.logger.info(f"Revoked {permission} from {role}")
                return True
        
        return False
    
    def get_role_permissions(self, role):
        """
        Get permissions for role
        
        Args:
            role: Role name
            
        Returns:
            List of permissions
        """
        return self.role_permissions.get(role, [])
    
    def get_user_permissions(self, user):
        """
        Get permissions for user
        
        Args:
            user: Username
            
        Returns:
            List of permissions
        """
        role = self.get_user_role(user)
        if role:
            return self.get_role_permissions(role)
        return []
    
    def create_session(self, user, timeout=None):
        """
        Create user session
        
        Args:
            user: Username
            timeout: Session timeout in seconds
            
        Returns:
            Session ID
        """
        import uuid
        
        session_id = str(uuid.uuid4())
        
        if timeout is None:
            timeout = config.SESSION_TIMEOUT
        
        self.session_data[session_id] = {
            'user': user,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=timeout),
            'last_activity': datetime.now(),
            'active': True
        }
        
        self.logger.info(f"Created session {session_id} for user {user}")
        return session_id
    
    def validate_session(self, session_id):
        """
        Validate session
        
        Args:
            session_id: Session ID
            
        Returns:
            True if session is valid
        """
        if session_id not in self.session_data:
            return False
        
        session = self.session_data[session_id]
        
        # Check if expired
        if datetime.now() > session['expires_at']:
            session['active'] = False
            return False
        
        # Update last activity
        session['last_activity'] = datetime.now()
        
        return session['active']
    
    def end_session(self, session_id):
        """
        End user session
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful
        """
        if session_id in self.session_data:
            self.session_data[session_id]['active'] = False
            self.logger.info(f"Ended session {session_id}")
            return True
        
        return False
    
    def check_inactivity(self, session_id, timeout=None):
        """
        Check for inactivity timeout
        
        Args:
            session_id: Session ID
            timeout: Inactivity timeout in seconds
            
        Returns:
            True if should lock due to inactivity
        """
        if timeout is None:
            timeout = config.INACTIVITY_LOCK_TIMEOUT
        
        if session_id not in self.session_data:
            return True
        
        session = self.session_data[session_id]
        last_activity = session['last_activity']
        
        if datetime.now() - last_activity > timedelta(seconds=timeout):
            session['active'] = False
            self.logger.info(f"Inactivity lock for session {session_id}")
            return True
        
        return False
    
    def get_active_sessions(self):
        """Get all active sessions"""
        active = []
        
        for session_id, session in self.session_data.items():
            if session['active'] and datetime.now() < session['expires_at']:
                active.append({
                    'session_id': session_id,
                    'user': session['user'],
                    'created_at': session['created_at'],
                    'last_activity': session['last_activity']
                })
        
        return active
    
    def end_all_sessions(self, user=None):
        """
        End all sessions, optionally for specific user
        
        Args:
            user: Optional username
            
        Returns:
            Number of sessions ended
        """
        count = 0
        
        for session_id, session in self.session_data.items():
            if user is None or session['user'] == user:
                if session['active']:
                    session['active'] = False
                    count += 1
        
        if user:
            self.logger.info(f"Ended {count} sessions for user {user}")
        else:
            self.logger.info(f"Ended {count} sessions")
        
        return count


# ============================================
# Main function for testing
# ============================================

def test_permissions():
    """Test permission manager"""
    print("Testing Permission Manager...")
    
    pm = PermissionManager()
    
    # Set roles
    pm.set_user_role("admin_user", config.UserRole.ADMIN)
    pm.set_user_role("regular_user", config.UserRole.USER)
    pm.set_user_role("guest_user", config.UserRole.GUEST)
    
    # Test permissions
    print("\n" + "="*60)
    print("Testing Permissions:")
    print("="*60)
    
    test_users = [
        ("admin_user", config.Permission.FILE_MANAGEMENT),
        ("regular_user", config.Permission.FILE_MANAGEMENT),
        ("guest_user", config.Permission.FILE_MANAGEMENT),
        ("admin_user", config.Permission.SYSTEM_MONITOR),
        ("guest_user", config.Permission.SYSTEM_MONITOR),
    ]
    
    for user, permission in test_users:
        has_perm = pm.has_permission(user, permission)
        print(f"{user} has {permission}: {has_perm}")
    
    # Test sessions
    print("\n" + "="*60)
    print("Testing Sessions:")
    print("="*60)
    
    session_id = pm.create_session("test_user")
    print(f"Created session: {session_id}")
    print(f"Session valid: {pm.validate_session(session_id)}")
    print(f"Should lock (inactive): {pm.check_inactivity(session_id, timeout=1)}")
    
    # Wait a bit
    import time
    time.sleep(2)
    
    print(f"Should lock (after 2 sec): {pm.check_inactivity(session_id, timeout=1)}")
    
    pm.end_session(session_id)
    print(f"Session valid after end: {pm.validate_session(session_id)}")
    
    return pm


if __name__ == "__main__":
    test_permissions()
