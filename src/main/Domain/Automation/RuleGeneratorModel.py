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

    def generate(self, DeviceInfo, mqtt_manager, RuleDescription: dict) -> [Rule]:
        Rules = []
        for rule_name, rule_content in RuleDescription.get("Body", {}).items():
            action = {"action": self.ActGen.generate(DeviceInfo, mqtt_manager, rule_content["Action"]), "inverseAction": self.ActGen.generate(DeviceInfo, mqtt_manager, self.inverse_action(rule_content["Action"]))}
            rule = Rule(ConditionRegistry.create(rule_content["Condition"]), action)
            Rules.append(rule)

        return Rules

    def inverse_action(self, activation_json: dict):
        # Clone the original to avoid modifying in-place
        new_json = {
            "Header": activation_json["Header"].copy(),
            "Body": {
                "CommandType": activation_json["Body"]["CommandType"],
                "Parameter": {}
            }
        }

        for key, value in activation_json["Body"]["Parameter"].items():
            # Inverse value: 1 -> 0, 0 -> 1
            if isinstance(value, (int, float)) and value in [0, 1]:
                new_json["Body"]["Parameter"][key] = 1 - value
            else:
                raise ValueError(f"Unsupported value '{value}' for inversion. Must be 0 or 1.")
        return new_json


