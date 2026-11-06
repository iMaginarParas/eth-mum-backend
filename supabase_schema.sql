-- PayLink Database Schema for Supabase
-- Run this SQL in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('created', 'pending', 'confirmed', 'failed', 'expired');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE refund_status AS ENUM ('pending', 'processing', 'completed', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create merchants table
CREATE TABLE IF NOT EXISTS merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR NOT NULL UNIQUE,
    business_name VARCHAR NOT NULL,
    wallet_address VARCHAR NOT NULL,
    payout_address VARCHAR NOT NULL,
    api_key VARCHAR NOT NULL UNIQUE,
    webhook_url VARCHAR,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create index on email and api_key for faster lookups
CREATE INDEX IF NOT EXISTS idx_merchants_email ON merchants(email);
CREATE INDEX IF NOT EXISTS idx_merchants_api_key ON merchants(api_key);

-- Create payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id VARCHAR NOT NULL UNIQUE,
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    amount NUMERIC(36, 18) NOT NULL,
    currency VARCHAR DEFAULT 'USDT',
    customer_wallet VARCHAR,
    merchant_wallet VARCHAR NOT NULL,
    status payment_status DEFAULT 'created',
    order_id VARCHAR,
    description VARCHAR,
    payment_metadata VARCHAR,
    checkout_url VARCHAR,
    success_url VARCHAR,
    cancel_url VARCHAR,
    tx_hash VARCHAR,
    block_number VARCHAR,
    expires_at TIMESTAMP,
    confirmed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes on payments
CREATE INDEX IF NOT EXISTS idx_payments_payment_id ON payments(payment_id);
CREATE INDEX IF NOT EXISTS idx_payments_merchant_id ON payments(merchant_id);
CREATE INDEX IF NOT EXISTS idx_payments_tx_hash ON payments(tx_hash);

-- Create refunds table
CREATE TABLE IF NOT EXISTS refunds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    refund_id VARCHAR NOT NULL UNIQUE,
    payment_id UUID NOT NULL REFERENCES payments(id),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    amount NUMERIC(36, 18) NOT NULL,
    reason VARCHAR,
    customer_wallet VARCHAR NOT NULL,
    status refund_status DEFAULT 'pending',
    tx_hash VARCHAR,
    block_number VARCHAR,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes on refunds
CREATE INDEX IF NOT EXISTS idx_refunds_refund_id ON refunds(refund_id);
CREATE INDEX IF NOT EXISTS idx_refunds_payment_id ON refunds(payment_id);
CREATE INDEX IF NOT EXISTS idx_refunds_merchant_id ON refunds(merchant_id);
CREATE INDEX IF NOT EXISTS idx_refunds_tx_hash ON refunds(tx_hash);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_merchants_updated_at ON merchants;
CREATE TRIGGER update_merchants_updated_at
    BEFORE UPDATE ON merchants
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_payments_updated_at ON payments;
CREATE TRIGGER update_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_refunds_updated_at ON refunds;
CREATE TRIGGER update_refunds_updated_at
    BEFORE UPDATE ON refunds
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
