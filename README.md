# CraftBots

CraftBots is a multi-agent simulator to evaluate/benchmark integrated planning and execution in complex tasks.

![Screenshot of Craftbots simulation](screenshot.png)

## Quickstart

Install the dependencies, clone the repository, and run `main.py`
```bash
git clone https://github.com/strathclyde-artificial-intelligence/craft-bots
cd ./craft-bots
pip install -r requirements.txt
python main.py
```

Press "reset" to generate a new simulation, and "start" to begin the simulation. The default agent acts randomly.

### Connect your own agent

Once you have created your own agent open `main.py` and modify the lines which append the default agent to the simulation.
```python
# agent
agent = TestAgent()
sim.agents.append(agent)
```
  
## CraftBots Wiki
Further information is available on the [CraftBots Wiki here](https://github.com/strathclyde-artificial-intelligence/craft-bots/wiki).

## OMPAS Binding: generation of protobuf files:
```bash
python3 -m grpc_tools.protoc -I ../grpc --python_out=. --pyi_out=. --grpc_python_out=. -I. ../grpc/platform_interface.proto
``