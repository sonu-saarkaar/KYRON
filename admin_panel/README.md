# KYRON Master Admin Panel

Production-grade admin panel for KYRON AI Digital Execution Agent.

## Features

- **Role-Based Access Control**: 5-tier role hierarchy (MASTER_ADMIN, SUPER_ADMIN, ADMIN, OPERATOR, VIEWER)
- **JWT Authentication**: Secure access and refresh token system
- **Admin Management**: Create, block, and manage admin accounts (MASTER_ADMIN only)
- **User Management**: View and manage KYRON users
- **Comprehensive Logging**: Login logs, agent logs, and error logs
- **System Control**: Toggle KYRON agent status and manage system settings
- **Modern UI**: Dark/Light theme support, responsive design

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Start MongoDB

Ensure MongoDB is running on `localhost:27017` (or update `MONGODB_URL` in `backend/core/config.py`)

### 3. Initialize Master Admin

```bash
cd backend
python init_admin.py
```

Follow the prompts to create your first MASTER_ADMIN account.

### 4. Start Backend Server

```bash
cd backend
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open Admin Panel

Open `admin_panel/login.html` in your browser, or serve it via a local web server:

```bash
# Using Python's built-in server
cd admin_panel
python -m http.server 5500
```

Then navigate to: `http://localhost:5500/login.html`

## API Endpoints

### Authentication
- `POST /auth/login` - Admin login
- `POST /auth/logout` - Admin logout
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current admin info

### Admin Management (MASTER_ADMIN only)
- `POST /admins/create` - Create new admin
- `PATCH /admins/block` - Block/unblock admin
- `GET /admins` - List all admins
- `DELETE /admins/{admin_id}` - Delete admin

### User Management
- `GET /users` - List all users

### Logs
- `GET /logs/login` - Get login logs
- `GET /logs/agent` - Get agent logs
- `GET /logs/error` - Get error logs

### System (MASTER_ADMIN only)
- `GET /system/status` - Get system status
- `POST /system/agent-toggle` - Toggle agent ON/OFF
- `GET /system/settings` - Get system settings
- `POST /system/settings` - Update system settings

## Role Permissions

### MASTER_ADMIN
- All permissions
- Create/delete/block admins
- Assign roles
- Toggle agent status
- View all logs (including sensitive data)
- System settings management

### SUPER_ADMIN
- View all admins and users
- View all logs
- System status view

### ADMIN
- View and manage users
- View agent and error logs

### OPERATOR
- View users
- View agent logs

### VIEWER
- View users
- View agent logs (read-only)

## Security Features

- JWT-based authentication with refresh tokens
- Bcrypt password hashing (12 rounds)
- Role-based route guards
- Login audit logging (IP, device, timestamp)
- Token expiry and refresh flow
- CORS enabled for Chrome Extension & Admin UI

## Database Collections

- `admins` - Admin accounts
- `users` - KYRON users
- `login_logs` - Login attempts
- `agent_logs` - Agent activity logs
- `error_logs` - System error logs
- `system_settings` - System configuration

## Configuration

Edit `backend/core/config.py` to customize:
- MongoDB connection URL
- JWT secret key and expiration
- CORS origins
- Role permissions

## Notes

- The admin panel uses vanilla JavaScript (no React/Vue)
- All API calls use Fetch API
- Tokens are stored in localStorage
- Theme preference is saved in localStorage

