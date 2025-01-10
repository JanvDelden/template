import yaml, munch


def load_yaml_file(filepath):
    with open(filepath, "r") as file:
        return yaml.safe_load(file)


def get_config(config_path):
    # Get the main configuration file
    main_cfg = load_yaml_file(config_path)

    # Get the default arguments, which are paths to other YAML files
    default_args = main_cfg.pop("default_args", None)

    if default_args is not None:
        # Load the configuration from the default argument files
        for path in default_args:
            default_config = load_yaml_file(path)

            # Modify content of default config if different entry in main config and then update main config with modified default config
            for key in main_cfg:
                if key in default_config:
                    default_config[key] = main_cfg[key]

            main_cfg.update(default_config)
    return munch.Munch.fromDict(main_cfg)


def code_formatter_test_fn(
    first_variable, second_variable, third_variable, fourth_variable, fifth_variable, sixth_variable, seventh_variable=None
):
    """
    Test docstring
    """
    pass
