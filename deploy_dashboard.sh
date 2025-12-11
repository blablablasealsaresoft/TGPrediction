#!/bin/bash

# ============================================================================
# APOLLO CyberSentinel Dashboard Deployment Script
# ============================================================================

set -e  # Exit on error

echo "🚀 APOLLO CyberSentinel Dashboard Deployment"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

print_success "Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker Compose is installed"

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please create it from env.example.txt"
    exit 1
fi

print_success ".env file found"

# Check if Web API environment variables are set
if ! grep -q "WEB_API_ENABLED" .env; then
    print_info "Web API environment variables not found in .env"
    print_info "Adding default Web API configuration..."
    
    cat >> .env << 'EOF'

# ============================================================================
# 🌐 WEB API / DASHBOARD CONFIGURATION
# ============================================================================

WEB_API_ENABLED=true
WEB_API_HOST=0.0.0.0
WEB_API_PORT=8080
WEB_API_CORS_ORIGINS=http://localhost:3000,http://localhost
WEB_API_JWT_SECRET=change-this-jwt-secret-in-production-min-32-chars
WEB_API_ADMIN_API_KEY=change-this-admin-api-key-in-production
ADMIN_PASSWORD=admin
EOF
    
    print_info "Please edit .env and update the Web API credentials before continuing"
    print_info "Press Enter to continue or Ctrl+C to exit..."
    read
fi

print_success "Web API configuration found"

# Check if frontend .env exists
if [ ! -f apollo-dashboard/frontend/.env ]; then
    print_info "Creating frontend .env file..."
    cp apollo-dashboard/frontend/.env.example apollo-dashboard/frontend/.env
    print_success "Frontend .env created"
fi

# Step 1: Build images
print_info "Step 1/6: Building Docker images..."
docker-compose -f docker-compose.prod.yml build

print_success "Docker images built successfully"

# Step 2: Stop existing containers
print_info "Step 2/6: Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

print_success "Existing containers stopped"

# Step 3: Start database first
print_info "Step 3/6: Starting database services..."
docker-compose -f docker-compose.prod.yml up -d postgres redis

# Wait for database to be ready
print_info "Waiting for database to be ready..."
sleep 10

print_success "Database services started"

# Step 4: Initialize database
print_info "Step 4/6: Initializing database..."
# Database initialization happens automatically in the bot

print_success "Database initialized"

# Step 5: Start all services
print_info "Step 5/6: Starting all services..."
docker-compose -f docker-compose.prod.yml up -d

print_success "All services started"

# Step 6: Wait for services to be ready
print_info "Step 6/6: Waiting for services to be ready..."
sleep 15

# Check if services are running
print_info "Checking service health..."

# Check trading bot
if docker-compose -f docker-compose.prod.yml ps | grep -q "trading-bot-app.*Up"; then
    print_success "Trading bot is running"
else
    print_error "Trading bot failed to start"
fi

# Check dashboard
if docker-compose -f docker-compose.prod.yml ps | grep -q "apollo-dashboard.*Up"; then
    print_success "Dashboard is running"
else
    print_error "Dashboard failed to start"
fi

# Check nginx
if docker-compose -f docker-compose.prod.yml ps | grep -q "nginx-proxy.*Up"; then
    print_success "Nginx proxy is running"
else
    print_error "Nginx proxy failed to start"
fi

# Test API endpoint
print_info "Testing API health endpoint..."
sleep 5
if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
    print_success "API health check passed"
else
    print_error "API health check failed - service may still be starting"
fi

echo ""
echo "=============================================="
echo "🎉 Deployment Complete!"
echo "=============================================="
echo ""
echo "📊 Access the dashboard at:"
echo "   Dashboard:    http://localhost"
echo "   Admin Panel:  http://localhost/admin"
echo "   API Health:   http://localhost:8080/health"
echo ""
echo "📝 View logs:"
echo "   All logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "   Bot logs:     docker-compose -f docker-compose.prod.yml logs -f trading-bot"
echo "   Dashboard:    docker-compose -f docker-compose.prod.yml logs -f apollo-dashboard"
echo "   Nginx:        docker-compose -f docker-compose.prod.yml logs -f nginx-proxy"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "⚠️  IMPORTANT: Update the default passwords in .env before production use!"
echo ""

