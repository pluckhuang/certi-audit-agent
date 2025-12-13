// target_contracts/solana/src/lib.rs
use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod vulnerable_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let config = &mut ctx.accounts.config;
        config.admin = ctx.accounts.signer.key();
        Ok(())
    }

    // 🚨 漏洞函数：缺失 Signer Check
    // 意图：只有当前的 admin 才能把 admin 权限转给别人
    // 现实：代码里只检查了传入的 old_admin 账号数据是否匹配，但没检查 old_admin 是否"签字"同意了
    pub fn update_admin(ctx: Context<UpdateAdmin>, new_admin: Pubkey) -> Result<()> {
        let config = &mut ctx.accounts.config;

        // 这里的逻辑看似在检查，其实只是数据比对
        if config.admin != ctx.accounts.old_admin.key() {
             return Err(ErrorCode::InvalidAdmin.into());
        }

        // 💀 致命错误：没有检查 ctx.accounts.old_admin.is_signer
        // 攻击者可以传入真正的 admin 的公钥作为 'old_admin' 参数，
        // 只要不要求 admin 签名，攻击者就能通过这个检查，把 admin 改成自己！
        
        config.admin = new_admin;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = signer, space = 8 + 32)]
    pub config: Account<'info, Config>,
    #[account(mut)]
    pub signer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateAdmin<'info> {
    #[account(mut)]
    pub config: Account<'info, Config>,
    
    /// CHECK: 这是一个不安全的代码演示，我们故意用 AccountInfo 而不是 Signer
    pub old_admin: AccountInfo<'info>, 
}

#[account]
pub struct Config {
    pub admin: Pubkey,
}

#[error_code]
pub enum ErrorCode {
    #[msg("Invalid admin account provided.")]
    InvalidAdmin,
}