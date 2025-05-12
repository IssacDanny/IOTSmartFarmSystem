import asyncio, json
from .RuleGeneratorModel import RuleGenerator
from Infrastructure import ProcedureCall


class Automizer:
    def __init__(self, DeviceInfo, AutomationRule):
        self.DeviceInfo = DeviceInfo
        self.ruleGen = RuleGenerator()
        self.ruleSet = self.ruleGen.generate(DeviceInfo, AutomationRule)
        self.lock = asyncio.Lock()
        self.running = False

    async def AddRule(self, RuleDescription: dict):
        rules = self.ruleGen.generate(self.DeviceInfo, RuleDescription)
        ProcedureCall.AddAutomationRule(self.DeviceInfo, RuleDescription)
        async with self.lock:
            self.ruleSet.extend(rules)

    async def UpdateRuleSet(self, RuleDescription: dict):
        rules = self.ruleGen.generate(self.DeviceInfo, RuleDescription)
        ProcedureCall.UpdataAutomationRule(self.DeviceInfo, RuleDescription)
        async with self.lock:
            self.ruleSet = rules

    async def EnforceRule(self):
        self.running = True
        BATCH_SIZE = 10
        while self.running:
            # Take a snapshot of the current rules
            async with self.lock:
                rule_snapshot = list(self.ruleSet)

            # Fetch sensor data
            sensor_data = self.fetch_sensor_data()
            if not sensor_data:
                await asyncio.sleep(1)
                continue

            # Apply rules
            for i in range(0, len(rule_snapshot), BATCH_SIZE):
                batch = rule_snapshot[i:i + BATCH_SIZE]
                for rule in batch:
                    rule.apply(sensor_data)

                await asyncio.sleep(1)

    async def StopEnforcing(self):
        self.running = False

    def fetch_sensor_data(self):
        result = ProcedureCall.RetrieveLatestSensorData(self.DeviceInfo)
        if result:
            last_entry = result[-1]
            return json.loads(last_entry.get('data_payload', '{}'))  # safe access
        return {}
