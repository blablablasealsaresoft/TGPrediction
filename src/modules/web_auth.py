"""
Simple authentication system for APOLLO Dashboard
Supports API key authentication and optional session-based auth
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable
from functools import wraps

from aiohttp import web

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass


class DashboardAuth:
    """
    Simple authentication for the dashboard
    Supports:
    - API Key authentication for programmatic access
    - Optional session-based auth for browser (future)
    """
    
    def __init__(self, master_api_key: Optional[str] = None):
        """
        Initialize authentication
        
        Args:
            master_api_key: Master API key for full access (from env)
        """
        self.master_api_key = master_api_key
        self.api_keys = {}  # Store additional API keys if needed
        
        # For future session management
        self.sessions = {}
        
        logger.info("Dashboard authentication initialized")
        if self.master_api_key:
            logger.info("Master API key is configured")
        else:
            logger.warning("⚠️ No master API key configured! Dashboard is OPEN to public!")
    
    def generate_api_key(self, user_id: str, permissions: list = None) -> str:
        """
        Generate a new API key for a user
        
        Args:
            user_id: User identifier
            permissions: List of permissions (e.g., ['read', 'write', 'admin'])
        
        Returns:
            Generated API key (32 character hex string)
        """
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        self.api_keys[key_hash] = {
            'user_id': user_id,
            'permissions': permissions or ['read'],
            'created_at': datetime.utcnow(),
            'last_used': None
        }
        
        logger.info(f"Generated API key for user {user_id}")
        return api_key
    
    def validate_api_key(self, api_key: str) -> Optional[dict]:
        """
        Validate an API key and return user info
        
        Args:
            api_key: API key to validate
        
        Returns:
            User info dict if valid, None otherwise
        """
        # Check master key first
        if self.master_api_key and api_key == self.master_api_key:
            return {
                'user_id': 'admin',
                'permissions': ['read', 'write', 'admin'],
                'is_admin': True
            }
        
        # Check stored keys
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_info = self.api_keys.get(key_hash)
        
        if key_info:
            # Update last used
            key_info['last_used'] = datetime.utcnow()
            return {
                'user_id': key_info['user_id'],
                'permissions': key_info['permissions'],
                'is_admin': 'admin' in key_info['permissions']
            }
        
        return None
    
    def require_auth(self, permissions: list = None):
        """
        Decorator to require authentication for an endpoint
        
        Args:
            permissions: Required permissions (optional)
        
        Usage:
            @auth.require_auth(['read'])
            async def get_data(request):
                user = request['user']
                ...
        """
        def decorator(handler: Callable):
            @wraps(handler)
            async def wrapped(self_or_request, *args, **kwargs):
                # Handle both class methods and standalone functions
                if isinstance(self_or_request, web.Request):
                    request = self_or_request
                else:
                    request = args[0] if args else kwargs.get('request')
                
                # If no master key configured, allow all (development mode)
                if not self.master_api_key:
                    request['user'] = {
                        'user_id': 'anonymous',
                        'permissions': ['read', 'write', 'admin'],
                        'is_admin': True
                    }
                    return await handler(self_or_request, *args, **kwargs)
                
                # Check for API key in headers
                api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')
                
                if api_key and api_key.startswith('Bearer '):
                    api_key = api_key[7:]  # Remove 'Bearer ' prefix
                
                if not api_key:
                    return web.json_response(
                        {'error': 'Missing API key', 'message': 'Provide X-API-Key header'},
                        status=401
                    )
                
                # Validate API key
                user = self.validate_api_key(api_key)
                
                if not user:
                    return web.json_response(
                        {'error': 'Invalid API key'},
                        status=401
                    )
                
                # Check permissions if required
                if permissions:
                    has_permission = any(perm in user['permissions'] for perm in permissions)
                    if not has_permission and not user.get('is_admin'):
                        return web.json_response(
                            {'error': 'Insufficient permissions'},
                            status=403
                        )
                
                # Add user to request
                request['user'] = user
                
                # Call original handler
                return await handler(self_or_request, *args, **kwargs)
            
            return wrapped
        return decorator


def setup_auth_routes(app: web.Application, auth: DashboardAuth):
    """
    Setup authentication-related routes
    
    Args:
        app: aiohttp Application
        auth: DashboardAuth instance
    """
    
    async def generate_api_key_endpoint(request: web.Request) -> web.Response:
        """Generate a new API key (admin only)"""
        try:
            data = await request.json()
            user_id = data.get('user_id')
            permissions = data.get('permissions', ['read'])
            
            if not user_id:
                return web.json_response(
                    {'error': 'user_id is required'},
                    status=400
                )
            
            api_key = auth.generate_api_key(user_id, permissions)
            
            return web.json_response({
                'api_key': api_key,
                'user_id': user_id,
                'permissions': permissions,
                'message': 'API key generated successfully. Store it securely!'
            })
        
        except Exception as e:
            logger.error(f"Error generating API key: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def validate_api_key_endpoint(request: web.Request) -> web.Response:
        """Validate an API key"""
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return web.json_response(
                {'valid': False, 'error': 'No API key provided'},
                status=400
            )
        
        user = auth.validate_api_key(api_key)
        
        if user:
            return web.json_response({
                'valid': True,
                'user_id': user['user_id'],
                'permissions': user['permissions'],
                'is_admin': user.get('is_admin', False)
            })
        else:
            return web.json_response({
                'valid': False,
                'error': 'Invalid API key'
            }, status=401)
    
    # Add routes
    # Admin route (requires master API key)
    app.router.add_post('/api/v1/auth/generate-key', 
                        auth.require_auth(['admin'])(generate_api_key_endpoint))
    
    # Public validation endpoint
    app.router.add_get('/api/v1/auth/validate', validate_api_key_endpoint)
    
    logger.info("Authentication routes configured")


def create_default_auth(master_api_key: Optional[str] = None) -> DashboardAuth:
    """
    Create default authentication instance
    
    Args:
        master_api_key: Master API key (optional, from environment)
    
    Returns:
        DashboardAuth instance
    """
    return DashboardAuth(master_api_key=master_api_key)
