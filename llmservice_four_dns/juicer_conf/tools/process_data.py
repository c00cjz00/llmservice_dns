from loguru import logger

from data_juicer.config import init_configs
from data_juicer.core import Executor
import os
#import data_juicer.ops.mapper.zhtw_punct_mapper
#os.environ['HF_TOKEN']="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"

@logger.catch(reraise=True)
def main():
    cfg = init_configs()
    if cfg.executor_type == 'default':
        executor = Executor(cfg)
    elif cfg.executor_type == 'ray':
        from data_juicer.core.ray_executor import RayExecutor
        executor = RayExecutor(cfg)
    executor.run()


if __name__ == '__main__':
    main()
