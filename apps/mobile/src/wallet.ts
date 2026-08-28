import { Keypair, Connection, clusterApiUrl, PublicKey } from '@solana/web3.js';
import 'react-native-get-random-values';

export class MeshCoinWallet {
    private keypair: Keypair;
    private connection: Connection;

    constructor() {
        this.keypair = Keypair.generate();
        this.connection = new Connection(clusterApiUrl('devnet'), 'confirmed');
    }

    public getPublicKey(): string {
        return this.keypair.publicKey.toString();
    }

    public async getBalance(): Promise<number> {
        return await this.connection.getBalance(this.keypair.publicKey);
    }
}
