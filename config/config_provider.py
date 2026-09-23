class ConfigProvider:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._discount_configs = []
        return cls._instance

    def set_discount_configs(self, configs):
        self._discount_configs = list(configs)

    def get_discount_configs(self):
        return list(self._discount_configs)
