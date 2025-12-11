#!/bin/bash

##############################################################################
# APOLLO CyberSentinel Dashboard Deployment Script
# Version: 2.0 Enterprise
# Author: APOLLO CyberSentinel Team
# Inspired by: Gates (scalability), Buffett (risk management), McAfee (security)
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DASHBOARD_PORT=8080
API_PORT=8081
NGINX_PORT=80

##############################################################################
# Helper Functions
##############################################################################

print_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
    ___    ____  ____  __    __    ____ 
   /   |  / __ \/ __ \/ /   / /   / __ \
  / /| | / /_/ / / / / /   / /   / / / /
 / ___ |/ ____/ /_/ / /___/ /___/ /_/ / 
/_/  |_/_/    \____/_____/_____/\____/  
                                        
 CyberSentinel Enterprise Trading Platform
 Dashboard Deployment Script v2.0
EOF
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${PURPLE}▶️  $1${NC}"
}

##############################################################################
# Prerequisite Checks
##############################################################################

check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    log_success "Docker installed: $(docker --version)"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    log_success "Docker Compose installed: $(docker-compose --version)"
    
    # Check if running as root (not recommended)
    if [ "$EUID" -eq 0 ]; then
        log_warning "Running as root is not recommended for security."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$available_space" -lt 10 ]; then
        log_warning "Low disk space: ${available_space}GB available (10GB minimum recommended)"
    fi
    
    # Check if port 8080 is available
    if lsof -Pi :$DASHBOARD_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "Port $DASHBOARD_PORT is already in use"
        read -p "Use different port? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "Enter port number: " DASHBOARD_PORT
        fi
    fi
    
    log_success "All prerequisites met!"
}

##############################################################################
# Project Setup
##############################################################################

setup_project_structure() {
    log_step "Setting up project structure..."
    
    # Create directories
    mkdir -p frontend backend docs nginx logs backups
    
    # Create subdirectories
    mkdir -p docs/{api,user,admin,architecture}
    mkdir -p logs/{app,nginx,system}
    mkdir -p backups/{daily,weekly,monthly}
    
    log_success "Project structure created"
}

##############################################################################
# Generate Configuration Files
##############################################################################

generate_nginx_config() {
    log_step "Generating Nginx configuration..."
    
    cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 4096;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    limit_req_zone $binary_remote_addr zone=dashboard_limit:10m rate=30r/m;

    # Upstream servers
    upstream dashboard {
        server frontend:3000;
    }

    upstream api {
        server backend:8081;
    }

    # Dashboard server
    server {
        listen 80;
        server_name _;

        # Dashboard
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
            
            limit_req zone=dashboard_limit burst=10 nodelay;
        }

        # API proxy
        location /api/ {
            proxy_pass http://api/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_cache_bypass $http_upgrade;
            
            limit_req zone=api_limit burst=20 nodelay;
        }

        # WebSocket endpoint
        location /ws {
            proxy_pass http://api/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "Upgrade";
            proxy_set_header Host $host;
            proxy_read_timeout 86400;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
    
    log_success "Nginx configuration generated"
}

generate_docker_compose() {
    log_step "Generating Docker Compose configuration..."
    
    cat > docker-compose.dashboard.yml << EOF
version: '3.8'

services:
  # Frontend Dashboard
  frontend:
    image: nginx:alpine
    container_name: apollo-dashboard
    ports:
      - "${DASHBOARD_PORT}:80"
    volumes:
      - ./index.html:/usr/share/nginx/html/index.html:ro
      - ./docs:/usr/share/nginx/html/docs:ro
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # API Documentation Server
  docs:
    image: nginx:alpine
    container_name: apollo-docs
    ports:
      - "8082:80"
    volumes:
      - ./docs:/usr/share/nginx/html:ro
    restart: unless-stopped

networks:
  default:
    name: apollo-network
    external: true
EOF
    
    log_success "Docker Compose configuration generated"
}

##############################################################################
# Copy Documentation Files
##############################################################################

copy_documentation() {
    log_step "Copying documentation files..."
    
    # Copy main docs to docs directory
    if [ -f "ENTERPRISE_README.md" ]; then
        cp ENTERPRISE_README.md docs/index.md
        log_success "Main README copied"
    fi
    
    if [ -f "COMPLETE_API_DOCS.md" ]; then
        cp COMPLETE_API_DOCS.md docs/api/index.md
        log_success "API documentation copied"
    fi
    
    # Create index.html for docs
    cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APOLLO CyberSentinel - Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #050814 100%);
            color: #f0f0f0;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #00d4ff;
            margin-bottom: 2rem;
        }
        .doc-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        .doc-card {
            background: rgba(10, 14, 39, 0.8);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 10px;
            padding: 2rem;
            transition: all 0.3s;
        }
        .doc-card:hover {
            transform: translateY(-5px);
            border-color: #00d4ff;
        }
        .doc-card h2 {
            color: #00d4ff;
            margin-bottom: 1rem;
        }
        .doc-card p {
            color: #aaa;
            margin-bottom: 1rem;
        }
        .doc-card a {
            color: #00d4ff;
            text-decoration: none;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 APOLLO CyberSentinel Documentation</h1>
        <div class="doc-grid">
            <div class="doc-card">
                <h2>🏢 Enterprise README</h2>
                <p>Complete system overview, features, and quick start guide</p>
                <a href="index.md">View Documentation →</a>
            </div>
            <div class="doc-card">
                <h2>🔌 API Documentation</h2>
                <p>Complete REST API reference with examples</p>
                <a href="api/index.md">View API Docs →</a>
            </div>
            <div class="doc-card">
                <h2>📊 Dashboard</h2>
                <p>Access the live monitoring dashboard</p>
                <a href="/">Go to Dashboard →</a>
            </div>
        </div>
    </div>
</body>
</html>
EOF
    
    log_success "Documentation structure created"
}

##############################################################################
# Deploy Services
##############################################################################

deploy_services() {
    log_step "Deploying services..."
    
    # Create network if it doesn't exist
    if ! docker network inspect apollo-network &> /dev/null; then
        docker network create apollo-network
        log_success "Docker network created"
    fi
    
    # Start services
    docker-compose -f docker-compose.dashboard.yml up -d
    
    log_success "Services deployed"
}

##############################################################################
# Health Checks
##############################################################################

perform_health_checks() {
    log_step "Performing health checks..."
    
    sleep 5  # Wait for services to start
    
    # Check dashboard
    if curl -f http://localhost:$DASHBOARD_PORT/health &> /dev/null; then
        log_success "Dashboard is healthy"
    else
        log_error "Dashboard health check failed"
    fi
    
    # Check if containers are running
    if docker ps | grep apollo-dashboard &> /dev/null; then
        log_success "Dashboard container is running"
    else
        log_error "Dashboard container is not running"
    fi
}

##############################################################################
# Display Summary
##############################################################################

display_summary() {
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║        ✅ APOLLO CyberSentinel Dashboard Deployed!        ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Get server IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    echo -e "${CYAN}📊 Access Points:${NC}"
    echo -e "   Dashboard:      ${GREEN}http://localhost:$DASHBOARD_PORT${NC}"
    echo -e "   Dashboard (IP): ${GREEN}http://$SERVER_IP:$DASHBOARD_PORT${NC}"
    echo -e "   Documentation:  ${GREEN}http://localhost:8082${NC}"
    echo ""
    
    echo -e "${CYAN}🔧 Useful Commands:${NC}"
    echo -e "   View logs:    ${YELLOW}docker-compose -f docker-compose.dashboard.yml logs -f${NC}"
    echo -e "   Stop:         ${YELLOW}docker-compose -f docker-compose.dashboard.yml down${NC}"
    echo -e "   Restart:      ${YELLOW}docker-compose -f docker-compose.dashboard.yml restart${NC}"
    echo -e "   Status:       ${YELLOW}docker-compose -f docker-compose.dashboard.yml ps${NC}"
    echo ""
    
    echo -e "${CYAN}📚 Documentation Files:${NC}"
    echo -e "   Main README:  ${YELLOW}./ENTERPRISE_README.md${NC}"
    echo -e "   API Docs:     ${YELLOW}./COMPLETE_API_DOCS.md${NC}"
    echo -e "   Dashboard:    ${YELLOW}./index.html${NC}"
    echo ""
    
    echo -e "${CYAN}🔐 Security Notes:${NC}"
    echo -e "   • Change default passwords immediately"
    echo -e "   • Configure firewall rules"
    echo -e "   • Enable HTTPS for production"
    echo -e "   • Review security settings in .env"
    echo ""
    
    log_success "Deployment complete! 🚀"
}

##############################################################################
# Main Execution
##############################################################################

main() {
    print_banner
    
    log_info "Starting APOLLO CyberSentinel Dashboard deployment..."
    echo ""
    
    check_prerequisites
    echo ""
    
    setup_project_structure
    generate_nginx_config
    generate_docker_compose
    copy_documentation
    echo ""
    
    deploy_services
    echo ""
    
    perform_health_checks
    echo ""
    
    display_summary
}

# Run main function
main "$@"
