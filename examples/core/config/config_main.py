from symphony.bdk.core.config.bdk_config_loader import BdkConfigLoader


class ConfigMain:

    @staticmethod
    def run():
        config_1 = BdkConfigLoader.load_from_file("/absolute/path/to/config.yaml")

        with open("/absolute/path/to/config.yaml") as config_file:
            config_2 = BdkConfigLoader.load_from_content(config_file.read())

        config_3 = BdkConfigLoader.load_from_symphony_dir("config.yaml")


if __name__ == "__main__":
    ConfigMain.run()
