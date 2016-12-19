class BaseComponent:
    config_name = None

    @classmethod
    def create_components(cls, config, context):
        comps = []

        for data in config.values():
            comp = cls(data)
            comp.setup(context.event_manager)
            comps.append(comp)

        return comps
