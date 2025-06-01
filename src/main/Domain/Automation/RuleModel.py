from..Controller.CommandModel import ActivationCommand
from..Automation.RuleConditionModel import Condition
import asyncio


class Rule:
    def __init__(self, cond: Condition, action: {ActivationCommand}):
        self.cond = cond
        self.action = action

    async def apply(self, SensorData: dict):
        if self.cond.evaluate(SensorData):
            self.action['action'].run()
            await asyncio.sleep(5)
            self.action['inverseAction'].run()


