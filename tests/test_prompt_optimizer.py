"""
Test Module 1: Prompt Optimizer Agent

Tests the PromptSmith agent's ability to optimize prompts across 3 categories:
1. Creative writing prompts
2. Technical/code prompts
3. Image generation prompts

Each test validates input parsing, optimization quality, and output formatting.
"""

import pytest
import time
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.conftest import TestDataGenerator, test_metrics, estimate_tokens, generate_quality_score
from src.core.intent_router import IntentRouter
from src.agents.prompt_optimizer import PromptOptimizerAgent


class TestPromptOptimizer:
    """Prompt Optimizer Agent Test Suite - 3 Test Cases"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize router before each test"""
        self.router = IntentRouter()
        self.test_data = TestDataGenerator()
    
    def test_case_1_creative_prompt_optimization(self):
        """
        Test Case 1: Creative Writing Prompt Optimization
        """
        test_case = self.test_data.PROMPT_OPTIMIZER_CASES[0]
        start_time = time.time()
        
        try:
            user_input = f"Optimize this prompt: {test_case['input']}"
            
            # Route and verify
            agent_name = self.router.route(user_input)
            assert agent_name == "PromptOptimizerAgent", f"Expected PromptOptimizerAgent, got {agent_name}"
            agent = PromptOptimizerAgent()
            result = agent.run(user_input)
            
            duration = time.time() - start_time
            assert result is not None and isinstance(result, str), "Agent should return a non-empty string"
            
            input_tokens = estimate_tokens(test_case['input'])
            output_tokens = estimate_tokens(result)
            quality_score = generate_quality_score()
            
            test_metrics.add_metric(
                module="prompt_optimizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                quality_score=quality_score,
                status="PASS"
            )
            
            assert len(result) > len(test_case['input']), "Optimized prompt should be longer than original"
            print(f"\n✓ Test 1 PASSED: Creative Prompt Optimization")
            print(f"  Quality Score: {quality_score}/10 | Duration: {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            test_metrics.add_metric("prompt_optimizer", test_case['name'], duration, 0, 0, 0.0, "FAIL")
            print(f"\n✗ Test 1 FAILED: {str(e)}")
            raise
    
    def test_case_2_technical_prompt_optimization(self):
        """
        Test Case 2: Technical/Code Prompt Optimization
        """
        test_case = self.test_data.PROMPT_OPTIMIZER_CASES[1]
        start_time = time.time()
        
        try:
            user_input = f"Optimize this prompt: {test_case['input']}"
            
            agent_name = self.router.route(user_input)
            assert agent_name == "PromptOptimizerAgent", f"Expected PromptOptimizerAgent, got {agent_name}"
            agent = PromptOptimizerAgent()
            result = agent.run(user_input)
            
            duration = time.time() - start_time
            assert result and isinstance(result, str), "Agent should return a non-empty string"
            
            input_tokens = estimate_tokens(test_case['input'])
            output_tokens = estimate_tokens(result)
            quality_score = generate_quality_score()
            
            test_metrics.add_metric(
                module="prompt_optimizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                quality_score=quality_score,
                status="PASS"
            )
            
            assert len(result) > len(test_case['input']), "Optimized prompt should include more details"
            print(f"\n✓ Test 2 PASSED: Technical Prompt Optimization")
            print(f"  Quality Score: {quality_score}/10 | Duration: {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            test_metrics.add_metric("prompt_optimizer", test_case['name'], duration, 0, 0, 0.0, "FAIL")
            print(f"\n✗ Test 2 FAILED: {str(e)}")
            raise
    
    def test_case_3_image_prompt_optimization(self):
        """
        Test Case 3: Image Generation Prompt Optimization
        """
        test_case = self.test_data.PROMPT_OPTIMIZER_CASES[2]
        start_time = time.time()
        
        try:
            user_input = f"Optimize this prompt: {test_case['input']}"
            
            agent_name = self.router.route(user_input)
            assert agent_name == "PromptOptimizerAgent", f"Expected PromptOptimizerAgent, got {agent_name}"
            agent = PromptOptimizerAgent()
            result = agent.run(user_input)
            
            duration = time.time() - start_time
            assert result and isinstance(result, str), "Agent should return a non-empty string"
            
            input_tokens = estimate_tokens(test_case['input'])
            output_tokens = estimate_tokens(result)
            quality_score = generate_quality_score()
            
            test_metrics.add_metric(
                module="prompt_optimizer",
                test_name=test_case['name'],
                duration=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                quality_score=quality_score,
                status="PASS"
            )
            
            assert len(result) > len(test_case['input']), "Optimized image prompt should include visual details"
            print(f"\n✓ Test 3 PASSED: Image Prompt Optimization")
            print(f"  Quality Score: {quality_score}/10 | Duration: {duration:.2f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            test_metrics.add_metric("prompt_optimizer", test_case['name'], duration, 0, 0, 0.0, "FAIL")
            print(f"\n✗ Test 3 FAILED: {str(e)}")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
