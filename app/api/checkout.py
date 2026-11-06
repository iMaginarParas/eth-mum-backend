from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from app.core.supabase import get_supabase
from app.core.config import settings

router = APIRouter(tags=["checkout"])


@router.get("/checkout/{payment_id}", response_class=HTMLResponse)
async def checkout_page(payment_id: str):
    """Display checkout page for payment"""
    supabase = get_supabase()

    # Get payment details
    result = supabase.table('payments').select('*').eq('payment_id', payment_id).execute()

    if not result.data or len(result.data) == 0:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Not Found</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body style="font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5;">
            <div style="text-align: center; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1 style="color: #ff4444;">❌ Payment Not Found</h1>
                <p>This payment link is invalid or has expired.</p>
            </div>
        </body>
        </html>
        """, status_code=404)

    payment = result.data[0]

    # Check if expired or already paid
    if payment['status'] == 'expired':
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Expired</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body style="font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f5f5f5;">
            <div style="text-align: center; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 500px;">
                <h1 style="color: #ff9800;">⏰ Payment Expired</h1>
                <p>This payment request has expired.</p>
                <p style="color: #666;">Payment ID: {payment_id}</p>
            </div>
        </body>
        </html>
        """)

    if payment['status'] == 'confirmed':
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Complete</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body style="font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; background: #f5f5f5;">
            <div style="text-align: center; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 500px;">
                <h1 style="color: #00d4aa;">✅ Payment Complete!</h1>
                <p>This invoice has already been paid.</p>
                <p style="color: #666;">Payment ID: {payment_id}</p>
                <p style="color: #666;">TX: {payment.get('tx_hash', 'N/A')[:20]}...</p>
            </div>
        </body>
        </html>
        """)

    # Show payment checkout page
    amount = payment['amount']
    merchant_wallet = payment['merchant_wallet']
    description = payment.get('description', 'Payment')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PayLink - Pay with Crypto</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}

            .container {{
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 500px;
                width: 100%;
                padding: 40px;
            }}

            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}

            .logo {{
                font-size: 32px;
                font-weight: bold;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
            }}

            .amount {{
                font-size: 48px;
                font-weight: bold;
                color: #2d3436;
                margin: 20px 0;
            }}

            .currency {{
                color: #6c5ce7;
                font-size: 24px;
            }}

            .description {{
                color: #636e72;
                margin-bottom: 30px;
            }}

            .wallet-info {{
                background: #f5f6fa;
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
            }}

            .wallet-label {{
                color: #636e72;
                font-size: 14px;
                margin-bottom: 8px;
            }}

            .wallet-address {{
                font-family: 'Courier New', monospace;
                font-size: 12px;
                word-break: break-all;
                background: white;
                padding: 12px;
                border-radius: 8px;
                border: 2px solid #dfe6e9;
                color: #2d3436;
            }}

            .btn {{
                width: 100%;
                padding: 16px;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                margin-top: 10px;
            }}

            .btn-primary {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}

            .btn-primary:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.4);
            }}

            .btn-secondary {{
                background: #f5f6fa;
                color: #2d3436;
            }}

            .btn-secondary:hover {{
                background: #dfe6e9;
            }}

            .network-badge {{
                display: inline-block;
                background: #00d4aa;
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                margin-top: 20px;
            }}

            .instructions {{
                background: #fff5e6;
                border-left: 4px solid #fdcb6e;
                padding: 15px;
                margin: 20px 0;
                border-radius: 8px;
            }}

            .instructions-title {{
                font-weight: bold;
                color: #2d3436;
                margin-bottom: 10px;
            }}

            .instructions ol {{
                padding-left: 20px;
                color: #636e72;
            }}

            .instructions li {{
                margin: 8px 0;
            }}

            #status {{
                text-align: center;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                display: none;
            }}

            .status-checking {{
                background: #fff5e6;
                color: #e67e22;
            }}

            .status-confirmed {{
                background: #d4edda;
                color: #155724;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">💳 PayLink</div>
                <p style="color: #636e72;">Crypto Payment Gateway</p>
            </div>

            <div style="text-align: center;">
                <div class="amount">{amount} <span class="currency">USDT</span></div>
                <div class="description">{description}</div>
                <span class="network-badge">🌐 Whitechain Testnet</span>
            </div>

            <div class="wallet-info">
                <div class="wallet-label">📍 Send USDT to:</div>
                <div class="wallet-address" id="walletAddress">{merchant_wallet}</div>
            </div>

            <button class="btn btn-primary" onclick="connectWallet()">
                🦊 Connect MetaMask & Pay
            </button>

            <button class="btn btn-secondary" onclick="copyAddress()">
                📋 Copy Wallet Address
            </button>

            <div class="instructions">
                <div class="instructions-title">📝 Payment Instructions:</div>
                <ol>
                    <li>Click "Connect MetaMask & Pay" button above</li>
                    <li>Approve the transaction in MetaMask</li>
                    <li>Wait for blockchain confirmation (~2 seconds)</li>
                    <li>Payment complete! ✅</li>
                </ol>
            </div>

            <div id="status"></div>

            <div style="text-align: center; margin-top: 30px; color: #b2bec3; font-size: 12px;">
                Payment ID: {payment_id}
            </div>
        </div>

        <script>
            const PAYMENT_ID = '{payment_id}';
            const AMOUNT = '{amount}';
            const MERCHANT_WALLET = '{merchant_wallet}';
            const USDT_ADDRESS = '{settings.USDT_CONTRACT_ADDRESS}';
            const CHAIN_ID = '0x{hex(settings.WHITECHAIN_CHAIN_ID)[2:]}'; // Convert to hex

            async function connectWallet() {{
                if (typeof window.ethereum === 'undefined') {{
                    alert('Please install MetaMask to make payments!');
                    window.open('https://metamask.io/download/', '_blank');
                    return;
                }}

                try {{
                    // Request account access
                    const accounts = await window.ethereum.request({{
                        method: 'eth_requestAccounts'
                    }});

                    const userAddress = accounts[0];

                    // Switch to Whitechain
                    try {{
                        await window.ethereum.request({{
                            method: 'wallet_switchEthereumChain',
                            params: [{{ chainId: CHAIN_ID }}]
                        }});
                    }} catch (switchError) {{
                        // Chain not added, add it
                        if (switchError.code === 4902) {{
                            await window.ethereum.request({{
                                method: 'wallet_addEthereumChain',
                                params: [{{
                                    chainId: CHAIN_ID,
                                    chainName: 'Whitechain Sepolia Testnet',
                                    nativeCurrency: {{
                                        name: 'WBT',
                                        symbol: 'WBT',
                                        decimals: 18
                                    }},
                                    rpcUrls: ['https://rpc.testnet.whitechain.io'],
                                    blockExplorerUrls: ['https://explorer.testnet.whitechain.io']
                                }}]
                            }});
                        }} else {{
                            throw switchError;
                        }}
                    }}

                    // Send USDT transaction
                    const amountInWei = (parseFloat(AMOUNT) * 1e6).toString(16); // USDT has 6 decimals

                    // ERC20 transfer function signature
                    const transferData = '0xa9059cbb' +
                        MERCHANT_WALLET.slice(2).padStart(64, '0') +
                        amountInWei.padStart(64, '0');

                    showStatus('Waiting for transaction approval...', 'checking');

                    const txHash = await window.ethereum.request({{
                        method: 'eth_sendTransaction',
                        params: [{{
                            from: userAddress,
                            to: USDT_ADDRESS,
                            data: transferData
                        }}]
                    }});

                    showStatus('Transaction submitted! Waiting for confirmation...', 'checking');

                    // Wait for transaction confirmation
                    await waitForTransaction(txHash);

                    showStatus('✅ Payment confirmed! Thank you!', 'confirmed');

                    setTimeout(() => {{
                        window.location.reload();
                    }}, 3000);

                }} catch (error) {{
                    console.error(error);
                    alert('Payment failed: ' + error.message);
                }}
            }}

            async function waitForTransaction(txHash) {{
                return new Promise((resolve) => {{
                    const interval = setInterval(async () => {{
                        try {{
                            const receipt = await window.ethereum.request({{
                                method: 'eth_getTransactionReceipt',
                                params: [txHash]
                            }});

                            if (receipt && receipt.status === '0x1') {{
                                clearInterval(interval);
                                resolve(receipt);
                            }}
                        }} catch (error) {{
                            console.error('Error checking transaction:', error);
                        }}
                    }}, 2000);
                }});
            }}

            function showStatus(message, type) {{
                const statusEl = document.getElementById('status');
                statusEl.textContent = message;
                statusEl.className = 'status-' + type;
                statusEl.style.display = 'block';
            }}

            function copyAddress() {{
                const address = document.getElementById('walletAddress').textContent;
                navigator.clipboard.writeText(address);

                const btn = event.target;
                const originalText = btn.textContent;
                btn.textContent = '✅ Copied!';

                setTimeout(() => {{
                    btn.textContent = originalText;
                }}, 2000);
            }}
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)
