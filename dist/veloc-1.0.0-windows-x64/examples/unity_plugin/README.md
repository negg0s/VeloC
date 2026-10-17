# VeloC Native Plugin for Unity & .NET

This directory contains a complete native C# P/Invoke integration for Unity.

## How to use in Unity:
1. Compile your VeloC kernel into a 64-bit DLL:
   ```bash
   python veloc.py build src/physics.vc -o veloc_physics.dll --fp=fast -O3
   ```
2. Place `veloc_physics.dll` into your Unity project at:
   `Assets/Plugins/x86_64/veloc_physics.dll`
3. Attach `NativePhysics.cs` to your game objects.
4. Call `NativePhysics.veloc_simulate_step(Time.deltaTime, count)` inside your `Update()` loop with zero GC allocations!
