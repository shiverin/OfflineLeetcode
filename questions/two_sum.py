# Two Sum
# Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to target.

from typing import List

class Solution:
    def twoSum(self, nums, target):
        # Write your code here
        d={}
        n=0
        for i in nums:
            if not target-i in d:
                d[i]=n
            else:
                return [d[target-i],n]
            n+=1
        return 0
