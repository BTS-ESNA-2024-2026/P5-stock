# P5-Stock

Full-stack inventory management application with Flask backend and React frontend.

## Project Structure

```
P5-stock/
├── backend/           # Flask API server
│   ├── database/      # SQLAlchemy models and config
│   ├── src/           # Flask application
│   └── requirements.txt
├── frontend/          # Vite + React + TypeScript
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── pages/
│   │   ├── services/
│   │   └── styles/
│   └── package.json
├── database/          # MySQL Docker setup
├── documentation/     # Project documentation
├── package.json       # Root workspace config
└── pnpm-workspace.yaml
```

## Prerequisites

- Node.js >= 18.0.0
- pnpm >= 8.0.0
- Python >= 3.10
- MySQL (or Docker)

## Quick Start

### 1. Install dependencies

```bash
# Install pnpm if not installed
npm install -g pnpm

# Install all dependencies (frontend + dev tools)
pnpm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Setup environment variables

Create `.env` file in the `backend` folder:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/p5stock
FLASK_ENV=development
FRONTEND_URL=http://localhost:5173
```

### 3. Generate JWT keys (required for authentication)

```bash
cd backend
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
cd ..
```

### 4. Setup database

```bash
cd database/mysql-docker
docker-compose up -d
cd ../..
```

### 5. Run development servers

```bash
# Run both frontend and backend concurrently
pnpm dev

# Or run them separately:
pnpm dev:frontend  # Vite dev server on :5173
pnpm dev:backend   # Flask server on :5000
```

## Development Commands

| Command | Description |
|---------|-------------|
| `pnpm dev` | Run both frontend and backend in development mode |
| `pnpm dev:frontend` | Run only the Vite dev server |
| `pnpm dev:backend` | Run only the Flask server |
| `pnpm build` | Build frontend for production |
| `pnpm preview` | Preview production build locally |
| `pnpm lint` | Run ESLint on frontend code |

## API Endpoints

### Authentication
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `POST /auth/register` - Register new user
- `GET /auth/me` - Get current user

### Assets
- `GET /api/assets` - List all assets (with pagination & filters)
- `GET /api/assets/:id` - Get single asset
- `POST /api/asset` - Create asset
- `PUT /api/asset/:id` - Update asset
- `DELETE /api/asset/:id` - Delete asset

### Asset Types
- `GET /api/asset_types` - List all asset types
- `POST /api/asset_type` - Create asset type

### Bases
- `GET /api/bases` - List all bases
- `POST /api/base` - Create base
- `PUT /api/base/:id` - Update base

### Rooms
- `GET /api/rooms` - List all rooms
- `POST /api/room` - Create room
- `PUT /api/room/:id` - Update room

### Specs & Values
- `GET /api/specs` - List all specs
- `POST /api/specs` - Create spec
- `GET /api/values` - List all values
- `POST /api/value` - Create value
- `PUT /api/value/:id` - Update value

## Production Build

```bash
# Build frontend
pnpm build

# The built files will be in frontend/dist/
# Configure your web server to serve these static files
# and proxy API requests to the Flask backend

# Run production backend
pnpm start:prod
```

## Tech Stack

### Backend
- Flask 3.1.2
- SQLAlchemy 2.0
- Flask-CORS
- PyJWT (RS256)
- Argon2 password hashing
- MySQL

### Frontend
- React 18
- TypeScript
- Vite 6
- React Router 7
- Axios

## Security Features

- JWT authentication with RS256
- Argon2 password hashing
- CORS protection
- Rate limiting
- Role-based access control
