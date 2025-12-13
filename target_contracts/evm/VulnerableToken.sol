// VulnerableToken.sol
pragma solidity ^0.8.0;

contract VulnerableToken {
    mapping (address => uint256) public balances;

    constructor() payable {
        balances[msg.sender] = 1000 ether; // 初始余额
    }

    // 充值函数
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // 提现函数：包含重入漏洞
    function withdraw(uint256 _amount) public {
        // 1. 检查
        require(balances[msg.sender] >= _amount, "Insufficient balance");

        // 2. 交互 (外部调用) - 关键的漏洞点
        (bool success, ) = msg.sender.call{value: _amount}(""); 
        require(success, "Withdrawal failed");

        // 3. 影响 (状态更新) - 发生在外部调用之后
        balances[msg.sender] -= _amount; 
    }

    function getBalance() public view returns (uint256) {
        return balances[msg.sender];
    }
}