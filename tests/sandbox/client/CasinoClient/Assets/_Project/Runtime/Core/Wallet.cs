using System;
namespace Game.Core
{
    /// <summary>Client-side cached view of the server wallet. Server is authoritative.</summary>
    public sealed class Wallet
    {
        public long Coins { get; private set; }
        public event Action<long> Changed;
        public void ApplyServerBalance(long coins) { Coins = coins; Changed?.Invoke(Coins); }
    }
}
