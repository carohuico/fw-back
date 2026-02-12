import json

import requests
from scripts.logging import logger
from scripts.config import PLMConf
from scripts.constants import app_constants


class PLMUtility(object):
    def __init__(self):
        self.base_url = PLMConf.plm_base_url
        self.hcm_base_url = PLMConf.plm_hcm_base_url
        self.allowed_classes = PLMConf.plm_allowed_classes
        self.plm_rest_version = app_constants.PLMConstants.plm_rest_version

    def get_from_plm(self, token, url_endpoint, params=None):
        """
        This method performs get request of provided endpoint from PLM
        """
        try:
            url = self.base_url + url_endpoint
            headers = {
                'Authorization': f'Bearer {token}',
                'REST-Framework-Version': self.plm_rest_version
            }
            # if version_header:
            #     headers.update({
            #         'REST-Framework-Version': version_header,
            #     })
            response = requests.get(url, params=params, headers=headers)
            if 200 <= response.status_code <= 299:
                data = response.json()
            elif response.status_code == 401:
                logger.error(f"Unauthorized request failed while fetching data. {response.status_code} {response.content}")
                raise ConnectionError("Unauthorized")
            elif response.status_code == 400:
                err_data = json.loads(response.content)
                raise Exception(str(err_data["o:errorDetails"][0]["detail"]))
            else:
                logger.error(f"Request failed while fetching data. {response.status_code} {response.content}")
                raise Exception(str(response.content))
            return data
        except ConnectionError as err:
            raise Exception(err.args[0])
        except Exception as err:
            logger.error(f"Error while performing get request from PLM {str(err)}")
            raise Exception(f"Error while performing get request from PLM - {str(err)}")

    def get_from_plm_default_url(self, token, url):
        """
        This method performs get request of provided default url from PLM
        foor example:
            
        """
        try:
            logger.info(self.__module__)
            headers = {
                'REST-Framework-Version': self.plm_rest_version,
                'Authorization': f'Bearer {token}'
            }
            response = requests.get(url, headers=headers)
            if 200 <= response.status_code <= 299:
                data = response.json()
            elif response.status_code == 401:
                logger.error(f"Unauthorized request failed while fetching data. {response.status_code} {response.content}")
                raise ConnectionError("Unauthorized")
            elif response.status_code == 400:
                err_data = json.loads(response.content)
                raise Exception(str(err_data["o:errorDetails"][0]["detail"]))
            else:
                logger.error(f"Request failed while fetching data. {response.content}")
                raise Exception(str(response.content))
            return data
        except ConnectionError as err:
            raise Exception(err.args[0])
        except Exception as err:
            logger.error(f"Error while performing default get request from PLM {str(err)}")
            raise Exception(f"Error while performing default get request from PLM - {str(err)}")

    def post_to_plm(self, token, url_endpoint, request_data):
        """
        This method performs get request of provided endpoint from PLM
        """
        try:
            url = self.base_url + url_endpoint
            headers = {
                'REST-Framework-Version': self.plm_rest_version,
                'Authorization': f'Bearer {token}'
            }
            response = requests.post(url, json=request_data, headers=headers)
            if 200 <= response.status_code <= 299:
                data = response.json()
            elif response.status_code == 401:
                logger.error(f"Unauthorized request failed while fetching data. {response.status_code} {response.content}")
                raise ConnectionError("Unauthorized")
            elif response.status_code == 400:
                err_data = json.loads(response.content)
                raise Exception(str(err_data["o:errorDetails"][0]["detail"]))
            else:
                logger.error(f"Request failed while posting data. {response.status_code} + {str(response.content)}")
                raise Exception(str(response.content))
            return data
        except ConnectionError as err:
            raise Exception(err.args[0])
        except Exception as err:
            logger.error(f"Error while performing post request from PLM {str(err)}")
            raise Exception(f"Error while performing post request from PLM - {str(err)}")

    def update_to_plm(self, token, url_endpoint, request_data):
        """
        This method performs get request of provided endpoint from PLM
        """
        try:
            url = self.base_url + url_endpoint
            headers = {
                'Authorization': f'Bearer {token}',
                'REST-Framework-Version': self.plm_rest_version,
                'Upsert-Mode': 'true'
            }
            response = requests.patch(url, json=request_data, headers=headers)
            if 200 <= response.status_code <= 299:
                data = response.json()
            elif response.status_code == 401:
                logger.error(f"Unauthorized request failed while fetching data. {response.status_code} {response.content}")
                raise ConnectionError("Unauthorized")
            elif response.status_code == 400:
                err_data = json.loads(response.content)
                raise Exception(str(err_data["o:errorDetails"][0]["detail"]))
            else:
                logger.error(f"Request failed while updating data. {response.status_code}, {str(response.content)}")
                raise Exception(str(response.content))
            return data
        except ConnectionError as err:
            raise Exception(err.args[0])
        except Exception as err:
            logger.error(f"Error while performing update request from PLM {str(err)}")
            raise Exception(f"Error while performing update request from PLM - {str(err)}")

    def batch_request(self, token, batch_input):
        """
        This method performs get request of provided endpoint from PLM
        """
        try:
            if not batch_input:
                return {}
            url = self.base_url
            headers = {
                'REST-Framework-Version': self.plm_rest_version,
                'Content-Type': 'application/vnd.oracle.adf.batch+json',
                'Authorization': f'Bearer {token}'
            }
            response = requests.post(url, json={"parts": batch_input}, headers=headers)
            if 200 <= response.status_code <= 299:
                data = response.json()
            elif response.status_code == 401:
                logger.error(f"Unauthorized request failed while fetching data. {response.status_code} {response.content}")
                raise ConnectionError("Unauthorized")
            elif response.status_code == 400:
                err_data = json.loads(response.content)
                raise Exception(str(err_data["o:errorDetails"][0]["detail"]))
            else:
                logger.error(f"Request failed while fetching data. {response.status_code}, {response.content}")
                raise Exception(str(response.content))
            return data
        except ConnectionError as err:
            raise Exception(err.args[0])
        except Exception as err:
            logger.error(f"Error while performing batch request from PLM {str(err)}")
            raise Exception(f"Error while performing batch request from PLM - {str(err)}")

    def validate_plm_user(self, params, token):
        """
        """
        try:
            url = self.hcm_base_url + '/userAccountsLOV'
            headers = {
                'REST-Framework-Version': self.plm_rest_version,
                'Authorization': f'Bearer {token}'
            }
            response = requests.get(url, params=params, headers=headers)
            if 200 <= response.status_code <= 299:
                data = response.json()
            elif response.status_code == 401:
                logger.error(f"Unauthorized request failed while fetching data. {response.status_code} {response.content}")
                raise ConnectionError("Unauthorized")
            elif response.status_code == 400:
                err_data = json.loads(response.content)
                raise Exception(str(err_data["o:errorDetails"][0]["detail"]))
            else:
                logger.error(f"Request failed while fetching data. {response.content}")
                raise Exception(str(response.content))
            return data
        except ConnectionError as err:
            raise Exception(err.args[0])
        except Exception as err:
            logger.error("Error while validating user in PLM ", str(err))
            raise Exception("Error while validating user in PLM ")

    def delete_from_plm(self, token, url_endpoint):
        """
        This method performs get request of provided endpoint from PLM
        """
        try:
            url = self.base_url + url_endpoint
            headers = {
                'Authorization': f'Bearer {token}',
                'REST-Framework-Version': self.plm_rest_version,
                'Upsert-Mode': 'true'
            }
            response = requests.delete(url, headers=headers)
            if 200 <= response.status_code <= 299:
                data = True
            elif response.status_code == 401:
                logger.error(f"Unauthorized request failed while deleting data. {response.status_code} {response.content}")
                raise ConnectionError("Unauthorized")
            elif response.status_code == 400:
                err_data = json.loads(response.content)
                raise Exception(str(err_data["o:errorDetails"][0]["detail"]))
            else:
                logger.error(f"Request failed while deleting data. {response.status_code}, {str(response.content)}")
                raise Exception(str(response.content))
            return data
        except ConnectionError as err:
            raise Exception(err.args[0])
        except Exception as err:
            logger.error(f"Error while performing delete request from PLM {str(err)}")
            raise Exception(f"Error while performing delete request from PLM - {str(err)}")
