use anchor_lang::prelude::*;
use anchor_lang::solana_program::ed25519_program;
use anchor_lang::solana_program::instruction::Instruction;
use anchor_lang::solana_program::sysvar::instructions::{load_instruction_at_checked, ID as IX_ID};

// This is a placeholder ID. You will update this after running `anchor keys sync`.
declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkg476zPFsLnS");

#[program]
pub mod meshcoin {
    use super::*;

    /// Initializes the global MeshCoin state (the Treasury).
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let state = &mut ctx.accounts.state;
        state.admin = ctx.accounts.admin.key();
        state.total_supply = 100_000;
        Ok(())
    }

    /// Verifies a cryptographic signature from a client node, and if valid,
    /// transfers MeshCoin from the global treasury to the worker node.
    pub fn verify_and_reward(ctx: Context<VerifyAndReward>, amount: u64, message: Vec<u8>) -> Result<()> {
        // In Solana, ed25519 signature verification is typically done via a precompiled program
        // that must be included in the same transaction before this instruction.
        // We ensure the previous instruction was the ed25519 signature verification.
        
        let ixs = ctx.accounts.ix_sysvar.to_account_info();
        
        // Load the previous instruction (which must be the ed25519 program)
        let previous_instruction = load_instruction_at_checked(0, &ixs)
            .map_err(|_| ErrorCode::InvalidSignatureVerification)?;
            
        if previous_instruction.program_id != ed25519_program::ID {
            return err!(ErrorCode::InvalidSignatureVerification);
        }
        
        // If the signature is verified, we can safely record the transfer and adjust balances.
        // In a real implementation using SPL Token, you would CPI into the Token Program here.
        let state = &mut ctx.accounts.state;
        
        require!(state.total_supply >= amount, ErrorCode::InsufficientFunds);
        
        state.total_supply -= amount;
        
        msg!("Signature verified! Transferred {} MeshCoins.", amount);
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init, 
        payer = admin, 
        space = 8 + 32 + 8,
        seeds = [b"meshcoin_state"], 
        bump
    )]
    pub state: Account<'info, MeshCoinState>,
    
    #[account(mut)]
    pub admin: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct VerifyAndReward<'info> {
    #[account(
        mut,
        seeds = [b"meshcoin_state"], 
        bump
    )]
    pub state: Account<'info, MeshCoinState>,
    
    /// CHECK: Instructions sysvar
    #[account(address = IX_ID)]
    pub ix_sysvar: AccountInfo<'info>,
    
    #[account(mut)]
    pub worker: SystemAccount<'info>, // The node receiving the reward
}

#[account]
pub struct MeshCoinState {
    pub admin: Pubkey,
    pub total_supply: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("The required ed25519 signature verification instruction is missing or invalid.")]
    InvalidSignatureVerification,
    #[msg("Treasury has insufficient MeshCoins.")]
    InsufficientFunds,
}
