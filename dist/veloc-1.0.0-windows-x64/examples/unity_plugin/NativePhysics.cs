// Auto-generated VeloC C# / Unity P/Invoke Interop Layer
using System;
using System.Runtime.InteropServices;

namespace VeloC.Interop
{
    public static class NativePhysics
    {
        private const string LibraryName = "veloc_physics";

        [DllImport(LibraryName, EntryPoint = "veloc_physics_init", CallingConvention = CallingConvention.Cdecl)]
        public static extern void veloc_physics_init();

        [DllImport(LibraryName, EntryPoint = "veloc_simulate_step", CallingConvention = CallingConvention.Cdecl)]
        public static extern int veloc_simulate_step(float dt, int entity_count);

        [DllImport(LibraryName, EntryPoint = "veloc_get_energy", CallingConvention = CallingConvention.Cdecl)]
        public static extern float veloc_get_energy();

    }
}