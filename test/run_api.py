import os
import shutil

import pytest

from tools import logger
from common.base_requests import BaseRequest
from tools.data_process import DataProcess
from tools.read_file import ReadFile

report = ReadFile.read_config('$.file_path.report')
logfile = ReadFile.read_config('$.file_path.log')
# 读取excel数据对象
cases = ReadFile.read_testcase()


class TestApi:

    @classmethod
    def run(cls):
        if os.path.exists('../report'):
            shutil.rmtree(path='../report')
        logger.add(logfile, enqueue=True, encoding='utf-8')
        logger.info('开始测试...')
        pytest.main(args=[f'--alluredir={report}/data'])
        os.system(f'allure generate {report}/data -o {report}/html --clean')
        logger.success('报告已生成')

    @pytest.mark.parametrize('case', cases)
    def test_main(self, case):
        response, expect = BaseRequest.send_request(case)
        # 断言操作
        DataProcess.assert_result(response, expect)


if __name__ == '__main__':
    TestApi.run()