#!/bin/bash

# 🦄 APOLLO CyberSentinel - Dashboard Suite Setup Script
# Automated deployment script by Bill Gates, Warren Buffett, and John McAfee
# Version: 1.0.0

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis
SUCCESS="✅"
FAIL="❌"
INFO="ℹ️"
ROCKET="🚀"
GEAR="⚙️"
LOCK="🔐"
CHART="📊"
BOOK="📚"
TOOLS="🔧"

# Banner
echo -e "${PURPLE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      🦄 APOLLO CyberSentinel - Dashboard Suite             ║
║                                                              ║
║      Enterprise-Grade Monitoring & Administration           ║
║                                                              ║
║      Built by: Bill Gates • Warren Buffett • John McAfee   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}${ROCKET} Starting automated setup...${NC}\n"

# Check if running in correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}${FAIL} Error: docker-compose.yml not found!${NC}"
    echo -e "${YELLOW}Please run this script from the apollo-dashboard directory.${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check Prerequisites
echo -e "${BLUE}${GEAR} Step 1/10: Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}${FAIL} Docker not found!${NC}"
    echo -e "${YELLOW}Please install Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    echo -e "${RED}${FAIL} Docker Compose not found!${NC}"
    echo -e "${YELLOW}Please install Docker Compose: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${YELLOW}${INFO} Node.js not found. Installing is recommended for development.${NC}"
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}${SUCCESS} Node.js ${NODE_VERSION} detected${NC}"
fi

echo -e "${GREEN}${SUCCESS} Prerequisites check passed!${NC}\n"

# Step 2: Create Directory Structure
echo -e "${BLUE}${GEAR} Step 2/10: Creating directory structure...${NC}"

mkdir -p frontend/src frontend/public backend/src backend/routes backend/services backend/middleware
mkdir -p docs nginx/ssl logs
mkdir -p /mnt/user-data/outputs

echo -e "${GREEN}${SUCCESS} Directories created!${NC}\n"

# Step 3: Generate Secure Keys
echo -e "${BLUE}${LOCK} Step 3/10: Generating secure keys...${NC}"

if [ ! -f .env ]; then
    echo "Generating .env file..."
    
    # Generate random keys
    ADMIN_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    DB_PASSWORD=$(openssl rand -hex 16)
    
    cat > .env << EOF
# APOLLO Dashboard Suite Configuration
# Generated: $(date)

# Admin API Security
ADMIN_API_KEY=${ADMIN_KEY}
JWT_SECRET=${JWT_SECRET}

# Database
DATABASE_URL=postgresql://trader:${DB_PASSWORD}@trading-bot-db:5432/trading_bot
DB_PASSWORD=${DB_PASSWORD}

# Redis
REDIS_URL=redis://trading-bot-redis:6379

# Application
NODE_ENV=production
PORT=8081

# Frontend
REACT_APP_API_URL=http://localhost:8080
REACT_APP_WS_URL=ws://localhost:8080/ws

# Optional: SSL
SSL_ENABLED=false
DOMAIN=dashboard.apollocybersentinel.com
EOF

    echo -e "${GREEN}${SUCCESS} Generated .env file with secure keys!${NC}"
    echo -e "${YELLOW}${LOCK} IMPORTANT: Keep these keys secret!${NC}"
    echo -e "${CYAN}Admin API Key: ${ADMIN_KEY}${NC}"
else
    echo -e "${YELLOW}${INFO} .env file already exists, skipping...${NC}"
fi

echo ""

# Step 4: Setup Frontend
echo -e "${BLUE}${CHART} Step 4/10: Setting up React frontend...${NC}"

cd frontend

if [ ! -f package.json ]; then
    echo "Creating React application..."
    
    # Create package.json
    cat > package.json << 'EOF'
{
  "name": "apollo-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "react-scripts": "5.0.1",
    "recharts": "^2.10.0",
    "lucide-react": "^0.292.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

    # Create public/index.html
    mkdir -p public
    cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="APOLLO CyberSentinel - Enterprise Trading Dashboard" />
    <title>APOLLO Dashboard</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

    # Create src/index.js
    cat > src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

    # Create src/App.js
    cat > src/App.js << 'EOF'
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './Dashboard';
import AdminPanel from './AdminPanel';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/admin" element={<AdminPanel />} />
      </Routes>
    </BrowserRouter>
  );
}
EOF

    echo -e "${GREEN}${SUCCESS} Frontend structure created!${NC}"
else
    echo -e "${YELLOW}${INFO} Frontend already initialized${NC}"
fi

# Install dependencies if node is available
if command_exists npm; then
    echo "Installing npm dependencies..."
    npm install --silent
    echo -e "${GREEN}${SUCCESS} Dependencies installed!${NC}"
fi

cd ..
echo ""

# Step 5: Setup Backend
echo -e "${BLUE}${GEAR} Step 5/10: Setting up Express backend...${NC}"

cd backend

if [ ! -f package.json ]; then
    cat > package.json << 'EOF'
{
  "name": "apollo-admin-api",
  "version": "1.0.0",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "dev": "nodemon src/server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "compression": "^1.7.4",
    "morgan": "^1.10.0",
    "dotenv": "^16.3.1",
    "pg": "^8.11.3",
    "ioredis": "^5.3.2",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  }
}
EOF

    echo -e "${GREEN}${SUCCESS} Backend structure created!${NC}"
    
    if command_exists npm; then
        echo "Installing backend dependencies..."
        npm install --silent
        echo -e "${GREEN}${SUCCESS} Backend dependencies installed!${NC}"
    fi
else
    echo -e "${YELLOW}${INFO} Backend already initialized${NC}"
fi

cd ..
echo ""

# Step 6: Create Dockerfiles
echo -e "${BLUE}${TOOLS} Step 6/10: Creating Docker configurations...${NC}"

# Frontend Dockerfile
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
EOF

# Frontend Nginx config
cat > frontend/nginx.conf << 'EOF'
server {
    listen 3000;
    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }
}
EOF

# Backend Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 8081
CMD ["node", "src/server.js"]
EOF

echo -e "${GREEN}${SUCCESS} Docker configurations created!${NC}\n"

# Step 7: Create Docker Network
echo -e "${BLUE}${GEAR} Step 7/10: Setting up Docker network...${NC}"

if docker network ls | grep -q "apollo-network"; then
    echo -e "${YELLOW}${INFO} Network already exists${NC}"
else
    docker network create apollo-network
    echo -e "${GREEN}${SUCCESS} Docker network created!${NC}"
fi

echo ""

# Step 8: Build Images
echo -e "${BLUE}${TOOLS} Step 8/10: Building Docker images...${NC}"
echo -e "${YELLOW}This may take a few minutes...${NC}\n"

docker-compose build --no-cache

echo -e "${GREEN}${SUCCESS} Images built successfully!${NC}\n"

# Step 9: Start Services
echo -e "${BLUE}${ROCKET} Step 9/10: Starting all services...${NC}"

docker-compose up -d

echo ""
echo -e "${GREEN}${SUCCESS} All services started!${NC}\n"

# Wait for services to initialize
echo -e "${YELLOW}${INFO} Waiting for services to initialize (30 seconds)...${NC}"
sleep 30

# Step 10: Verify Deployment
echo -e "${BLUE}${GEAR} Step 10/10: Verifying deployment...${NC}"

# Check if containers are running
CONTAINERS=$(docker-compose ps --services --filter "status=running" | wc -l)
EXPECTED=4

if [ "$CONTAINERS" -ge "$EXPECTED" ]; then
    echo -e "${GREEN}${SUCCESS} All containers running!${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Only $CONTAINERS/$EXPECTED containers running${NC}"
fi

# Test endpoints
echo ""
echo -e "${CYAN}Testing endpoints...${NC}"

# Health check
if curl -s http://localhost/health > /dev/null; then
    echo -e "${GREEN}${SUCCESS} Health check: PASSED${NC}"
else
    echo -e "${RED}${FAIL} Health check: FAILED${NC}"
fi

# Dashboard
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}${SUCCESS} Dashboard: ACCESSIBLE${NC}"
else
    echo -e "${YELLOW}⚠️  Dashboard: Not responding yet (may need more time)${NC}"
fi

# Documentation
if curl -s http://localhost:3001/docs > /dev/null; then
    echo -e "${GREEN}${SUCCESS} Documentation: ACCESSIBLE${NC}"
else
    echo -e "${YELLOW}⚠️  Documentation: Not responding yet${NC}"
fi

# Admin API
if curl -s http://localhost:8081/health > /dev/null; then
    echo -e "${GREEN}${SUCCESS} Admin API: ACCESSIBLE${NC}"
else
    echo -e "${YELLOW}⚠️  Admin API: Not responding yet${NC}"
fi

echo ""

# Final Summary
echo -e "${PURPLE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                 🎉 SETUP COMPLETE! 🎉                       ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${GREEN}${SUCCESS} Your APOLLO Dashboard Suite is ready!${NC}\n"

echo -e "${CYAN}📊 Access Your Dashboards:${NC}"
echo -e "   ${CHART} Main Dashboard:    ${BLUE}http://localhost:3000${NC}"
echo -e "   ${BOOK} Documentation:     ${BLUE}http://localhost:3001/docs${NC}"
echo -e "   ${LOCK} Admin Panel:       ${BLUE}http://localhost:3000/admin${NC}"
echo -e "   ${GEAR} Health Check:      ${BLUE}http://localhost/health${NC}"

echo ""
echo -e "${CYAN}🔐 Your Admin Credentials:${NC}"
echo -e "   ${LOCK} API Key: ${YELLOW}$(grep ADMIN_API_KEY .env | cut -d '=' -f2)${NC}"

echo ""
echo -e "${CYAN}📝 Useful Commands:${NC}"
echo -e "   View logs:          ${YELLOW}docker-compose logs -f${NC}"
echo -e "   Stop services:      ${YELLOW}docker-compose down${NC}"
echo -e "   Restart services:   ${YELLOW}docker-compose restart${NC}"
echo -e "   View status:        ${YELLOW}docker-compose ps${NC}"

echo ""
echo -e "${CYAN}📚 Documentation:${NC}"
echo -e "   README:             ${YELLOW}cat README.md${NC}"
echo -e "   Deployment Guide:   ${YELLOW}cat DEPLOYMENT_GUIDE.md${NC}"

echo ""
echo -e "${GREEN}${ROCKET} Happy Trading!${NC}"
echo -e "${PURPLE}Built with 💎 by APOLLO CyberSentinel${NC}\n"

# Save setup info
cat > SETUP_INFO.txt << EOF
APOLLO Dashboard Suite - Setup Information
Generated: $(date)

Access URLs:
- Dashboard: http://localhost:3000
- Documentation: http://localhost:3001/docs
- Admin Panel: http://localhost:3000/admin
- Health Check: http://localhost/health

Admin API Key: $(grep ADMIN_API_KEY .env | cut -d '=' -f2)

Container Status:
$(docker-compose ps)

Setup completed successfully!
EOF

echo -e "${INFO} Setup information saved to SETUP_INFO.txt\n"

exit 0
