"""Simple Flask OAuth demo for ATProto SDK.

This demonstrates basic OAuth flow with the atproto_oauth package.
For production use, implement proper session management and error handling.

Run with:
    uv run python examples/oauth_flask_demo/app.py
"""

import os
from urllib.parse import urlencode

from atproto_oauth import OAuthClient
from atproto_oauth.stores import MemorySessionStore, MemoryStateStore
from flask import Flask, jsonify, redirect, request, session

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'development-secret-key-change-in-production')

# OAuth configuration
# For localhost testing, client_id is special localhost URL
REDIRECT_URI = 'http://127.0.0.1:5000/callback'
SCOPE = 'atproto'

# Create client_id for localhost testing
CLIENT_ID = 'http://localhost?' + urlencode(
    {
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
    }
)

# Initialize OAuth client with memory stores (for demo only!)
oauth_client = OAuthClient(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    state_store=MemoryStateStore(),
    session_store=MemorySessionStore(),
)


@app.route('/')
def index() -> str:
    """Homepage."""
    if 'user_did' in session:
        return f"""
        <html>
            <body>
                <h1>ATProto OAuth Demo</h1>
                <p>Logged in as: {session.get('user_handle')} ({session.get('user_did')})</p>
                <p><a href="/logout">Logout</a></p>
            </body>
        </html>
        """

    return """
    <html>
        <body>
            <h1>ATProto OAuth Demo</h1>
            <form action="/login" method="post">
                <label for="handle">Enter your Bluesky handle:</label><br>
                <input type="text" id="handle" name="handle" placeholder="user.bsky.social" required><br><br>
                <input type="submit" value="Login with OAuth">
            </form>
        </body>
    </html>
    """


@app.route('/login', methods=['POST'])
def login() -> str:
    """Start OAuth flow."""
    handle = request.form.get('handle', '').strip().removeprefix('@')

    if not handle:
        return 'Handle required', 400

    try:
        # Start OAuth authorization
        import asyncio

        auth_url, state = asyncio.run(oauth_client.start_authorization(handle))

        # Store state in session for verification
        session['oauth_state'] = state

        # Redirect user to authorization server
        return redirect(auth_url)

    except Exception:  # noqa: BLE001
        import traceback

        error_msg = traceback.format_exc()
        return (f'<html><body><h1>Login Error</h1><pre>{error_msg}</pre><p><a href="/">Back</a></p></body></html>'), 500


@app.route('/callback')
def callback() -> str:
    """Handle OAuth callback."""
    # Check for errors
    if error := request.args.get('error'):
        error_desc = request.args.get('error_description', '')
        return (
            f'<html><body><h1>Authorization Error</h1><p>{error}: {error_desc}</p>'
            f'<p><a href="/">Back</a></p></body></html>'
        ), 400

    # Get authorization code and parameters
    code = request.args.get('code')
    state = request.args.get('state')
    iss = request.args.get('iss')

    if not code or not state or not iss:
        return 'Missing required parameters', 400

    # Verify state matches what we stored
    stored_state = session.get('oauth_state')
    if not stored_state or stored_state != state:
        return 'Invalid state parameter', 400

    try:
        # Complete OAuth flow
        import asyncio

        oauth_session = asyncio.run(oauth_client.handle_callback(code, state, iss))

        # Store user info in session
        session['user_did'] = oauth_session.did
        session['user_handle'] = oauth_session.handle
        session.pop('oauth_state', None)

        return redirect('/')

    except Exception as e:  # noqa: BLE001
        return f'<html><body><h1>Callback Error</h1><p>{e!s}</p><p><a href="/">Back</a></p></body></html>', 500


@app.route('/logout')
def logout() -> str:
    """Logout and revoke OAuth session."""
    user_did = session.get('user_did')

    if user_did:
        try:
            # Revoke OAuth session
            import asyncio

            oauth_session = asyncio.run(oauth_client.session_store.get_session(user_did))
            if oauth_session:
                asyncio.run(oauth_client.revoke_session(oauth_session))
        except Exception as e:  # noqa: BLE001
            print(f'Error revoking session: {e}')

    # Clear browser session
    session.clear()
    return redirect('/')


@app.route('/api/profile')
def api_profile() -> tuple:
    """Example API endpoint using OAuth session."""
    user_did = session.get('user_did')
    if not user_did:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        import asyncio

        # Get OAuth session
        oauth_session = asyncio.run(oauth_client.session_store.get_session(user_did))
        if not oauth_session:
            return jsonify({'error': 'Session not found'}), 401

        # Make authenticated request to PDS
        response = asyncio.run(
            oauth_client.make_authenticated_request(
                session=oauth_session,
                method='GET',
                url=f'{oauth_session.pds_url}/xrpc/com.atproto.repo.describeRepo?repo={user_did}',
            )
        )

        if response.status_code != 200:
            return jsonify({'error': 'PDS request failed', 'status': response.status_code}), 500

        return jsonify(response.json())

    except Exception as e:  # noqa: BLE001
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print('Starting ATProto OAuth Flask demo...')
    print('Visit http://127.0.0.1:5000 to test OAuth flow')
    print()
    print('Note: This is a development demo. For production:')
    print('  - Use persistent state/session stores (not memory)')
    print('  - Implement proper error handling')
    print('  - Use HTTPS')
    print('  - Set a strong secret key')
    print()
    app.run(debug=True, port=5000)  # noqa: S201
