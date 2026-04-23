# Project P5

## Quick Start - Dev Container (Recommended)

[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/BTS-ESNA-2024-2026/P5-stock.git)
[![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=green&logo=github)](https://codespaces.new/BTS-ESNA-2024-2026/P5-stock)

Or follow these steps:

1. Install [VS Code](https://code.visualstudio.com/) and the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Clone the repository:
   ```sh
   git clone https://github.com/BTS-ESNA-2024-2026/P5-stock.git
   cd P5-stock
   ```
3. Open in VS Code and click "Reopen in Container" when prompted
4. The dev container will automatically install all dependencies and set up the environment

---

## Manual Setup

### Requirements
- Node.js >= 24.0.0
- pnpm >= 10.0.0
- Python >= 3.11
- uv (Python package manager)
- Docker & Docker Compose

### Clone the Repository
```sh
git clone https://github.com/BTS-ESNA-2024-2026/P5-stock.git
cd P5-stock
```

### Install Dependencies
This is a monorepo with frontend and backend. Install both using:
```sh
pnpm i
```

This will:
- Install Node dependencies (frontend + root)
- Install Python dependencies (backend) via uv

### Generate RSA Keys
/!\ DO NOT SHARE **private.pem** EVER /!\
```sh
pnpm genkey
```

This generates `private.pem` and `public.pem` in the backend directory.

### Run the Application

#### Development Mode (Frontend + Backend)
```sh
pnpm dev
```

Or run them separately:
```sh
# Terminal 1 - Frontend (http://localhost:5173)
pnpm dev:frontend

# Terminal 2 - Backend (http://localhost:8000)
pnpm dev:backend
```

#### Production Mode
```sh
# Build frontend
pnpm build:frontend

# Start backend
pnpm start:backend
```

### Docker Setup
For database and services, see `docker/dev/docker-compose.yml`:
```sh
cd docker/dev
docker compose up
```

### Login Credentials
Default test credentials:
- Username: `defadm`
- Password: `yaa`

Access the app at http://localhost:5173
