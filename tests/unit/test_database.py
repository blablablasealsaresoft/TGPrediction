"""
Tests for database module
"""

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_database_init(mock_database):
    """Test database initialization"""
    # Database should be initialized in fixture
    assert mock_database is not None


@pytest.mark.asyncio
async def test_add_trade(mock_database):
    """Test adding a trade"""
    trade_data = {
        'user_id': 123,
        'signature': 'test_sig_123',
        'trade_type': 'buy',
        'token_mint': 'test_token',
        'token_symbol': 'TST',
        'amount_sol': 0.5,
        'amount_tokens': 100.0,
        'price': 0.005,
        'slippage': 0.5,
        'price_impact': 0.1,
        'success': True
    }
    
    trade = await mock_database.add_trade(trade_data)
    
    assert trade.id is not None
    assert trade.user_id == 123
    assert trade.trade_type == 'buy'
    assert trade.token_mint == 'test_token'


@pytest.mark.asyncio
async def test_get_user_trades(mock_database):
    """Test retrieving user trades"""
    # Add some trades
    for i in range(5):
        await mock_database.add_trade({
            'user_id': 123,
            'signature': f'sig_{i}',
            'trade_type': 'buy',
            'token_mint': 'test_token',
            'token_symbol': 'TST',
            'amount_sol': 0.5,
            'amount_tokens': 100.0,
            'price': 0.005,
            'slippage': 0.5,
            'price_impact': 0.1,
            'success': True
        })
    
    trades = await mock_database.get_user_trades(user_id=123, limit=10)
    
    assert len(trades) == 5
    assert trades[0].user_id == 123


@pytest.mark.asyncio
async def test_get_user_stats(mock_database):
    """Test getting user statistics"""
    # Add profitable and losing trades
    await mock_database.add_trade({
        'user_id': 123,
        'signature': 'profitable_1',
        'trade_type': 'sell',
        'token_mint': 'test',
        'token_symbol': 'TST',
        'amount_sol': 1.0,
        'amount_tokens': 100,
        'price': 0.01,
        'slippage': 0.5,
        'price_impact': 0.1,
        'success': True,
        'pnl_sol': 0.5
    })
    
    await mock_database.add_trade({
        'user_id': 123,
        'signature': 'losing_1',
        'trade_type': 'sell',
        'token_mint': 'test',
        'token_symbol': 'TST',
        'amount_sol': 0.3,
        'amount_tokens': 100,
        'price': 0.003,
        'slippage': 0.5,
        'price_impact': 0.1,
        'success': True,
        'pnl_sol': -0.2
    })
    
    stats = await mock_database.get_user_stats(user_id=123, days=30)
    
    assert stats['total_trades'] == 2
    assert stats['profitable_trades'] == 1
    assert stats['win_rate'] == 50.0
    assert stats['total_pnl'] == 0.3

