"""
🧠 ENHANCED NEURAL ENGINE - PREDICTION LAYER
Transforms unified scores into probability predictions with actionable recommendations

Integrates seamlessly with existing UnifiedNeuralEngine
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ConfidenceLevel(Enum):
    """Prediction confidence tiers"""
    ULTRA = "ULTRA"      # 90-100% - Auto-trade for Gold+ tiers
    HIGH = "HIGH"        # 80-89%  - Strong signal
    MEDIUM = "MEDIUM"    # 65-79%  - Conditional
    LOW = "LOW"          # <65%    - Avoid


class Direction(Enum):
    """Price direction prediction"""
    UP = "UP"
    DOWN = "DOWN"
    NEUTRAL = "NEUTRAL"


@dataclass
class EnhancedPrediction:
    """Complete prediction with probabilities and recommendations"""
    token_address: str
    unified_score: float
    safety_score: int
    direction: Direction
    confidence_score: float
    confidence_level: ConfidenceLevel
    timeframe_hours: int
    suggested_action: str
    position_size_sol: Optional[float]
    take_profit_target: Optional[float]
    stop_loss: Optional[float]
    ai_ml_score: float
    sentiment_score: float
    wallet_score: float
    community_score: float
    reasoning: List[str]
    contributing_factors: Dict[str, float]
    signals_used: int
    timestamp: datetime


class PredictionLayer:
    """
    Enhancement layer for UnifiedNeuralEngine
    Converts unified scores into actionable probability predictions
    """
    
    def __init__(self, neural_engine):
        """
        Args:
            neural_engine: UnifiedNeuralEngine instance
        """
        self.neural_engine = neural_engine
        self.predictions = []
        self.outcomes = []
        
        logger.info("🎯 Prediction Layer initialized")
    
    async def enhanced_analysis(
        self,
        token_address: str,
        ai_analysis: Dict,
        sentiment_data: Optional[Dict],
        community_signal: Optional[Dict],
        wallet_signals: List[Dict],
        safety_score: int,
        user_tier: Optional[str] = None
    ) -> EnhancedPrediction:
        """
        Create enhanced prediction with probabilities
        
        Args:
            token_address: Token to analyze
            ai_analysis: Standard AI analysis from AIStrategyManager
            sentiment_data: Sentiment from ActiveSentimentScanner
            community_signal: Community ratings
            wallet_signals: Signals from 441 elite wallets
            safety_score: 6-layer protection score
            user_tier: User's tier for position sizing
        """
        
        # Get unified neural analysis
        neural_result = await self.neural_engine.analyze_with_full_intelligence(
            token_address=token_address,
            ai_prediction=ai_analysis,
            sentiment_data=sentiment_data,
            community_signal=community_signal,
            wallet_signals=wallet_signals,
            market_context={}
        )
        
        # Extract component scores
        component_scores = neural_result.get('component_scores', {})
        ml_score = component_scores.get('ai', 50) / 100
        sentiment_score = component_scores.get('sentiment', 50) / 100
        wallet_score = component_scores.get('wallets', 50) / 100
        community_score = component_scores.get('community', 50) / 100
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            ml_score, sentiment_score, wallet_score,
            community_score, safety_score,
            neural_result.get('signal_alignment', 0)
        )
        
        # Determine direction
        direction = self._determine_direction(
            ml_score, sentiment_score, wallet_score,
            neural_result.get('unified_score', 50) / 100
        )
        
        # Classify confidence level
        confidence_level = self._classify_confidence(confidence)
        
        # Generate recommendations
        action = self._suggest_action(confidence_level, direction, user_tier, safety_score)
        position_size = self._calculate_position_size(confidence, user_tier, safety_score)
        take_profit = self._calculate_take_profit(confidence)
        stop_loss = self._calculate_stop_loss(confidence)
        
        # Build reasoning
        reasoning = self._generate_reasoning(
            ml_score, sentiment_score, wallet_score,
            community_score, safety_score,
            neural_result.get('signal_alignment', 0),
            neural_result
        )
        
        # Create prediction
        prediction = EnhancedPrediction(
            token_address=token_address,
            unified_score=neural_result.get('unified_score', 50),
            safety_score=safety_score,
            direction=direction,
            confidence_score=confidence,
            confidence_level=confidence_level,
            timeframe_hours=6,
            suggested_action=action,
            position_size_sol=position_size,
            take_profit_target=take_profit,
            stop_loss=stop_loss,
            ai_ml_score=ml_score * 100,
            sentiment_score=sentiment_score * 100,
            wallet_score=wallet_score * 100,
            community_score=community_score * 100,
            reasoning=reasoning,
            contributing_factors={
                'ai': ml_score * neural_result.get('learned_weights', {}).get('ai_prediction', 0.25),
                'sentiment': sentiment_score * neural_result.get('learned_weights', {}).get('sentiment_score', 0.25),
                'wallets': wallet_score * neural_result.get('learned_weights', {}).get('wallet_intelligence', 0.25),
                'community': community_score * neural_result.get('learned_weights', {}).get('community_rating', 0.25),
                'safety': safety_score / 100 * 0.2
            },
            signals_used=self._count_signals(sentiment_data, wallet_signals, community_signal),
            timestamp=datetime.utcnow()
        )
        
        self.predictions.append(prediction)
        return prediction
    
    def _calculate_confidence(
        self, ml_score, sentiment_score, wallet_score,
        community_score, safety_score, signal_alignment
    ) -> float:
        """Calculate overall confidence with safety factor"""
        
        # Get learned weights from neural engine
        weights = self.neural_engine.weights
        
        base_confidence = (
            ml_score * weights['ai_prediction'] +
            sentiment_score * weights['sentiment_score'] +
            wallet_score * weights['wallet_intelligence'] +
            community_score * weights['community_rating']
        )
        
        # Safety factor
        safety_factor = safety_score / 100
        base_confidence *= (0.5 + (safety_factor * 0.5))
        
        # Signal alignment bonus
        if signal_alignment >= 3:
            base_confidence *= 1.15
        elif signal_alignment >= 2:
            base_confidence *= 1.10
        
        return min(1.0, base_confidence)
    
    def _determine_direction(self, ml_score, sentiment_score, wallet_score, unified_score) -> Direction:
        """Determine predicted direction - wallet intelligence weighted highest"""
        combined = (
            ml_score * 0.20 +
            sentiment_score * 0.25 +
            wallet_score * 0.40 +  # Smart money most important
            unified_score * 0.15
        )
        
        if combined > 0.6:
            return Direction.UP
        elif combined < 0.4:
            return Direction.DOWN
        return Direction.NEUTRAL
    
    def _classify_confidence(self, score: float) -> ConfidenceLevel:
        """Classify confidence level"""
        if score >= 0.90:
            return ConfidenceLevel.ULTRA
        elif score >= 0.80:
            return ConfidenceLevel.HIGH
        elif score >= 0.65:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
    
    def _suggest_action(self, confidence, direction, user_tier, safety_score) -> str:
        """Generate action recommendation"""
        
        # Safety override
        if safety_score < 60:
            return "⚠️ AVOID - SAFETY CONCERNS"
        
        if confidence == ConfidenceLevel.ULTRA:
            if direction == Direction.UP:
                if user_tier in ['GOLD', 'PLATINUM', 'ELITE']:
                    return "🚀 AUTO-BUY (Ultra Confidence - Gold+ Tier)"
                return "🚀 STRONG BUY (Upgrade to Gold for auto-trade)"
            elif direction == Direction.DOWN:
                return "🚨 AVOID - HIGH CONFIDENCE DUMP"
        
        elif confidence == ConfidenceLevel.HIGH:
            if direction == Direction.UP:
                return "✅ STRONG BUY (Manual Review)"
            elif direction == Direction.DOWN:
                return "⚠️ AVOID"
        
        elif confidence == ConfidenceLevel.MEDIUM:
            if direction == Direction.UP:
                return "⚡ CONDITIONAL BUY (Review Carefully)"
            return "❌ SKIP"
        
        return "➖ NEUTRAL - SKIP"
    
    def _calculate_position_size(self, confidence, user_tier, safety_score) -> Optional[float]:
        """Kelly Criterion position sizing adjusted by tier"""
        
        if confidence < 0.65 or safety_score < 60:
            return None
        
        # Kelly Criterion
        win_prob = confidence
        loss_prob = 1 - win_prob
        kelly_fraction = ((1.5 * win_prob) - loss_prob) / 1.5
        kelly_fraction *= 0.25  # Conservative Kelly
        
        # Tier multipliers
        tier_multipliers = {
            'BRONZE': 0.5,
            'SILVER': 0.75,
            'GOLD': 1.0,
            'PLATINUM': 1.5,
            'ELITE': 2.0
        }
        
        multiplier = tier_multipliers.get(user_tier or 'BRONZE', 0.5)
        max_position = 5.0  # From config
        
        position = max_position * kelly_fraction * multiplier
        position = max(0.1, min(max_position, position))
        
        return round(position, 2)
    
    def _calculate_take_profit(self, confidence: float) -> float:
        """Dynamic take profit targets"""
        if confidence > 0.90:
            return 0.75  # 75%
        elif confidence > 0.80:
            return 0.50  # 50%
        elif confidence > 0.70:
            return 0.35  # 35%
        return 0.25
    
    def _calculate_stop_loss(self, confidence: float) -> float:
        """Dynamic stop loss"""
        if confidence > 0.85:
            return -0.15
        elif confidence > 0.70:
            return -0.12
        return -0.10
    
    def _generate_reasoning(
        self, ml_score, sentiment_score, wallet_score,
        community_score, safety_score, signal_alignment, neural_result
    ) -> List[str]:
        """Generate human-readable reasoning"""
        reasons = []
        
        if sentiment_score > 0.75:
            reasons.append(f"🔥 Strong positive sentiment ({sentiment_score*100:.0f}/100)")
        
        if wallet_score > 0.75:
            reasons.append(f"🐋 Elite wallets buying ({wallet_score*100:.0f}/100)")
        
        if community_score > 0.70:
            reasons.append(f"👥 Community approved ({community_score*100:.0f}/100)")
        
        if safety_score > 80:
            reasons.append(f"✅ Excellent safety ({safety_score}/100)")
        elif safety_score < 60:
            reasons.append(f"🚨 SAFETY CONCERNS ({safety_score}/100)")
        
        if ml_score > 0.70:
            reasons.append(f"🤖 AI confident ({ml_score*100:.0f}/100)")
        
        if signal_alignment >= 3:
            reasons.append(f"⚡ {signal_alignment}/4 signals aligned (+15% boost)")
        
        # System learning status
        if self.neural_engine.total_predictions > 50:
            acc = self.neural_engine.system_accuracy
            reasons.append(f"📊 System accuracy: {acc:.1%} ({self.neural_engine.total_predictions} predictions)")
        
        return reasons
    
    def _count_signals(self, sentiment_data, wallet_signals, community_signal) -> int:
        """Count total signals used"""
        count = 1  # AI always present
        
        if sentiment_data:
            count += 1
        if wallet_signals:
            count += len(wallet_signals)
        if community_signal:
            count += 1
        
        return count
    
    async def track_outcome(self, prediction: EnhancedPrediction, actual_pnl: float):
        """Track prediction outcomes for learning"""
        was_correct = (
            (prediction.direction == Direction.UP and actual_pnl > 0) or
            (prediction.direction == Direction.DOWN and actual_pnl < 0)
        )
        
        outcome = {
            'prediction': prediction,
            'actual_pnl': actual_pnl,
            'was_correct': was_correct,
            'confidence_level': prediction.confidence_level.value,
            'timestamp': datetime.utcnow()
        }
        
        self.outcomes.append(outcome)
        
        # Feed back to neural engine
        await self.neural_engine.learn_from_outcome(
            token_address=prediction.token_address,
            prediction={'unified_score': prediction.unified_score, 'component_scores': {
                'ai': prediction.ai_ml_score,
                'sentiment': prediction.sentiment_score,
                'wallets': prediction.wallet_score,
                'community': prediction.community_score
            }},
            actual_outcome={'profit_pct': (actual_pnl / prediction.position_size_sol * 100) if prediction.position_size_sol else 0}
        )
        
        logger.info(f"🎯 Prediction outcome: {'✅ CORRECT' if was_correct else '❌ WRONG'} | PnL: {actual_pnl:+.4f} SOL")
    
    def get_prediction_stats(self) -> Dict:
        """Get prediction performance stats"""
        if not self.outcomes:
            return {'total': 0, 'accuracy': 0, 'by_confidence': {}}
        
        total = len(self.outcomes)
        correct = sum(1 for o in self.outcomes if o['was_correct'])
        accuracy = correct / total
        
        # By confidence level
        by_confidence = {}
        for level in ConfidenceLevel:
            level_outcomes = [o for o in self.outcomes if o['confidence_level'] == level.value]
            if level_outcomes:
                level_correct = sum(1 for o in level_outcomes if o['was_correct'])
                by_confidence[level.value] = {
                    'total': len(level_outcomes),
                    'accuracy': level_correct / len(level_outcomes)
                }
        
        return {
            'total': total,
            'correct': correct,
            'accuracy': accuracy,
            'by_confidence': by_confidence
        }

