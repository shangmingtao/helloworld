# AI问题排查系统

## 系统架构

AI问题排查系统是一个基于多Agent协作的技术问题排查辅助工具，通过协调者Agent编排排查流程，调用5个专业子Agent完成问题定位和解决。

## 目录结构

```
ai-detetive/
├── __init__.py                      # 包初始化文件
├── coordinator_agent.py              # 协调者Agent
├── db_agent.py                      # 数据库查询Agent
├── dld_agent.py                     # 业务流程Agent
├── log_agent.py                     # 日志查询Agent
├── prd_agent.py                     # 产品需求Agent
├── code_agent.py                    # 代码查询Agent
├── example.py                       # 使用示例
├── README.md                        # 项目文档
└── prompts/                         # 提示词文件夹
    ├── __init__.py                  # 提示词加载模块
    ├── coordinator_agent_prompt.txt # 协调者Agent提示词
    ├── db_agent_prompt.txt          # 数据库Agent提示词
    ├── dld_agent_prompt.txt         # 业务流程Agent提示词
    ├── log_agent_prompt.txt         # 日志Agent提示词
    ├── prd_agent_prompt.txt         # 产品需求Agent提示词
    └── code_agent_prompt.txt        # 代码Agent提示词
```

## 提示词管理

所有Agent的提示词（system_prompt）都集中存储在 `prompts/` 文件夹中，每个Agent对应一个独立的 `.txt` 文件：

- `coordinator_agent_prompt.txt`: 协调者Agent的提示词
- `db_agent_prompt.txt`: 数据库Agent的提示词
- `dld_agent_prompt.txt`: 业务流程Agent的提示词
- `log_agent_prompt.txt`: 日志Agent的提示词
- `prd_agent_prompt.txt`: 产品需求Agent的提示词
- `code_agent_prompt.txt`: 代码Agent的提示词

### 加载提示词

提示词通过 `prompts/__init__.py` 模块中的函数加载：

```python
from prompts import (
    get_code_agent_prompt,
    get_coordinator_agent_prompt,
    get_db_agent_prompt,
    get_dld_agent_prompt,
    get_log_agent_prompt,
    get_prd_agent_prompt
)

# 加载特定的提示词
prompt = get_code_agent_prompt()
```

### 修改提示词

如需修改某个Agent的提示词，只需编辑 `prompts/` 文件夹中对应的 `.txt` 文件，无需修改Python代码。修改后系统会自动加载最新的提示词内容。

### 架构组件

#### 1. 协调者Agent (CoordinatorAgent)
- **职责**：问题排查流程自主编排、结果回归验证、置信度评估、循环次数控制
- **功能**：
  - 理解问题描述，设计排查方案
  - 协调各个子Agent收集信息
  - 综合分析结果，识别问题根因
  - 评估排查结果置信度
  - 控制排查迭代次数（默认3轮）

#### 2. 数据库Agent (DatabaseAgent)
- **职责**：查询数据库对象状态、详细内容或分析数据问题
- **功能**：
  - 查询对象状态（表、索引、存储过程等）
  - 查询对象详细内容（结构、数据）
  - 分析数据相关问题
- **访问方式**：通过将MySQL数据库内容向量化后访问

#### 3. 业务流程Agent (BusinessLogicAgent)
- **职责**：查询业务流程的实现路径和逻辑
- **功能**：
  - 获取业务流程的完整路径
  - 分析业务流程中的关键步骤和决策点
  - 识别异常处理逻辑
- **输出示例**：先查询数据库 → 进行数据比对 → 删除数据 → 给用户返回成功；删除数据失败 → 给用户返回失败

#### 4. 日志Agent (LogAgent)
- **职责**：查询关联日志
- **功能**：
  - 通过traceId查询完整调用链日志
  - 通过错误日志调用栈分析关联日志
  - 通过时间范围查询日志
  - 分析日志中的异常模式
- **访问方式**：通过将MySQL数据库内容向量化后访问

#### 5. 产品需求Agent (PRDAgent)
- **职责**：查询业务流程的业务逻辑和规则
- **功能**：
  - 查询业务逻辑和规则
  - 解释业务规则的应用场景
  - 分析业务场景的预期行为
  - 对比需求和实现的差异

#### 6. 代码Agent (CodeAgent)
- **职责**：查询业务对应的代码片段或根据错误日志查询相关代码
- **功能**：
  - 查询业务对应的代码实现
  - 根据错误日志定位相关代码
  - 分析代码逻辑和数据流
  - 按模式搜索代码
- **访问方式**：通过SSH从代码库拉取（账号密码待配置）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 1. 配置DeepSeek API密钥

在使用前，需要配置DeepSeek API密钥：

```python
API_KEY = "your-api-key"
BASE_URL = "https://api.deepseek.com/v1"
```

### 2. 配置代码库SSH连接（可选）

如果需要使用代码Agent查询代码，需要配置SSH连接信息：

```python
code_agent = CodeAgent(
    api_key=API_KEY,
    base_url=BASE_URL,
    ssh_host="your-ssh-host",
    ssh_user="your-ssh-user",
    ssh_password="your-ssh-password",
    code_repo_path="/path/to/repo"
)
```

## 使用方法

### 方法1：使用协调者Agent进行完整排查

```python
from coordinator_agent import CoordinatorAgent

# 初始化协调者Agent
coordinator = CoordinatorAgent(
    api_key="your-api-key",
    base_url="https://api.deepseek.com/v1"
)

# 执行问题排查
result = coordinator.investigate(
    problem_description="用户表查询速度很慢，响应时间超过5秒",
    max_rounds=3
)

# 查看结果
print(f"置信度: {result['confidence']}")
print(f"结论: {result['conclusion']}")
```

### 方法2：直接调用各个子Agent

```python
from db_agent import DatabaseAgent
from log_agent import LogAgent
from prd_agent import PRDAgent

# 初始化Agent
db_agent = DatabaseAgent(api_key, base_url)
log_agent = LogAgent(api_key, base_url)
prd_agent = PRDAgent(api_key, base_url)

# 查询数据库对象状态
result = db_agent.query_object_status(
    object_name="user_table",
    object_type="table"
)

# 通过traceId查询日志
result = log_agent.query_logs_by_trace_id(trace_id="abc123")

# 查询业务逻辑
result = prd_agent.query_business_logic(business_name="订单创建")
```

### 方法3：运行示例程序

```bash
cd ai-detetive
python example.py
```

## 工具使用说明

### 协调者Agent的5个Tools

1. **db_collector**: 数据库查询工具
   - 查询数据库对象状态、详细内容
   - 分析数据问题

2. **dld_collector**: 业务流程查询工具
   - 查询业务流程路径
   - 分析流程问题和关键步骤

3. **log_collector**: 日志查询工具
   - 通过traceId查询关联日志
   - 通过错误调用栈查询日志
   - 通过时间范围查询日志

4. **prd_collector**: 产品需求查询工具
   - 查询业务逻辑和规则
   - 分析业务场景

5. **code_collector**: 代码查询工具
   - 查询业务对应的代码
   - 根据错误日志定位代码

## 排查流程

1. **问题理解阶段**：分析问题描述，识别关键信息
2. **排查规划阶段**：设计排查步骤，选择合适的工具
3. **信息收集阶段**：调用各个工具收集信息
4. **结果分析阶段**：综合分析信息，识别问题根因
5. **验证确认阶段**：验证分析结果
6. **结果输出阶段**：给出结论和解决方案

## 输出说明

排查结果包含以下信息：
- `status`: 执行状态（success/error）
- `rounds_completed`: 完成的排查轮数
- `confidence`: 置信度评分（0-100）
- `findings`: 各轮排查的详细结果
- `actions_taken`: 已执行的操作记录
- `conclusion`: 最终结论

## 注意事项

1. **API密钥安全**：请妥善保管DeepSeek API密钥，不要泄露
2. **数据库访问**：db_agent和log_agent需要将数据库内容向量化，需要额外配置
3. **SSH连接**：code_agent的SSH连接需要配置正确的账号密码
4. **循环控制**：默认最大排查轮数为3轮，可根据需要调整
5. **日志记录**：系统会记录详细的执行日志，便于问题追溯

## 后续优化方向

1. 实现数据库向量化存储和查询
2. 完善SSH代码拉取功能
3. 添加更多的验证和确认机制
4. 优化提示词，提高排查准确性
5. 添加可视化的排查过程展示
6. 支持多轮对话和交互式排查
