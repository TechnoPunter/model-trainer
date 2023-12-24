import importlib
import os

from commons.config.reader import cfg
from commons.consts.consts import NEXT_CLOSE_FILE_NAME, RAW_PRED_FILE_NAME


def get_strats_modules(base_path: str, package_name: str):
    result = []
    package_path = package_name.replace('.', '/')
    package_directory = os.path.dirname(__file__)
    package_directory = os.path.join(package_directory, base_path, package_path)

    # Loop through all files in the package directory
    for filename in os.listdir(package_directory):
        if filename.endswith('.py') and not (filename.startswith("__")) and \
                filename[:-3] in cfg['steps']['strats']:
            module_name = filename[:-3]  # Remove the '.py' extension
            module_path = f'{package_name}.{module_name}'
            try:
                module = importlib.import_module(module_path)
                result.append(module)
            except ImportError as e:
                print(f'Error importing module {module_path}: {e}')

    return result


def run_get_predictions(prediction_params) -> str:
    """

    Args:
        :param prediction_params - tuple with following arguments
            params: Parameters
            data: OHLC++ data
            strategies: List of modules from strategy package
            scrip_name: Name of the scrip e.g. NSE_BANDHANBNK

    Returns:

    """
    params, data, scrip_name, mode = prediction_params
    strategies = get_strats_modules('../../', 'trainer.strategies')
    for strategy in strategies:

        strategy_name = strategy.__name__
        try:
            data['scrip'] = scrip_name
            result_df = strategy.get_predictions(data, mode, scrip_name)
            result_df['signal'] = result_df['signal'].astype(int)
        except Exception as ex:
            print(f"Error with {strategy.__name__} ex: {ex}")
            continue

        if result_df is not None:
            pred_key = ".".join([strategy_name, scrip_name])
            suffix = NEXT_CLOSE_FILE_NAME if mode == 'NEXT-CLOSE' else RAW_PRED_FILE_NAME
            result_df.to_csv(os.path.join(params['work_path'], pred_key + suffix), index=False, float_format='%.2f')
    status = f"Completed get_prediction for {scrip_name} & {strategies}"
    print(status)
    return status
