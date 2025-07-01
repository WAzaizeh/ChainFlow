from typing import List, Optional, Dict
from appwrite.services.users import Users
from appwrite.services.teams import Teams
from core.appwrite_client import create_client
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class AuthDatabase:
    def __init__(self):
        self.client = create_client(authenticated=True)
        self.users = Users(self.client)
        self.teams = Teams(self.client)

    def create_user(self, email: str, password: str, name: str, phone : str = None, branch_id: str = None) -> Dict:
        """Create a new user and add them to their branch team"""
        try:
            logger.info(f"Creating user: {email} for branch: {branch_id}")
            
            # Create user
            user = self.users.create(
                user_id='unique()',
                email=email,
                password=password,
                phone=phone,
                name=name
            )
            
            # Add to branch team
            self.teams.create_membership(
                team_id=branch_id,
                email=email,
                roles=['member']
            )
            
            logger.info(f"User created successfully: {user['$id']}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    def get_user_teams(self) -> List[Dict]:
        """Get all teams a user belongs to"""
        try:
            memberships = self.teams.list()
            print(f"Memberships: {memberships}")
            return memberships['teams'] if memberships and 'teams' in memberships else []
        except Exception as e:
            logger.error(f"Failed to get user teams: {e}")
            return []

    def get_user_branch(self, session: Dict) -> Optional[str]:
        """Get user's branch ID from their team membership"""
        if not session.get('user'):
            return None
            
        teams = self.get_user_teams()
        
        # First team ID is the branch ID
        return teams[0]['name'] if teams else None

    def is_admin(self, user_id: str) -> bool:
        """Check if user has admin role"""
            
        user_info = self.users.get(user_id)
        print(f"User info: {user_info}")

        return user_info.get('labels', []) == ['admin']

    def create_branch(self, name: str) -> Dict:
        """Create a new branch team"""
        try:
            logger.info(f"Creating branch team: {name}")
            team = self.teams.create(
                team_id='unique()',
                name=name
            )
            logger.info(f"Branch team created: {team['$id']}")
            return team
        except Exception as e:
            logger.error(f"Failed to create branch: {e}")
            raise

    def delete_user(self, user_id: str) -> bool:
        """Delete a user and remove from teams"""
        try:
            logger.info(f"Deleting user: {user_id}")
            self.users.delete(user_id)
            logger.info("User deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False

    def update_user(self, user_id: str, **updates) -> Dict:
        """Update user details"""
        try:
            logger.info(f"Updating user {user_id}: {updates}")
            user = self.users.update(user_id, **updates)
            logger.info("User updated successfully")
            return user
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise