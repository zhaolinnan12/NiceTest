from tools import logger, extractor, convert_json, rep_expr, allure_step
from tools.read_file import ReadFile


class DataProcess:
    response_dict = {}
    header = ReadFile.read_config('$.request_headers')
    have_token = header.copy()

    @classmethod
    def save_response(cls, key: str, value: object) -> None:
        """
        保存实际响应
        :param key: 保存字典中的key，一般使用用例编号
        :param value: 保存字典中的value，使用json响应
        """
        cls.response_dict[key] = value
        logger.info(f'添加key: {key}, 对应value: {value}')

    @classmethod
    def handle_path(cls, path_str: str) -> str:
        """路径参数处理
        :param path_str: 带提取表达式的字符串 /&$.case_005.data.id&/state/&$.case_005.data.create_time&
        """
        return rep_expr(path_str, cls.response_dict)

    @classmethod
    def handle_header(cls, token: str) -> dict:
        """处理header
        :param token: 写： 写入token到header中， 读： 使用带token的header， 空：使用不带token的header
        return
        """
        if token == '读':
            return cls.have_token
        else:
            return cls.header

    @classmethod
    def handler_files(cls, file_obj: str) -> object:
        """file对象处理方法
        :param file_obj: 上传文件使用，格式：接口中文件参数的名称:"文件路径地址"/["文件地址1", "文件地址2"]
        实例- 单个文件:
        """
        if file_obj == '':
            return
        for k, v in convert_json(file_obj).items():
            # 多文件上传
            if isinstance(v, list):
                files = []
                for path in v:
                    files.append((k, (open(path, 'rb'))))
            else:
                # 单文件上传
                files = {k: open(v, 'rb')}
        return files

    @classmethod
    def handle_data(cls, variable: str) -> dict:
        """请求数据处理
        :param variable: 请求数据，传入的是可转换字典/json的字符串,其中可以包含变量表达式
        return 处理之后的json/dict类型的字典数据
        """
        if variable == '':
            return
        data = rep_expr(variable, cls.response_dict)
        variable = convert_json(data)
        return variable

    @classmethod
    def assert_result(cls, response: dict, expect_str: str):
        """ 预期结果实际结果断言方法
        :param response: 实际响应字典
        :param expect_str: 预期响应内容，从excel中读取
        return None
        """
        expect_dict = convert_json(expect_str)
        index = 0
        for k, v in expect_dict.items():
            actual = extractor(response, k)
            index += 1
            print("服务端返回结果actual type :", type(actual))
            print("excel预期结果，v type :", type(v))
            logger.info(f'第{index}个断言,实际结果:{actual} | 预期结果:{v} \n断言结果 {actual == v}')
            allure_step(f'第{index}个断言',  f'实际结果:{actual} = 预期结果:{v}')
            try:
                assert actual == v
            except AssertionError:
                raise AssertionError(f'断言失败 -|- 实际结果:{actual} || 预期结果: {v}')
