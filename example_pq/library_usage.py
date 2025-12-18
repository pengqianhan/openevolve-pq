import os
from openevolve import run_evolution, evolve_function
from openevolve.config import Config, LLMModelConfig

# 配置使用本地 LLM
api_key = os.getenv('HASEL_API_KEY')
config = Config()
config.llm.api_base = "https://lm.deepnetdiscovery.net/v1"
config.llm.api_key = api_key
config.llm.models = [
    LLMModelConfig(
        name="qwen3-coder",
        api_base="https://lm.deepnetdiscovery.net/v1",
        api_key=api_key,
        weight=1.0
    )
]

# 简单的评估函数
def simple_evaluator(program_path):
    """简单评估器：测试排序函数是否正确"""
    try:
        # 读取并执行程序
        with open(program_path, 'r') as f:
            code = f.read()
        
        # 创建本地命名空间执行代码
        local_ns = {}
        exec(code, local_ns)
        
        # 测试用例
        test_cases = [
            ([3, 1, 2], [1, 2, 3]),
            ([5, 2, 8, 1], [1, 2, 5, 8]),
            ([1], [1]),
            ([], []),
        ]
        
        # 查找排序函数
        sort_func = None
        for name, obj in local_ns.items():
            if callable(obj) and 'sort' in name.lower():
                sort_func = obj
                break
        
        if sort_func is None:
            return {"score": 0.0, "error": "No sort function found"}
        
        # 运行测试
        passed = 0
        for input_arr, expected in test_cases:
            try:
                result = sort_func(input_arr.copy())
                if result == expected:
                    passed += 1
            except Exception:
                pass
        
        score = passed / len(test_cases)
        return {"score": score, "passed": passed, "total": len(test_cases)}
    
    except Exception as e:
        return {"score": 0.0, "error": str(e)}


# Evolve Python functions directly
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j] 
    return arr

# 使用本地 LLM 进行函数进化
result = evolve_function(
    bubble_sort,
    test_cases=[([3,1,2], [1,2,3]), ([5,2,8], [2,5,8])],
    iterations=5,  # 减少迭代次数用于测试
    config=config
)
print(f"Evolved sorting algorithm: {result.best_code}")