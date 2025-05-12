from..Controller.CommandModel import ActivationCommand
from..Automation.RuleConditionModel import Condition


class Rule:
    def __init__(self, cond: Condition, action: ActivationCommand):
        self.cond = cond
        self.action = action

    def apply(self, SensorData: dict):
        if self.cond.evaluate(SensorData):
            self.action.run()

