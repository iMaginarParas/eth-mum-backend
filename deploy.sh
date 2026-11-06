#!/bin/bash

# PayLink Backend Deployment Script for Railway
# Run this script to deploy your backend to Railway

set -e

echo "🚀 PayLink Backend Deployment to Railway"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${RED}❌ Railway CLI is not installed${NC}"
    echo "Install it with: npm install -g @railway/cli"
    exit 1
fi

echo -e "${GREEN}✓ Railway CLI is installed${NC}"

# Step 1: Login
echo ""
echo "Step 1: Login to Railway"
echo "------------------------"
railway whoami &> /dev/null || {
    echo "You need to login to Railway..."
    railway login
}

echo -e "${GREEN}✓ Logged in to Railway${NC}"

# Step 2: Initialize project (if not already done)
echo ""
echo "Step 2: Initialize Railway Project"
echo "-----------------------------------"

if [ ! -f ".railway" ]; then
    echo "Initializing new Railway project..."
    railway init
else
    echo -e "${GREEN}✓ Railway project already initialized${NC}"
fi

# Step 3: Add PostgreSQL (if not already added)
echo ""
echo "Step 3: Add PostgreSQL Database"
echo "--------------------------------"
echo "Adding PostgreSQL to your project..."
railway add -d postgresql || echo -e "${YELLOW}PostgreSQL may already be added${NC}"

# Step 4: Generate secrets
echo ""
echo "Step 4: Generate Secret Keys"
echo "-----------------------------"

SECRET_KEY=$(openssl rand -hex 32)
WEBHOOK_SECRET=$(openssl rand -hex 32)

echo -e "${GREEN}✓ Generated SECRET_KEY: ${SECRET_KEY}${NC}"
echo -e "${GREEN}✓ Generated WEBHOOK_SECRET: ${WEBHOOK_SECRET}${NC}"

# Step 5: Set environment variables
echo ""
echo "Step 5: Set Environment Variables"
echo "----------------------------------"

echo "⚠️  You need to provide your deployed contract addresses:"
read -p "Enter PAYMENT_PROCESSOR_ADDRESS: " PAYMENT_PROCESSOR
read -p "Enter REFUND_MANAGER_ADDRESS: " REFUND_MANAGER

echo ""
echo "Setting environment variables..."

railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set WEBHOOK_SECRET="$WEBHOOK_SECRET"
railway variables set WHITECHAIN_RPC_URL="https://rpc.testnet.whitechain.io"
railway variables set WHITECHAIN_CHAIN_ID="1874"
railway variables set USDT_CONTRACT_ADDRESS="0xcedfB56113143d55b2358b8CFbB0dEB5Ad2f55a7"
railway variables set PAYMENT_PROCESSOR_ADDRESS="$PAYMENT_PROCESSOR"
railway variables set REFUND_MANAGER_ADDRESS="$REFUND_MANAGER"

echo -e "${GREEN}✓ Environment variables set${NC}"

# Step 6: Deploy
echo ""
echo "Step 6: Deploy to Railway"
echo "--------------------------"
echo "Deploying your application..."

railway up

echo -e "${GREEN}✓ Deployment initiated${NC}"

# Step 7: Get domain
echo ""
echo "Step 7: Get Deployment URL"
echo "---------------------------"

DOMAIN=$(railway domain 2>&1)

if [[ $DOMAIN == *"No custom domain configured"* ]]; then
    echo "Creating a custom domain..."
    railway domain
    DOMAIN=$(railway domain 2>&1)
fi

echo -e "${GREEN}✓ Your app URL: $DOMAIN${NC}"

# Step 8: Run migrations
echo ""
echo "Step 8: Run Database Migrations"
echo "--------------------------------"
echo "Running Alembic migrations..."

railway run alembic upgrade head

echo -e "${GREEN}✓ Migrations complete${NC}"

# Final steps
echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Your PayLink backend is now live at:"
echo -e "${GREEN}$DOMAIN${NC}"
echo ""
echo "Next steps:"
echo "1. Test health endpoint: curl $DOMAIN/health"
echo "2. View API docs: $DOMAIN/docs"
echo "3. View logs: railway logs"
echo "4. Monitor: railway open"
echo ""
echo "Update these URLs:"
echo "- Set BACKEND_URL to: railway variables set BACKEND_URL=\"$DOMAIN\""
echo "- Update frontend .env with: NEXT_PUBLIC_API_URL=$DOMAIN"
echo "- Update demo-store with backend URL"
echo ""
echo "Deployment details saved to deployment.log"

# Save deployment info
cat > deployment.log << EOF
PayLink Backend Deployment
==========================
Date: $(date)
Domain: $DOMAIN
Secret Key: $SECRET_KEY
Webhook Secret: $WEBHOOK_SECRET
Payment Processor: $PAYMENT_PROCESSOR
Refund Manager: $REFUND_MANAGER

Commands:
- View logs: railway logs
- View dashboard: railway open
- Restart: railway restart
- View variables: railway variables

Health Check: $DOMAIN/health
API Docs: $DOMAIN/docs
EOF

echo -e "${GREEN}✓ Deployment information saved to deployment.log${NC}"
