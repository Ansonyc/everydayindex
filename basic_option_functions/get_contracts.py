
# 定义枚举ATM,OTM,ITM
class OptionType:
    ATM = 0
    OTM = 1
    ITM = 2

def pre_process_contracts(target_contracts):
    # 有A合约和正常价格合约的情况下，剔除带A的合约
    contracts_contain_A = target_contracts[target_contracts['security_name'].str.contains('A')]
    if len(target_contracts) != len(contracts_contain_A):
        target_contracts = target_contracts[~target_contracts['security_name'].str.contains('A')]
    
    # 去掉末尾的A字符后取最后4位数字
    target_contracts['price'] = target_contracts['security_name'].str.replace('A$', '', regex=True).str[-4:].astype(int) * 10
    
    return target_contracts

def get_contract(same_month_options, close_price, is_call=True, optionType = OptionType.ATM, level=0):
    same_month_options = pre_process_contracts(same_month_options)
    same_month_options['abs_price_diff'] = abs(same_month_options['price'] - close_price)
    if is_call:
        same_month_options = same_month_options[same_month_options['security_name'].str.contains('购')]
        atm_contract = same_month_options.nsmallest(1, 'abs_price_diff')
        if optionType == OptionType.ATM:
            return atm_contract.iloc[-1]

        # 修改这里的判断逻辑
        atm_code = atm_contract.iloc[0]['security_code']
        same_month_options = same_month_options[same_month_options['security_code'] != atm_code]

        if optionType == OptionType.OTM:
            same_month_options = same_month_options[same_month_options['price'] > close_price]
        elif optionType == OptionType.ITM:
            same_month_options = same_month_options[same_month_options['price'] < close_price]
        else:
            raise Exception("Invalid optionType")
        same_month_options['price_diff'] = abs(same_month_options['price'] - close_price)

        contract = same_month_options.nsmallest(level, 'price_diff')
        
        if len(contract) > 0:
            return contract.iloc[-1]
        else:
            return None
    else:
        same_month_options = same_month_options[same_month_options['security_name'].str.contains('沽')]
        atm_contract = same_month_options.nsmallest(1, 'abs_price_diff')
        if optionType == OptionType.ATM:
            return atm_contract.iloc[-1]

        # 修改这里的判断逻辑
        atm_code = atm_contract.iloc[0]['security_code']
        same_month_options = same_month_options[same_month_options['security_code'] != atm_code]

        if optionType == OptionType.OTM:
            same_month_options = same_month_options[same_month_options['price'] < close_price]
        elif optionType == OptionType.ITM:
            same_month_options = same_month_options[same_month_options['price'] > close_price]
        else:
            raise Exception("Invalid optionType")
        same_month_options['price_diff'] = abs(same_month_options['price'] - close_price)

        contract = same_month_options.nsmallest(level, 'price_diff')
        if len(contract) > 0:
            return contract.iloc[-1]
        else:
            return None
