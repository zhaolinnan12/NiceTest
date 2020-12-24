import requests
from tools import allure_step, allure_title, logger, extractor
from tools.data_process import DataProcess
from tools.read_file import ReadFile


class BaseRequest(object):
    session = None
#全局公用session
    @classmethod
    def get_session(cls):
        if cls.session is None:
            cls.session = requests.Session()
        return cls.session

    #不需要实例化，直接调用
    @classmethod
    def send_request(cls, case: list, env: str = 'dev') -> object:
        """
        :处理case数据，转换成可用数据发送请求
        :case: 读取出来的每一行用例内容，可进行解包
        :env: 环境名称config.yaml server下的 dev 后面的基准地址
        """
        case_number, case_title, path, token, method, parametric_key, file_obj, data, expect = case
        # allure测试报告报告 用例标题
        allure_title(case_title)
        # 处理文件中url、header、data、file、的前置方法
        url = ReadFile.read_config(f'$.server.{env}') + DataProcess.handle_path(path)
        allure_step('请求地址', url)
        header = DataProcess.handle_header(token)
        allure_step('请求头', header)
        data = DataProcess.handle_data(data)
        allure_step('请求参数', data)
        file = DataProcess.handler_files(file_obj)
        allure_step('上传文件', file)
        # 发送请求
        res = cls.send_api(url, method, parametric_key, header, data, file)
        allure_step('响应耗时(s)', res.elapsed.total_seconds())
        allure_step('响应内容', res.json())
        # 响应后操作
        if token == '写':
            DataProcess.have_token['token'] = extractor(res.json(), ReadFile.read_config('$.expr.token'))
            #全局使用登录token
            allure_step('请求头中添加Token', DataProcess.have_token)
        DataProcess.save_response(case_number, res.json())
        allure_step('存储实际响应', DataProcess.response_dict)
        return res.json(), expect

    @classmethod
    def send_api(cls, url, method, parametric_key, header=None, data=None, file=None) -> object:
        """
        :method: 请求方法
        :url: 请求url
        :parametric_key: 入参关键字， get/delete/head/options/请求使用params,
         post/put/patch请求可使用json（application/json）/data
        :data: 参数数据，默认等于None
        :file: 文件对象
        :header: 请求头
        :返回response对象
        """
        session = cls.get_session()
        #根据传参判断请求类型
        if parametric_key == 'params':
            res = session.request(method=method, url=url, params=data, headers=header)
        elif parametric_key == 'data':
            res = session.request(method=method, url=url, data=data, files=file, headers=header)
        elif parametric_key == 'json':
            res = session.request(method=method, url=url, json=data, files=file, headers=header)
        else:
            raise ValueError(
                '可选关键字为：get/delete/head/options/请求使用params, post/put/patch请求可使用json（application/json）/data')
        logger.info(f'\n请求地址:{url}\n请求方法:{method}\n请求头:{header}\n请求参数:{data}\n响应数据:{res.json()}')
        return res





