import asyncio, json
from .RuleGeneratorModel import RuleGenerator
from Infrastructure import ProcedureCall
from Infrastructure.Logging import write_log
from datetime import datetime


class Automizer:
    def __init__(self, DeviceInfo, mqtt_manager, AutomationRule):
        self.DeviceInfo = DeviceInfo
        self.ruleGen = RuleGenerator()
        self.ruleSet = self.ruleGen.generate(DeviceInfo, mqtt_manager,AutomationRule)
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
                    await rule.apply(sensor_data)

                #await asyncio.sleep(1)

    async def StopEnforcing(self):
        self.running = False

    def fetch_sensor_data(self):
        result = ProcedureCall.RetrieveLatestSensorData(self.DeviceInfo)
        if result:
            last_entry = result[-1]
            timestamp_str = last_entry.get('timestamp')

            if timestamp_str:
                try:
                    # Adjust format to your DB timestamp format
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    now = datetime.now()

                    # Accept only if data is fresh within the last 5 seconds
                    if abs((now - timestamp).total_seconds()) <= 5:
                        return json.loads(last_entry.get('data_payload', '{}'))

                except Exception as e:
                    write_log(f"Timestamp parse error: {e}")

        return {}
