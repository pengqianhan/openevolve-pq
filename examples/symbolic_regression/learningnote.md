# scripts.sh 脚本讲解文档

## 概述

`scripts.sh` 是一个用于批量运行符号回归实验的 Bash 脚本。它能够自动化地对多个科学领域的问题集进行 OpenEvolve 演化实验，支持并行执行和错误处理。

## 脚本结构

### 1. 问题集配置

#### 问题数量配置（第 4-9 行）
```bash
declare -A split_counts=(
    ["bio_pop_growth"]=24
    ["chem_react"]=36
    ["matsci"]=25
    ["phys_osc"]=44
)
```

定义了一个关联数组，存储每个问题集（split）包含的问题数量：
- **bio_pop_growth**: 生物种群增长，24个问题
- **chem_react**: 化学反应动力学，36个问题
- **matsci**: 材料科学，25个问题
- **phys_osc**: 物理振荡，44个问题

#### 目录前缀配置（第 11-16 行）
```bash
declare -A split_problem_dir_prefixes=(
    ["bio_pop_growth"]="BPG"
    ["chem_react"]="CRK"
    ["matsci"]="MatSci"
    ["phys_osc"]="PO"
)
```

定义了每个问题集对应的目录前缀，用于构建问题目录路径：
- BPG (Bio Population Growth)
- CRK (Chemical Reaction Kinetics)
- MatSci (Materials Science)
- PO (Physics Oscillation)

### 2. 主循环逻辑

#### 遍历问题集（第 22-75 行）

```bash
for split_name in "${!split_counts[@]}"; do
    count=${split_counts[$split_name]}
    problem_dir_prefix=${split_problem_dir_prefixes[$split_name]}
    # ...
done
```

外层循环遍历每个问题集，获取：
- `split_name`: 问题集名称
- `count`: 该问题集的问题数量
- `problem_dir_prefix`: 该问题集的目录前缀

#### 前缀验证（第 26-34 行）

对目录前缀进行验证检查：
- 如果前缀未定义，输出警告并跳过该问题集
- 支持空字符串前缀（某些问题集可能不需要前缀）

#### 遍历单个问题（第 44-73 行）

```bash
for (( i=0; i<count; i++ )); do
    problem_dir="$base_problems_dir/$split_name/$problem_dir_prefix$i"
    # ...
done
```

内层循环遍历单个问题集中的每个问题（ID 从 0 到 count-1）。

### 3. 文件路径构建

对于每个问题，脚本会构建三个关键文件的路径：

```bash
initial_program_path="$problem_dir/initial_program.py"
evaluator_path="$problem_dir/evaluator.py"
config_path="$problem_dir/config.yaml"
```

**示例路径结构**：
```
./problems/chem_react/CRK0/
├── initial_program.py
├── evaluator.py
└── config.yaml
```

### 4. 文件存在性检查（第 54-67 行）

在启动实验前，脚本会验证必需文件是否存在：

```bash
if [[ ! -f "$initial_program_path" ]]; then
    echo "  [Problem $i] SKIPPING: Initial program not found at $initial_program_path"
    continue
fi
```

如果任何必需文件缺失，会：
- 输出警告信息
- 跳过该问题
- 继续处理下一个问题

### 5. 实验启动（第 69-73 行）

```bash
cmd="python ../../openevolve-run.py \"$initial_program_path\" \"$evaluator_path\" --config \"$config_path\" --iterations 200"
eval $cmd &
```

构建并执行 OpenEvolve 命令：
- 使用相对路径调用 `openevolve-run.py`
- 传递初始程序、评估器和配置文件路径
- 设置迭代次数为 200
- `&` 符号将进程放到后台运行，实现并行执行

### 6. 进程管理

#### 分批等待（第 74 行）
```bash
wait    # let's do split by split
```

在每个问题集的所有问题启动后，`wait` 命令会等待该问题集的所有后台进程完成，再继续下一个问题集。这种"分批次"的策略可以：
- 避免同时启动过多进程导致系统资源耗尽
- 便于按问题集组织和监控实验进度

#### 最终等待（第 80 行）
```bash
wait
```

在所有问题集处理完成后，再次调用 `wait` 确保所有后台进程都已完成。

## 执行流程示意

```
开始
 │
 ├─ bio_pop_growth (24个问题)
 │   ├─ BPG0 → 启动实验（后台）
 │   ├─ BPG1 → 启动实验（后台）
 │   ├─ ...
 │   ├─ BPG23 → 启动实验（后台）
 │   └─ wait (等待所有24个实验完成)
 │
 ├─ chem_react (36个问题)
 │   ├─ CRK0 → 启动实验（后台）
 │   ├─ CRK1 → 启动实验（后台）
 │   ├─ ...
 │   ├─ CRK35 → 启动实验（后台）
 │   └─ wait (等待所有36个实验完成)
 │
 ├─ matsci (25个问题)
 │   └─ ... (同上)
 │
 ├─ phys_osc (44个问题)
 │   └─ ... (同上)
 │
 └─ 所有实验完成
```

## 使用方法

### 前置条件

1. 确保所有问题目录结构正确：
   ```
   ./problems/
   ├── bio_pop_growth/
   │   ├── BPG0/
   │   │   ├── initial_program.py
   │   │   ├── evaluator.py
   │   │   └── config.yaml
   │   ├── BPG1/
   │   └── ...
   ├── chem_react/
   │   ├── CRK0/
   │   └── ...
   └── ...
   ```

2. 确保 `openevolve-run.py` 在正确的相对路径位置

### 执行脚本

```bash
cd examples/symbolic_regression
chmod +x scripts.sh
./scripts.sh
```

### 输出示例

```
Starting all experiments...

----------------------------------------------------
Processing Split: chem_react
Number of problems: 36
Problem directory prefix: 'CRK'
Expected problem path structure: ./problems/chem_react/CRK[ID]/
----------------------------------------------------
  Launching chem_react - Problem 0 (./problems/chem_react/CRK0/initial_program.py)
  Launching chem_react - Problem 1 (./problems/chem_react/CRK1/initial_program.py)
  ...
```

## 关键特性

### 1. 并行执行
- 同一问题集内的所有问题并行运行
- 通过后台进程（`&`）实现并发

### 2. 错误容忍
- 缺失文件不会中断整个流程
- 只跳过有问题的单个实验

### 3. 进度监控
- 清晰的输出信息显示当前处理的问题集和问题
- 分阶段的等待策略便于监控

### 4. 灵活配置
- 通过修改数组可以轻松添加/删除问题集
- 每个问题使用独立的配置文件

## 注意事项

1. **资源管理**: 同时运行大量实验可能消耗大量 CPU/内存，建议根据系统资源调整并发数量
2. **迭代次数**: 当前硬编码为 200 次迭代，可根据需要修改第 71 行
3. **相对路径**: 脚本假设从 `examples/symbolic_regression/` 目录执行
4. **日志管理**: 每个实验的输出会混在一起，考虑重定向到独立日志文件

## 可能的改进方向

1. **添加日志重定向**:
   ```bash
   eval $cmd > "$problem_dir/experiment.log" 2>&1 &
   ```

2. **限制并发数量**:
   使用信号量或 GNU Parallel 控制同时运行的实验数量

3. **参数化迭代次数**:
   通过命令行参数或配置文件指定迭代次数

4. **进度条显示**:
   使用 `tqdm` 或类似工具显示整体进度

5. **失败重试机制**:
   记录失败的实验并支持自动重试
