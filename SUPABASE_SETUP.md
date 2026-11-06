# 🎉 SIMPLIFIED SUPABASE SETUP

No more DATABASE_URL complexity! Now you only need **2 environment variables**.

## Step 1: Get Your Supabase Credentials

1. Go to https://supabase.com/dashboard
2. Select your project (or create a new one)
3. Go to **Settings** → **API**
4. You'll need TWO values:

### A. Project URL
Look for "Project URL" - copy it
```
Example: https://abcdefghij.supabase.co
```

### B. Anon/Public Key
Look for "Project API keys" → **anon** **public** - copy it
```
Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6...
```

## Step 2: Update Your .env File

Edit `backend/.env` and update these two lines:

```bash
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_KEY_HERE
```

That's it! No DATABASE_URL needed anymore!

## Step 3: Create Tables in Supabase

1. Go to Supabase Dashboard → SQL Editor
2. Click "New query"
3. Paste the SQL from `supabase_schema.sql`
4. Click "Run"

## Step 4: Test Locally

```bash
cd backend
python3 main.py
```

Visit http://localhost:8000/docs to see the API!

## Step 5: Deploy to Railway

1. Go to https://railway.app/dashboard
2. Select your backend project
3. Go to **Variables** tab
4. **REMOVE** the `DATABASE_URL` variable (if it exists)
5. Update/Add only these variables:

```
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.YOUR_KEY_HERE
SECRET_KEY=f3d3757d345b75c84e443998c097f6c84604b70c350d5509a4e62dbb81950acd
WEBHOOK_SECRET=bd1d9e71b674a06c3402425a6988a8bb381ba88d44e94f59d0b4d0ca7919fe13
WHITECHAIN_RPC_URL=https://rpc.testnet.whitechain.io
WHITECHAIN_CHAIN_ID=1874
USDT_CONTRACT_ADDRESS=0xcedfB56113143d55b2358b8CFbB0dEB5Ad2f55a7
BACKEND_URL=https://web-production-7892c.up.railway.app
FRONTEND_URL=http://localhost:3000
```

6. Railway will automatically redeploy!

## That's It!

✅ No PostgreSQL connection strings
✅ No connection pooling confusion
✅ Just 2 simple environment variables from Supabase
✅ Easy to set up and maintain

Your backend will now use Supabase's REST API for all database operations!
