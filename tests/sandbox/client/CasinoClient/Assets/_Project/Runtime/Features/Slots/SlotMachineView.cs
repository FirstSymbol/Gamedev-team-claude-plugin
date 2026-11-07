using UnityEngine;
namespace Game.Slots
{
    public sealed class SlotMachineView : MonoBehaviour
    {
        [SerializeField] private Transform[] reels;
        public void ShowResult(int[] symbols) { /* animate reels */ }
    }
}
