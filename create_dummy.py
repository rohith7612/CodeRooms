import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'coderooms.settings')
django.setup()

from core.models import Problem

if not Problem.objects.filter(title="Two Sum").exists():
    Problem.objects.create(
        title="Two Sum",
        description="Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
        difficulty="Easy",
        topic="Arrays",
        initial_code="class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        # Write your code here\n        pass",
        test_cases=[
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"},
            {"input": "nums = [3,3], target = 6", "output": "[0,1]"}
        ]
    )
    print("Created Two Sum problem")
else:
    print("Two Sum already exists")
