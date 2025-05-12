from ..Controller.ActivationGeneratorModel import ActivationGenerator
from ..Automation.RuleModel import Rule
from ..Automation.RuleConditionModel import Condition, ThresholdCondition

class ConditionRegistry: # registry pattern
    _registry = {}

    @classmethod
    def register(cls, condition_Type: str):
        def decorator(factory):
            cls._registry[condition_Type] = factory
            return factory
        return decorator

    @classmethod
    def create(cls, Cond: dict) -> Condition:
        condition_Type = Cond.get("Type")
        factory = cls._registry.get(condition_Type)
        if not factory:
            raise ValueError(f"No command registered for type '{condition_Type}'")
        return factory(Cond)

@ConditionRegistry.register("SetThreshold") # this line return a decorator and call it with the bellow function as argument
def create_ThresHold_Condition(Cond):
    return ThresholdCondition(Cond["Description"])



class RuleGenerator:
    _instance = None
    def __new__(cls, *args, **kwargs): # singleton pattern
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.ActGen = ActivationGenerator()
        return cls._instance

    def generate(self, DeviceInfo, RuleDescription: dict) -> [Rule]:
        Rules = []
        for rule_name, rule_content in RuleDescription.get("Body", {}).items():
            rule = Rule(ConditionRegistry.create(rule_content["Condition"]), self.ActGen.generate(DeviceInfo, rule_content["Action"]))
            Rules.append(rule)

        return Rules


