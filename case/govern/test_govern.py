# -*- coding:utf-8 -*-

"""
@Author: huang
@Date: 2019-07-22 11:05
@LastEditors: huang
@LastEditTime: 2019-07-22 11:05
@Description:
"""

import allure
import pytest
from conf import setting as conf
from utils.platon_lib.ppos import Ppos
from hexbytes import HexBytes

from common.load_file import  get_node_info
from common.govern_util import *
from common.connect import connect_web3
from deploy.deploy import AutoDeployPlaton


class TestGovern:
    cbft_json_path = conf.CBFT2
    node_yml_path = conf.GOVERN_NODE_YML

    node_info = get_node_info(node_yml_path)

    # 共识节点信息
    rpc_list, enode_list, nodeid_list, ip_list, port_list = node_info.get('collusion')

    # 非共识节点信息
    rpc_list2, enode_list2, nodeid_list2, ip_list2, port_list2 = node_info.get('nocollusion')

    # 内置账户-拥有无限金额
    address = Web3.toChecksumAddress(conf.ADDRESS)

    # 钱包私钥
    private_key = conf.PRIVATE_KEY

    # 内置账户密码-拥有无限金额
    pwd = conf.PASSWORD

    # 没有绑定节点的钱包地址
    address_list = ["0x2b9CA6c401e96A7Ca3ce5e2E5f02a665E4f1631B", "0xdd3aA6f0B04A01a418b07F3dE41D4307A03E1016",
                    "0xb2fC346DF94cBE871AF2ea56B9E56E477569FcDb"]

    # 没有绑定节点的钱包私钥
    private_key_list = ["5cd4c60a74e69d35ed766bae72e32ded93cbd10eb545a558120d82f29f205823",
                       "e11e8dd946380db75036e4ac341d4eb24cfac01d637f01088658b9838639b8f6",
                       "0aea84e2169919c796b4983b130bf31ac152f78319f91f56563bd75cf842314c"]

    # 一个共识周期数包含的区块数
    block_count=250

    # 提案截止块高中，设置截止块高在第几个共识周期中
    conse_index=1

    # 提案截止块高中，设置截止块高在最大的共识周期中
    conse_border=3

    # 随机字符个数
    length=6

    # 节点的第三方主页
    website = 'https://www.platon.network/#/'

    # 节点的描述
    details = '发起升级提案'

    # 提案在github上的id
    github_id = '101'

    # 时间间隔-秒
    time_interval=10

    # 基本的gas
    base_gas = 21000

    # 基本的gasprice
    base_gas_price=60000000000000

    # 每次转账的金额
    trans_amount=100000000000000000000000000

    # 进行质押的gas
    staking_gas = base_gas + 32000 + 6000 + 100000

    # 发起提案的gas
    proposal_gas = base_gas + 450000 + 9000 + 50000

    # 发起投票的gas
    vote_gas = base_gas + 2000 + 9000 + 50000

    # 发起版本声明的gas
    declare_gas=base_gas + 3000 + 9000 + 50000

    # 进行质押的金额
    staking_amount=10000000

    # 发起提案的金额
    proposal_amount=10000000

    # 发起投票的金额
    vote_amount=10000000

    # 发起版本声明的金额
    declare_amount=10000000

    def setup_class(self):
        log.info('setup_class-开始')
        self.auto = AutoDeployPlaton(self.cbft_json_path)
        self.auto.kill_of_yaml(self.node_yml_path)
        self.auto.start_all_node(self.node_yml_path)

        self.link_1 = Ppos(self.rpc_list[0], self.address)

        # 新钱包地址和私钥
        self.no_link_1 = Ppos(self.rpc_list[1], self.address_list[0], privatekey= self.private_key_list[0])
        self.no_link_2 = Ppos(self.rpc_list[2], self.address_list[1], privatekey=self.private_key_list[1])
        self.no_link_3 = Ppos(self.rpc_list[3], self.address_list[2], privatekey=self.private_key_list[2])

        log.info('默认初始化后，给所有钱包进行转账处理')
        # 默认初始化后，给所有钱包进行转账处理
        # self.w3_list =connect_web3(url) [connect_web3(url) for url in self.rpc_list]
        self.w3_list = connect_web3(self.rpc_list[0])

        # 等待上链后再操作
        for to_account in self.address_list:
            tx_hash=self.transaction(self.address, to_account)
            tx_hash_hex=HexBytes(tx_hash).hex()
            result = self.w3_list[0].eth.waitForTransactionReceipt(tx_hash_hex)

        log.info('获取随机生成字符的对象 随机设置主题和说明')
        # 获取随机生成字符的对象 随机设置主题和说明
        self.rand_str = gen_random_string(self.length)
        self.external_id='id_'.join(self.rand_str)
        self.node_name='name_'.join(self.rand_str)
        self.topic = 'topic_'.join(self.rand_str)
        self.desc = 'desc_'.join(self.rand_str)

        log.info('setup_class-结束')

    # 重新部署链
    def re_deploy(self):
        log.info('re_deploy-开始')

        self.auto = AutoDeployPlaton(self.cbft_json_path)
        self.auto.kill_of_yaml(self.node_yml_path)
        self.auto.start_all_node(self.node_yml_path)

        self.link_1 = Ppos(self.rpc_list[0], self.address)

        # 新钱包地址和私钥
        self.no_link_1 = Ppos(self.rpc_list[0], self.address_list[0], privatekey=self.private_key_list[0])
        self.no_link_2 = Ppos(self.rpc_list[0], self.address_list[1], privatekey=self.private_key_list[1])
        self.no_link_3 = Ppos(self.rpc_list[0], self.address_list[2], privatekey=self.private_key_list[2])

        log.info('默认初始化后，给所有钱包进行转账处理')
        # 默认初始化后，给所有钱包进行转账处理
        # self.w3_list = [connect_web3(url) for url in self.rpc_list]
        self.w3_list = connect_web3(self.rpc_list[0])

        # 等待上链后再操作
        for to_account in self.address_list:
            tx_hash = self.transaction(self.address, to_account)
            tx_hash_hex = HexBytes(tx_hash).hex()
            result = self.w3_list[0].eth.waitForTransactionReceipt(tx_hash_hex)

        log.info('获取随机生成字符的对象 随机设置主题和说明')
        # 获取随机生成字符的对象 随机设置主题和说明
        self.rand_str = gen_random_string(self.length)
        self.external_id = 'id_'.join(self.rand_str)
        self.node_name = 'name_'.join(self.rand_str)
        self.topic = 'topic_'.join(self.rand_str)
        self.desc = 'desc_'.join(self.rand_str)

        log.info('re_deploy-结束')

    # 默认初始化后，给所有钱包进行转账处理
    def transaction(self, from_address, to_address=None):
        self.link_1.web3.personal.unlockAccount(self.address, self.pwd, 666666)
        params = {
            'to': to_address,
            'from': from_address,
            'gas': self.base_gas,
            'gasPrice': self.base_gas_price,
            'value': self.trans_amount
        }
        tx_hash = self.link_1.eth.sendTransaction(params)
        return tx_hash

    def submit_version(self,new_version,end_number,effect_number):
        '''
        提交升级提案
        :param rpc_link,block_count,conse_index
        :return: list
        '''

        # rpc_link = Ppos(self.rpc_list[2], self.address_list[2], chainid=101, privatekey=self.private_key_list[2])
        rpc_link=self.link_1

        # 获取截止、生效块高
        # end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link, self.block_count, self.conse_index)

        # 获取验证人列表
        verifierinfo = rpc_link.getVerifierList()
        v_list = verifierinfo.get('Data')

        verifier_list = []

        # 获取验证人节点ID列表
        for list1 in v_list:
            verifier_list.append(list1.get('NodeId'))

        # if is_exist_ineffective_proposal_info(rpc_link):
        #     log.info('链上存在生效的提案,不能再发起升级提案')
        #     return
        # else:

        # 获取升级版本号
        # new_version = get_version(rpc_link, flag=3)

        # 获取验证人的质押钱包地址和私钥
        address = Web3.toChecksumAddress(get_stakingaddree(rpc_link,verifier_list[1]))
        privatekey = get_privatekey(address)

        # 新建一个链接连接到链上 用上面的质押钱包地址和私钥
        rpc_link = Ppos(self.rpc_list[2], address, chainid=101, privatekey=privatekey)

        # 发起升级提案
        result = rpc_link.submitVersion(verifier_list[1], self.website, new_version, end_number, effect_number,from_address=address, privatekey=privatekey)

        log.info('升级提案后的结果为={}'.format(result))
        log.info('发起升级提案成功')
        return result

    @allure.title('1-发起升级提案-升级版本号的验证-升级版本号为空及格式不正确的验证')
    def test_submit_version_version_not_empty(self):
        '''
        用例id 9,12,19~22
        发起升级提案-升级版本号的验证-升级版本号为空及格式不正确的验证
        '''

        # 链上是否有未生效的升级提案，为True则有
        flag=is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if not flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link=self.link_1
        node_id=self.nodeid_list[0]

        # 获取单个合理的截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number=get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 版本号
        cur_version= get_version(rpc_link)
        new_version1 = get_version(rpc_link,flag=1)
        new_version2 = get_version(rpc_link,flag=2)

        log.info('当前版本号={}'.format(cur_version))

        # 版本号参数列表
        version_list = [new_version1,new_version2]

        log.info('没有有效的升级提案，可以发起升级提案')
        log.info('1-test_submit_version_version_not_empty-内置验证人节点发起升级提案')
        for new_version in version_list:
            if new_version == version_list[0]:
                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                log.info('提案结果={}'.format(result))

                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('should larger than current version', 0, len(
                    info)) > 0, '提交升级提案参数中升级目的版本号不正确（升级目的版本号<=链上当前版本号），发起升级提案失败'
            elif new_version == version_list[1]:
                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                log.info('提案结果={}'.format(result))

                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('should larger than current version', 0, len(
                    info)) > 0, '提交升级提案参数中升级目的版本号不正确（升级目标版本的大版本号等于链上当前版本号，升级目的版本号为小版本号大于链上链上当前小版本号），发起升级提案失败'
            else:
                pass
        log.info('1-test_submit_version_version_not_empty-发起升级提案-升级版本号的验证-升级版本号为空及格式不正确的验证-结束')

    @allure.title('2-发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性')
    def test_submit_version_end_block_number(self):
        '''
        用例id 10,24~28,32~34
        发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if not flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1
        node_id = self.nodeid_list[0]

        # 获取各类不合理的截止块高 在第几个共识周期 共识周期最大边界
        block_list = get_all_invalid_end_block_number(rpc_link,self.block_count,self.conse_index,self.conse_border)

        # 升级版本号
        new_version = get_version(rpc_link, flag=3)
        log.info('升级提案版本号={}'.format(new_version))

        log.info('2-test_submit_version_end_block_number-内置验证人节点发起升级提案')
        for count in range(len(block_list)):
            if count == 0:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]

                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('end-voting-block invalid', 0, len(info)) > 0, '截止区块块高不正确，不能等于当前块高，发起升级提案失败'
            elif count == 1:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]

                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('end-voting-block invalid', 0, len(info)) > 0, '截止区块块高不正确，不是第230块块高，发起升级提案失败'
            elif count == 2:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]

                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('end-voting-block invalid', 0, len(info)) > 0, '截止区块块高不正确，不是第230块块高，发起升级提案失败'
            elif count == 3:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]

                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info=result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('end-voting-block invalid', 0, len(info))>0, '截止区块块高不正确，为N+1周期的第230块块高，发起升级提案失败'
            else:
                pass
        log.info('2-test_submit_version_end_block_number-发起升级提案-截止区块高度的验证-验证截止区块的合法性及正确性-结束')

    @allure.title('3-发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性')
    def test_submit_version_effect_block_number(self):
        '''
        用例id 11,38~43
        发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if not flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1
        node_id = self.nodeid_list[0]

        # 获取各类不合理的生效块高 在第几个共识周期 共识周期最大边界
        block_list = get_all_invalid_effect_block_number(rpc_link,self.block_count,self.conse_index)

        # 升级版本号
        new_version = get_version(rpc_link, flag=3)
        log.info('升级提案版本号={}'.format(new_version))

        log.info('3-test_submit_version_effect_block_number-内置验证人节点发起升级提案')
        for count in range(len(block_list)):
            if count == 0:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0, len(info)) > 0, '生效区块块高不正确，生效块高设置为=当前块高，发起升级提案失败'
            elif count == 1:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0, len(info)) > 0, '生效区块块高不正确，生效块高设置为=截止块高，发起升级提案失败'
            elif count == 2:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0,
                                 len(info)) > 0, '生效区块块高不正确，生效块高为第(N + 4)个共识周期的第230块块高，发起升级提案失败'
            elif count == 3:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0,
                                 len(info)) > 0, '生效区块块高不正确，生效块高为第(N + 5)个共识周期的第229块块高，发起升级提案失败'
            elif count == 4:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0,
                                 len(info)) > 0, '生效区块块高不正确，生效块高为第(N + 5)个共识周期的第231块块高，发起升级提案失败'
            elif count == 5:
                end_number = block_list[count][0]
                effect_number = block_list[count][1]
                log.info('第{}组块高-截止块高={}-生效块高={}'.format(count+1,end_number, effect_number))

                result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                                endVotingBlock=end_number, activeBlock=effect_number)
                info = result.get('ErrMsg')
                assert result.get('Status') == False
                assert info.find('active-block invalid', 0, len(info)) > 0, '生效区块块高不正确，为第(N + 11)个共识周期的第250块块高，发起升级提案失败'
            else:
                pass
        log.info('3-test_submit_version_effect_block_number-发起升级提案-生效区块高度的验证-验证生效区块的合法性及正确性-结束')

    @allure.title('4-提案人身份的验证（质押排名101之后且质押TOKEN也不符合要求提案人），新人节点发起升级提案')
    def test_submit_version_on_newnode(self):
        '''
        用例id 14
        发起升级提案-提案人身份的验证（质押排名101之后且质押TOKEN也不符合要求提案人），新人节点发起升级提案
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if not flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1

        # 升级版本号
        new_version = get_version(self.link_1,3)
        log.info('当前生成的提案升级版本号={}'.format(new_version))

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        revice = rpc_link.getCandidateList()
        node_info = revice.get('Data')
        candidate_list = []

        for nodeid in node_info:
            candidate_list.append(nodeid.get('NodeId'))

        # 判断配置文件中的节点是否都已质押
        if set(self.nodeid_list2) < set(candidate_list):
            log.info('节点配置文件中的地址已全部质押，该用例执行失败')
        else:
            # rpc_link = Ppos(self.rpc_list[1], self.address_list[0], chainid=101, privatekey=self.private_key_list[0])
            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    log.info('test_submit_version_on_newnode-新节点发起升级提案')
                    result = rpc_link.submitVersion(verifier=self.nodeid_list2[i], url=self.website,newVersion=new_version,
                                                          endVotingBlock=end_number, activeBlock=effect_number)
                    log.info('新用户节点发起提案失败')
                    info = result.get('ErrMsg')
                    assert result.get('Status') == False
                    assert info.find('not a verifier', 0,
                                     len(info)) > 0, '发起升级提案失败-发起升级提案时，该节点是新人节点，而不是验证人节点'
                    break
        log.info('4-test_submit_version_on_newnode-发起升级提案-提案人身份的验证（质押排名101之后且质押TOKEN也不符合要求提案人），新人节点发起升级提案-结束')

    @allure.title('5-提案人身份的验证（质押排名101之后但质押TOKEN符合要求的提案人），候选人节点发起升级提案')
    def test_submit_version_on_candidatenode(self):
        '''
        用例id 13
        发起升级提案-提案人身份的验证（质押排名101之后但质押TOKEN符合要求的提案人），候选人节点发起升级提案
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if not flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1

        # 当前版本号
        cur_version = get_version(rpc_link)
        log.info('当前版本号={}'.format(cur_version))

        # 升级版本号
        new_version = get_version(rpc_link,3)
        log.info('当前生成的提案升级版本号={}'.format(new_version))

        log.info('没有有效的升级提案，可以发起升级提案')
        n_list = get_current_settle_account_candidate_list(rpc_link)

        # rpc_link = Ppos(self.rpc_list[1], self.address_list[0], chainid=101, privatekey=self.private_key_list[0])

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行升级提案，不存在就先进行质押
        if n_list:
            dv_nodeid = n_list[0]
            log.info('存在候选人节点，取第一个候选人节点={}'.format(dv_nodeid))
        else:
            # 获取候选人节点id列表
            revice = rpc_link.getCandidateList()
            node_info = revice.get('Data')
            candidate_list = []

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    result = rpc_link.createStaking(0, self.address_list[1], self.nodeid_list2[i], externalId=self.external_id,nodeName=self.node_name,
                                                    website=self.website, details=self.details,amount=self.staking_amount,
                                                    programVersion=cur_version,  from_address=self.address_list[1],
                                                    gasPrice=self.base_gas_price,gas=self.staking_gas)
                    dv_nodeid = self.nodeid_list2[i]
                    log.info('不存在候选人节点，质押后的候选人节点={}'.format(dv_nodeid))
                    log.info('候选人节点质押成功')
                    assert result.get('Status') == True
                    assert result.get('ErrMsg') == 'ok'
                break

        log.info('候选人节点质押完成')
        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number = get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        result = rpc_link.submitVersion(verifier=dv_nodeid, url=self.website, newVersion=new_version,
                                        endVotingBlock=end_number, activeBlock=effect_number)
        log.info('候选人节点发起提案失败')
        info = result.get('ErrMsg')
        assert result.get('Status') == False
        assert info.find('not a verifier', 0,
                         len(info)) > 0, '发起升级提案失败-发起升级提案时，该节点是候选人节点，而不是验证人节点'
        log.info('test_submit_version_on_candidatenode-发起升级提案-提案人身份的验证（质押排名101之后但质押TOKEN符合要求的提案人），候选人节点发起升级提案-结束')

    @allure.title('6-发起升级提案-升级提案成功的验证')
    def test_submit_version_success(self):
        '''
        用例id 15,18   正确的截止块高29~31,35~37,正确的生效块高44~46,47
        发起升级提案-升级提案成功的验证
        '''
        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(self.link_1)

        # 存在有效的升级提案，需要重新部署链
        if not flag:
            log.info('存在有效的升级提案，需要重新部署链')

            # 重新部署链
            log.info('重新部署链开始-re_deploy')
            self.re_deploy()
            log.info('重新部署链结束-re_deploy')

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

        log.info('没有有效的升级提案，可以发起升级提案')
        rpc_link = self.link_1

        # 升级版本号
        new_version =get_version(rpc_link,3)

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number,effect_number = get_single_valid_end_and_effect_block_number(rpc_link,self.block_count,self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 获取验证人id列表
        revice = rpc_link.getVerifierList()
        node_info = revice.get('Data')
        verifier_list = []

        dv_nodeid = False

        for nodeid in node_info:
            verifier_list.append(nodeid.get('NodeId'))

        for i in range(0, len(verifier_list)):
            if verifier_list[i] not in self.nodeid_list:
                dv_nodeid = verifier_list[i]
                break

        if dv_nodeid:
            result = rpc_link.submitVersion(verifier=dv_nodeid, url=self.website, newVersion=new_version,
                                            endVotingBlock=end_number, activeBlock=effect_number)
            log.info('result='.format(result))
            assert result.get('Status') == True
            assert result.get('ErrMsg') == 'ok', '发起升级提案成功'
            log.info('发起升级提案成功')
        else:
            log.info('发起升级提案-当前结算周期不存在可用验证人（创始验证人节点），该用例验证失败')

        log.info('6-test_submit_version_success-发起升级提案-升级提案成功的验证-结束')

    @allure.title('7-发起升级提案-未生效的升级提案的验证')
    def test_submit_ineffective_verify(self):
        '''
        用例id 16,17
        发起升级提案-未生效的升级提案的验证
        '''

        rpc_link=self.link_1
        node_id=self.nodeid_list[0]

        # 链上是否有未生效的升级提案，为True则有
        flag = is_exist_ineffective_proposal_info(rpc_link)

        # 设置获取截止、生效块高的对象
        new_version = get_version(rpc_link, 3)

        # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
        end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link, self.block_count,
                                                                                 self.conse_index)
        log.info('截止块高={}-生效块高={}'.format(end_number, effect_number))

        # 存在未生效的升级提案
        if not flag:
            log.info('存在未生效的升级提案，发起升级提案失败')
            result = rpc_link.submitVersion(verifier=node_id, url=self.website, newVersion=new_version,
                                            endVotingBlock=end_number, activeBlock=effect_number)
            log.info('result='.format(result))
            info = result.get('ErrMsg')
            assert result.get('Status') == False
            assert info.find('existing a version proposal', 0,
                             len(info)) > 0, '有未生效的升级提案，发起升级提案失败'
        else:
            log.info('不存在有效的升级提案，需先发起一个升级提案，再继续升级提案')

            result=self.submit_version(new_version,end_number,effect_number)
            log.info('提案后的结果={}'.format(result))
            assert result.get('Status') == True, '发起升级提案成功'

            log.info('等待一段时间={}秒'.format(self.time_interval))
            time.sleep(self.time_interval)

            log.info('再新发起一个升级提案')
            result=self.submit_version(new_version,end_number,effect_number)
            log.info('提案后的结果={}'.format(result))
            info = result.get('ErrMsg')
            assert result.get('Status') == False
            assert info.find('existing a version proposal', 0,
                             len(info)) > 0, '有未生效的升级提案，发起升级提案失败'
        log.info('7-test_submit_ineffective_verify-发起升级提案-未生效的升级提案的验证-结束')

    @allure.title('8-对升级提案进行投票-投票交易的验证（节点版本号的正确性校验）')
    def test_vote_vote_trans(self):
        '''
        用例id 48~50,60
        对升级提案进行投票-投票交易的验证（节点版本号的正确性校验）
        '''
        rpc_link=self.link_1
        node_id = self.nodeid_list[0]
        option = 1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案，然后再进行投票
        flag=is_exist_ineffective_proposal_info_for_vote(rpc_link)
        log.info('flag={}'.format(flag))

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 获取截止、生效块高
            end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link, self.block_count, self.conse_index)

            # 发起升级提案
            self.submit_version(end_number, effect_number)
        else:
            log.info('有可投票的升级提案，直接进行投票')

        # 设置获取版本号的对象
        little_version = get_version(rpc_link, 1)
        cur_version = get_version(rpc_link)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}'.format(little_version, cur_version))
        version_list = [little_version, cur_version]

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        # 投票
        for node_version in version_list:
            if node_version == little_version:
                result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                assert result.get('Status') == False,'发起升级投票交易时节点版本号不正确（小于提案升级版本号）'
            elif node_version == cur_version:
                result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=node_version)
                assert result.get('Status') == False,'发起升级投票交易时节点版本号不正确（等于提案升级版本号）'
            else:
                pass
        log.info('8-test_vote_vote_trans-对升级提案进行投票-投票交易的验证（节点版本号的正确性校验）-结束')

    @allure.title('9-对升级提案进行投票-是否在投票周期内的验证 conse_size * N - 20')
    def test_vote_notin_vote_cycle_a(self):
        '''
        用例id 51,54
        对升级提案进行投票-是否在投票周期内的验证 conse_size * N - 20
        '''
        log.info('对升级提案进行投票-是否在投票周期内的验证 conse_size * N - 20')

        # 重新部署链
        log.info('重新部署链开始-re_deploy')
        self.re_deploy()
        log.info('重新部署链结束-re_deploy')

        log.info('等待一段时间={}秒'.format(self.time_interval))
        time.sleep(self.time_interval)

        rpc_link = self.link_1
        node_id = self.nodeid_list[0]
        option = 1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案，然后再进行投票
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
            block_list = get_all_legal_end_and_effect_block_number_for_vote(rpc_link, self.block_count,
                                                                            self.conse_index, self.conse_border)
            end_number = block_list[0][0]
            effect_number = block_list[0][1]

            # 发起升级提案
            self.submit_version(end_number, effect_number)
        else:
            log.info('有可投票的升级提案，直接进行投票')

        log.info('等待一段时间={}秒，再去获取提案信息'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        # 等待一定的块高，再投票
        is_cur_block_number_big_than_end_block_number(rpc_link, end_block_number)

        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
        assert result.get('Status') == False, '发起升级投票交易时，不在投票周期，投票不成功'
        log.info('9-test_vote_notin_vote_cycle_a-对升级提案进行投票-是否在投票周期内的验证 conse_size * N - 20-结束')

    @allure.title('10-对升级提案进行投票-是否在投票周期内的验证 conse_size * (M-1) - 20')
    def test_vote_notin_vote_cycle_b(self):
        '''
        用例id 52,55
        对升级提案进行投票-是否在投票周期内的验证 conse_size * (M-1) - 20
        '''
        log.info('对升级提案进行投票-是否在投票周期内的验证 conse_size * (M-1)  - 20')

        # 重新部署链
        log.info('重新部署链开始-re_deploy')
        self.re_deploy()
        log.info('重新部署链结束-re_deploy')

        log.info('等待一段时间={}秒'.format(self.time_interval))
        time.sleep(self.time_interval)

        rpc_link = self.link_1
        node_id = self.nodeid_list[0]
        option = 1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案，然后再进行投票
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
            block_list = get_all_legal_end_and_effect_block_number_for_vote(rpc_link, self.block_count,
                                                                            self.conse_index, self.conse_border)
            end_number = block_list[1][0]
            effect_number = block_list[1][1]

            # 发起升级提案
            self.submit_version(end_number, effect_number)
        else:
            log.info('有可投票的升级提案，直接进行投票')

        log.info('等待一段时间={}秒，再去获取提案信息'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        # 等待一定的块高，再投票
        is_cur_block_number_big_than_end_block_number(rpc_link, end_block_number)

        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
        assert result.get('Status') == False, '发起升级投票交易时，不在投票周期，投票不成功'
        log.info('10-test_vote_notin_vote_cycle_b-对升级提案进行投票-是否在投票周期内的验证 conse_size * (M-1) - 20-结束')

    @allure.title('11-对升级提案进行投票-是否在投票周期内的验证 conse_size * M- 20')
    def test_vote_notin_vote_cycle_c(self):
        '''
        用例id 53,56
        对升级提案进行投票-是否在投票周期内的验证 conse_size * M- 20
        '''
        log.info('对升级提案进行投票-是否在投票周期内的验证 conse_size * (M)  - 20')

        # 重新部署链
        log.info('重新部署链开始-re_deploy')
        self.re_deploy()
        log.info('重新部署链结束-re_deploy')

        log.info('等待一段时间={}秒'.format(self.time_interval))
        time.sleep(self.time_interval)

        rpc_link = self.link_1
        node_id = self.nodeid_list[0]
        option = 1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案，然后再进行投票
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 截止块高 生效块高 在第几个共识周期 共识周期最大边界
            block_list = get_all_legal_end_and_effect_block_number_for_vote(rpc_link, self.block_count,
                                                                            self.conse_index, self.conse_border)
            end_number = block_list[2][0]
            effect_number = block_list[2][1]

            # 发起升级提案
            self.submit_version(end_number, effect_number)
        else:
            log.info('有可投票的升级提案，直接进行投票')

        log.info('等待一段时间={}秒，再去获取提案信息'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        # 等待一定的块高，再投票
        is_cur_block_number_big_than_end_block_number(rpc_link, end_block_number)

        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option, programVersion=new_version)
        assert result.get('Status') == False, '发起升级投票交易时，不在投票周期，投票不成功'
        log.info('11-test_vote_notin_vote_cycle_c-对升级提案进行投票-是否在投票周期内的验证 conse_size * M- 20-结束')

    @allure.title('12-对升级提案进行投票-是否是验证人节点的验证（新节点发起投票）')
    def test_vote_new_node_vote(self):
        '''
        用例id 62
        对升级提案进行投票-是否是验证人节点的验证（新节点发起投票）
        '''
        rpc_link = self.link_1
        option = 1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 获取截止、生效块高
            end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link, self.block_count,self.conse_index)

            # 发起升级提案
            self.submit_version(end_number, effect_number)
        else:
            log.info('有可投票的升级提案，直接进行投票')

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        revice = rpc_link.getCandidateList()
        node_info = revice.get('Data')
        candidate_list = []

        for nodeid in node_info:
            candidate_list.append(nodeid.get('NodeId'))

        # 判断配置文件中的节点是否都已质押
        if set(self.nodeid_list2) < set(candidate_list):
            log.info('节点配置文件中的地址已全部质押，该用例执行失败')
        else:
            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    log.info('test_vote_new_node_vote-新用户节点进行投票')

                    result = rpc_link.vote(verifier=self.nodeid_list2[i], proposalID=proposal_id, option=option,programVersion=new_version)

                    log.info('新用户节点进行投票，投票失败')
                    info = result.get('ErrMsg')
                    assert result.get('Status') == False
                    assert info.find('not a verifier', 0,
                                     len(info)) > 0, '发起升级投票交易时，该节点是新人节点，而不是验证人节点，投票失败'
                    break
        log.info('12-test_vote_new_node_vote-对升级提案进行投票-是否是验证人节点的验证（新节点发起投票）-结束')

    @allure.title('13-对升级提案进行投票-是否是验证人节点的验证（候选人节点发起投票）')
    def test_vote_candidate_node_vote(self):
        '''
        用例id 62
        对升级提案进行投票-是否是验证人节点的验证（候选人节点发起投票）
        '''
        rpc_link = self.link_1
        option = 1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 获取截止、生效块高
            end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link, self.block_count,self.conse_index)

            # 发起升级提案
            self.submit_version(end_number, effect_number)
        else:
            log.info('有可投票的升级提案，直接进行投票')

        # 当前版本号
        cur_version = get_version()

        # 获取当前结算周期非验证人的候选人列表
        n_list = get_current_settle_account_candidate_list(rpc_link)

        # rpc_link = Ppos(self.rpc_list[2], self.address_list[0], chainid=101, privatekey=self.private_key_list[0])

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行升级提案，不存在就先进行质押
        if n_list:
            dv_nodeid = n_list[0]
            log.info('存在候选人节点，取第一个候选人节点={}'.format(dv_nodeid))
        else:
            # 获取候选人节点id列表
            revice = rpc_link.getCandidateList()
            node_info = revice.get('Data')
            candidate_list = []

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    result = rpc_link.createStaking(0, self.address_list[2], self.nodeid_list2[i],
                                                    externalId=self.external_id, nodeName=self.node_name,
                                                    website=self.website, details=self.details,
                                                    amount=self.staking_amount,
                                                    programVersion=cur_version, from_address=self.address_list[2],
                                                    gasPrice=self.base_gas_price, gas=self.staking_gas)
                    dv_nodeid = self.nodeid_list2[i]
                    log.info('不存在候选人节点，质押后的候选人节点={}'.format(dv_nodeid))
                    log.info('候选人节点质押成功')
                    assert result.get('Status') == True
                    assert result.get('ErrMsg') == 'ok'
                break

        log.info('候选人节点质押完成')

        log.info('test_vote_new_node_vote-候选人节点进行投票')

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        result = rpc_link.vote(verifier=dv_nodeid, proposalID=proposal_id, option=option,programVersion=new_version)

        log.info('候选人节点进行投票，投票失败')
        info = result.get('ErrMsg')
        assert result.get('Status') == False
        assert info.find('not a verifier', 0,
                         len(info)) > 0, '发起升级投票交易时，该节点是候选人节点，而不是验证人节点，投票失败'
        log.info('13-test_vote_candidate_node_vote-对升级提案进行投票-是否是验证人节点的验证（候选人节点发起投票）-结束')

    @allure.title('15-对升级提案进行投票-升级投票通过（验证人节点发起升级投票）')
    def test_vote_vote_success(self):
        '''
        用例id 64
        对升级提案进行投票-升级投票通过（验证人节点发起升级投票）
        '''
        rpc_link = self.link_1
        node_id=self.nodeid_list[0]
        option = 1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 获取截止、生效块高
            end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link, self.block_count,
                                                                                     self.conse_index)

            # 发起升级提案
            self.submit_version(end_number, effect_number)
        else:
            log.info('有可投票的升级提案，直接进行投票')

        # 在等待一定时间后，进行首次进行投票
        log.info('等待一段时间={}秒后，进行首次进行投票'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        # 进行投票操作
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=new_version)
        assert result.get('Status') == True, '对升级提案进行投票时，升级投票通过（验证人节点发起升级投票），投票成功'
        log.info('15-test_vote_vote_success-对升级提案进行投票-升级投票通过（验证人节点发起升级投票）-结束')

    @allure.title('16-对升级提案进行投票-是否已经投票过的验证')
    def test_vote_vote_double_cycle(self):
        '''
        用例id 59
        对升级提案进行投票-是否已经投票过的验证
        '''
        rpc_link = self.link_1
        node_id=self.nodeid_list[0]
        option = 1

        # 判断是否存在可投票的提案，没有则需要先发起一个升级提案
        flag = is_exist_ineffective_proposal_info_for_vote(rpc_link)

        # True 没有可投票的升级提案
        if not flag:
            log.info('没有可投票的升级提案，需先发起一个升级提案成功后，再投票')

            # 获取截止、生效块高
            end_number, effect_number = get_single_valid_end_and_effect_block_number(rpc_link, self.block_count,self.conse_index)

            # 发起升级提案
            self.submit_version(end_number, effect_number)
        else:
            log.info('有可投票的升级提案，直接进行投票')

        # 在等待一定时间后，进行首次进行投票
        log.info('等待一段时间={}秒后，进行首次进行投票'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        # 进行投票操作
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=new_version)
        assert result.get('Status') == True, '对升级提案进行投票时，升级投票通过（验证人节点发起升级投票），投票成功'

        # 在等待一定时间后，再次进行投票
        log.info('等待一段时间={}秒后，再次进行投票'.format(self.time_interval))
        time.sleep(self.time_interval)

        # 提案ID，升级版本号，截止块高
        proposal_id, new_version, end_block_number = get_effect_proposal_info_for_vote(rpc_link)

        # 进行投票操作
        result = rpc_link.vote(verifier=node_id, proposalID=proposal_id, option=option,programVersion=new_version)
        assert result.get('Status') == False, '对升级提案进行投票时，是否已经投票过的验证，已经进行投票后，不能再次重复投票，投票失败'
        log.info('16-test_vote_vote_double_cycle-对升级提案进行投票-是否已经投票过的验证，已经进行投票后，不能再次重复投票-结束')



    @allure.title('9-非质押钱包进行版本声明')
    def test_declare_version_nostaking_address(self):
        '''
        版本声明-非质押钱包进行版本声明
        '''
        rpc_link = self.no_link_2

        # 版本号
        cur_version = get_version(rpc_link)
        log.info('当前版本号为：{}'.format(cur_version))

        result = rpc_link.declareVersion(self.nodeid_list[0], cur_version, self.address_list[1])
        assert result.get('Status') == False
        assert result.get('ErrMsg') == "Declare version error:tx sender should be node's staking address."

    @allure.title('10-无有效的升级提案，新节点进行版本声明')
    def test_declare_version_noproposal_newnode(self):
        '''
        版本声明-无有效的升级提案，新节点进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        new_version0 = get_version(rpc_link)
        new_version1 = get_version(rpc_link, flag=1)
        new_version2 = get_version(rpc_link, flag=2)
        new_version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            log.info('当前链上存在生效的升级提案，该用例执行失败')
        else:
            revice = rpc_link.getCandidateList()
            node_info = revice.get('Data')
            candidate_list = []

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            # 判断配置文件中的节点是否都已质押
            if set(self.nodeid_list2) < set(candidate_list):
                log.info('节点配置文件中的地址已全部质押，该用例执行失败')
            else:
                for i in range(0, len(self.nodeid_list2)):
                    if self.nodeid_list2[i] not in candidate_list:

                        for version in version_list:
                            result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                             Web3.toChecksumAddress(self.address_list[1]))
                            assert result.get('Status') == False
                        break

    @allure.title('11-存在有效的升级提案，新节点进行版本声明')
    def test_declare_version_hasproposal_newnode(self):
        '''
        版本声明-存在有效的升级提案，新节点进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        new_version0 = get_version(rpc_link)
        new_version1 = get_version(rpc_link, flag=1)
        new_version2 = get_version(rpc_link, flag=2)
        new_version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        # 判断当前链上是否存在有效的升级提案
        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list == 'null':
            log.info('当前链上不存在生效的升级提案，进行发布升级提案')
            self.submit_version()

        # 获取候选人的节点id
        revice = rpc_link.getCandidateList()
        node_info = revice.get('Data')
        candidate_list = []

        for nodeid in node_info:
            candidate_list.append(nodeid.get('NodeId'))

        if (set(self.nodeid_list2) < set(candidate_list)):
            log.info('节点配置文件中的地址已全部质押,用例执行失败')
        else:
            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    for version in version_list:
                        result = rpc_link.declareVersion(self.nodeid_list2[i], version,
                                                         Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == False

                    break

    @allure.title('12-不存在有效的升级提案，候选节点进行版本声明')
    def test_declare_version_noproposal_Candidate(self):
        '''
        版本声明-不存在有效的升级提案，候选节点进行版本声明
        '''

        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        new_version0 = get_version(rpc_link)
        new_version1 = get_version(rpc_link, flag=1)
        new_version2 = get_version(rpc_link, flag=2)
        new_version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]
        n_list = get_current_settle_account_candidate_list(rpc_link)

        # 判断是否存在候选人节点(非验证人)，存在则直接用该节点进行版本声明，不存在就先进行质押
        if n_list:
            dv_nodeid = n_list[0]
        else:
            # 获取候选人节点id列表
            revice = rpc_link.getCandidateList()
            node_info = revice.get('Data')
            candidate_list = []

            for nodeid in node_info:
                candidate_list.append(nodeid.get('NodeId'))

            for i in range(0, len(self.nodeid_list2)):
                if self.nodeid_list2[i] not in candidate_list:
                    result = rpc_link.createStaking(0, self.address_list[0], self.nodeid_list2[i],
                                                    externalId=self.external_id,
                                                    nodeName=self.node_name,
                                                    website=self.website, details=self.details,
                                                    amount=self.staking_amount,
                                                    programVersion=new_version0, gasPrice=self.base_gas_price,
                                                    gas=self.staking_gas)
                    dv_nodeid = self.nodeid_list2[i]
                    assert result.get('Status') == True
                    assert result.get('ErrMsg') == 'ok'
                    break

        for version in version_list:
            if version == version_list[0]:
                result = rpc_link.declareVersion(dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                assert result.get('Status') == True
            else:
                result = rpc_link.declareVersion(dv_nodeid, version, Web3.toChecksumAddress(self.address_list[1]))
                assert result.get('Status') == False

    @allure.title('13-存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_propsal_verifier(self):
        '''
        版本声明-存在有效的升级提案，验证人进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        new_version0 = get_version(rpc_link)
        new_version1 = get_version(rpc_link, flag=1)
        new_version2 = get_version(rpc_link, flag=2)
        new_version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list == 'null':
            self.submit_version()

        # 获取验证人id列表
        revice = rpc_link.getVerifierList()
        node_info = revice.get('Data')
        verifier_list = []

        dv_nodeid = False
        for nodeid in node_info:
            verifier_list.append(nodeid.get('NodeId'))

        for i in range(0, len(verifier_list)):
            if verifier_list[i] not in self.nodeid_list:
                dv_nodeid = verifier_list[i]
                break

        if not dv_nodeid:
            log.info('当前结算周期不存在可用验证人（非创始验证人节点），该用例验证失败')
        else:
            for version in version_list:
                if version == version_list[1]:
                    result = rpc_link.declareVersion(dv_nodeid, version,
                                                     Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == False
                else:
                    result = rpc_link.declareVersion(dv_nodeid, version,
                                                     Web3.toChecksumAddress(self.address_list[1]))
                    assert result.get('Status') == True

    @allure.title('14-不存在有效的升级提案，验证人进行版本声明')
    def test_declare_version_nopropsal_verifier(self):
        '''
        版本声明-不存在有效的升级提案，验证人进行版本声明
        '''
        rpc_link = Ppos(self.rpc_list[2], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        # 升级版本号
        new_version0 = get_version(rpc_link)
        new_version1 = get_version(rpc_link, flag=1)
        new_version2 = get_version(rpc_link, flag=2)
        new_version3 = get_version(rpc_link, flag=3)

        log.info('当前生成的小版本号为：{}-当前版本号为：{}-大于当前的版本号：{}-大版本号为：{}-'.format(new_version0, new_version1, new_version2,
                                                                        new_version3))

        # 版本号参数列表
        version_list = [new_version0, new_version1, new_version2, new_version3]

        proposal_info = rpc_link.listProposal()
        proposal_list = proposal_info.get('Data')

        if proposal_list != 'null':
            log.info('存在有效的升级提案，该用例执行失败')
        else:
            revice = rpc_link.getVerifierList()
            node_info = revice.get('Data')
            verifier_list = []
            dv_nodeid = False

            for nodeid in node_info:
                verifier_list.append(nodeid.get('NodeId'))

            for i in range(0, len(verifier_list)):
                if verifier_list[i] not in self.nodeid_list:
                    dv_nodeid = verifier_list[i]
                    break

            # 判断是否存在验证
            if dv_nodeid:
                for version in version_list:
                    if version == version_list[0] or version == version_list[1]:
                        result = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                         Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == True
                    else:
                        result = rpc_link.declareVersion(self.nodeid_list2[2], version,
                                                         Web3.toChecksumAddress(self.address_list[1]))
                        assert result.get('Status') == False

            else:
                log.info('当前结算周期不存在可用验证人（非创始验证人节点），该用例验证失败')

    @allure.title('20-查询节点链生效的版本')
    def test_get_active_version(self):
        '''
        查询节点链生效的版本
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])
        log.info('查询节点链生效的版本-test_get_active_version-={}'.format(rpc_link.getActiveVersion()))

    @allure.title('21-查询提案列表')
    def test_get_proposal_list(self):
        '''
        查询提案列表
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        result = rpc_link.listProposal(self.private_key_list[1], self.address_list[1], gasPrice=60000000000000,gas=101000)

        log.info('查询提案列表-test_get_proposal_list-={}'.format(result))

    @allure.title('22-查询节点列表')
    def test_get_node_list(self):
        '''
        查询节点列表
        :return:
        '''
        rpc_link = Ppos(self.rpc_list[3], self.address_list[1], chainid=101, privatekey=self.private_key_list[1])

        gas2 = self.base_gas + 6000 + 32000 + 12000

        gas_price2 = self.base_gas_price

        result = rpc_link.getTallyResult('111', self.address_list[1], gas_price2, gas2)

        log.info('查询节点列-test_get_node_list-={}'.format(result))


if  __name__ == '__main__':
    pytest.main(["-s", "test_govern.py"])
